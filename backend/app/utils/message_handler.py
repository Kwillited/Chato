"""统一消息处理器，处理消息的输入和输出"""
from typing import List, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
import json
import uuid
import re
from app.core.logging_config import logger
from app.services.base_service import BaseService


class MessageHandler:
    """统一消息处理器，处理消息的输入和输出"""
    
    # 输入处理器（Request）
    class Request:
        """输入处理器，处理用户输入到模型的转换"""
        
        @staticmethod
        def convert_to_langchain_messages(messages: List[Dict[str, str]]) -> List[BaseMessage]:
            """将内部消息格式转换为langchain消息格式
            
            Args:
                messages: 内部消息格式列表
                
            Returns:
                List[BaseMessage]: langchain消息格式列表
            """
            langchain_messages = []
            for msg in messages:
                role = msg['role'].lower()
                content = msg['content']
                
                if role == 'system':
                    langchain_messages.append(SystemMessage(content=content))
                elif role == 'user':
                    langchain_messages.append(HumanMessage(content=content))
                elif role == 'assistant':
                    langchain_messages.append(AIMessage(content=content))
                else:
                    langchain_messages.append(HumanMessage(content=content))
            
            return langchain_messages
        
        @staticmethod
        def extract_latest_input(messages: List[Dict[str, str]]) -> tuple:
            """从消息列表中提取最新输入和历史消息
            
            Args:
                messages: 消息列表
                
            Returns:
                tuple: (latest_input, chat_history)
            """
            if messages and isinstance(messages[-1], dict) and "content" in messages[-1]:
                latest_input = messages[-1]["content"]
                chat_history = messages[:-1]
                return latest_input, chat_history
            return "", []
        
        @staticmethod
        def process_think_tags(content: str) -> tuple:
            """处理内容中的Think标签，提取思考内容并移除标签
            
            Args:
                content: 包含思考标签的内容
                
            Returns:
                tuple: (thinking_content, actual_content)
            """
            # 支持两种标签格式
            think_patterns = [
                re.compile(r'\s*<think>([\s\S]*?)</think>\s*', re.IGNORECASE),
                re.compile(r'\s*\[think\]([\s\S]*?)\[/think\]\s*', re.IGNORECASE)
            ]
            
            thinking_content = None
            actual_content = content
            
            for pattern in think_patterns:
                match = pattern.match(content)
                if match:
                    thinking_content = match.group(1)
                    actual_content = pattern.sub('', content).strip()
                    break
            
            return thinking_content, actual_content
        
        @staticmethod
        def filter_think_tags(content: str) -> str:
            """过滤内容中的think标签
            
            Args:
                content: 原始内容
                
            Returns:
                过滤后的内容
            """
            # 使用统一的process_think_tags方法
            _, filtered_content = MessageHandler.Request.process_think_tags(content)
            return filtered_content
    
    # 输出处理器（Response）
    class Response:
        """输出处理器，处理模型响应到用户的转换"""
        
        @staticmethod
        def create_ai_message(now, content, model_display_name, files=None):
            """创建标准格式的AI回复消息
            
            Args:
                now: 当前时间戳
                content: 回复内容
                model_display_name: 模型显示名称
                files: 相关文件列表
                
            Returns:
                标准格式的AI回复消息
            """
            ai_message_id = str(uuid.uuid4())
            ai_message = {
                'id': ai_message_id,
                'role': 'assistant',
                'content': content,
                'createdAt': now,
                'model': model_display_name,
                'files': files or []  # 添加files字段，默认空列表
            }
            logger.debug(f"创建AI消息: id={ai_message_id}, model={model_display_name}, content_length={len(content)}")
            return ai_message
        
        @staticmethod
        def process_full_reply(full_reply, now, model_display_name, full_reasoning=None):
            """处理完整回复，分离思考内容和实际内容
            
            Args:
                full_reply: 完整的回复内容
                now: 当前时间戳
                model_display_name: 模型显示名称
                full_reasoning: 累积的思考内容
                
            Returns:
                标准格式的AI回复消息
            """
            # 如果提供了full_reasoning，直接使用它
            if full_reasoning:
                thinking_content = full_reasoning
                actual_content = full_reply
            else:
                # 否则从full_reply中提取思考内容
                thinking_content, actual_content = MessageHandler.Request.process_think_tags(full_reply)
            
            # 创建AI回复，确保包含完整的模型和版本信息
            ai_message = MessageHandler.Response.create_ai_message(now, actual_content, model_display_name)
            # 添加思考内容到AI消息
            ai_message['reasoning_content'] = thinking_content
            
            return ai_message
        
        @staticmethod
        def process_streaming_chunk(chunk, full_reply):
            """处理单个流式响应块

            Args:
                chunk: 流式响应块
                full_reply: 当前累积的完整回复

            Returns:
                (formatted_chunk, updated_full_reply): 格式化后的响应块和更新后的完整回复
            """
            # 检查是否是错误消息格式
            if isinstance(chunk, str) and chunk.startswith('data: {"error"'):
                return chunk, full_reply
            
            # 尝试解析chunk数据
            try:
                # 如果chunk已经是格式化的字符串，直接处理
                if isinstance(chunk, str) and chunk.startswith('data: '):
                    chunk_str = chunk[6:].strip()
                    chunk_data = json.loads(chunk_str)
                    
                    if 'chunk' in chunk_data:
                        actual_chunk = chunk_data['chunk']
                        full_reply += actual_chunk
                        return chunk, full_reply  # 直接传递格式化的chunk
                    elif 'error' in chunk_data:
                        return chunk, full_reply  # 直接传递错误信息
                    else:
                        # 如果chunk_data中既没有chunk也没有error，直接返回原chunk
                        return chunk, full_reply
                else:
                    # 假设chunk是直接的内容块
                    full_reply += chunk
                    response_data = {
                        'chunk': chunk,
                        'done': False
                    }
                    formatted_chunk = f'data: {json.dumps(response_data, ensure_ascii=False)}\n\n'
                    return formatted_chunk, full_reply
            except Exception as e:
                BaseService.log_error(f"处理流式响应块失败: {e}")
                # 尝试作为直接内容处理
                full_reply += str(chunk)
                response_data = {
                    'chunk': str(chunk),
                    'done': False
                }
                formatted_chunk = f'data: {json.dumps(response_data, ensure_ascii=False)}\n\n'
                return formatted_chunk, full_reply
        
        @staticmethod
        def process_agent_stream_chunk(chunk, full_reply):
            """处理智能体事件流响应块

            Args:
                chunk: 智能体事件流响应块
                full_reply: 当前累积的完整回复

            Returns:
                (formatted_chunk, updated_full_reply): 格式化后的响应块和更新后的完整回复
            """
            try:
                # 检查是否已经是SSE格式
                if isinstance(chunk, str) and chunk.startswith('data: '):
                    chunk_str = chunk[6:].strip()
                    try:
                        chunk_data = json.loads(chunk_str)
                        # 检查是否是智能体响应
                        if chunk_data.get('agent', False):
                            # 累积完整回复
                            if 'chunk' in chunk_data:
                                full_reply += chunk_data['chunk']
                            elif 'content' in chunk_data:
                                full_reply += chunk_data['content']
                        return chunk, full_reply
                    except:
                        # 如果解析失败，直接返回原chunk
                        return chunk, full_reply
                else:
                    # 如果不是SSE格式，包装成SSE格式
                    try:
                        # 尝试解析chunk，看是否是JSON格式
                        chunk_data = json.loads(chunk)
                        # 添加agent标记
                        chunk_data['agent'] = True
                        # 包装成SSE格式
                        formatted_chunk = f'data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n'
                        # 累积完整回复
                        if 'chunk' in chunk_data:
                            full_reply += chunk_data['chunk']
                        elif 'content' in chunk_data:
                            full_reply += chunk_data['content']
                        return formatted_chunk, full_reply
                    except:
                        # 如果不是JSON格式，直接作为内容包装
                        content_data = {
                            'chunk': chunk,
                            'agent': True
                        }
                        formatted_chunk = f'data: {json.dumps(content_data, ensure_ascii=False)}\n\n'
                        full_reply += chunk
                        return formatted_chunk, full_reply
            except Exception as e:
                BaseService.log_error(f"处理智能体事件流响应块失败: {e}")
                # 尝试作为直接内容处理
                full_reply += str(chunk)
                content_data = {
                    'chunk': str(chunk),
                    'agent': True
                }
                formatted_chunk = f'data: {json.dumps(content_data, ensure_ascii=False)}\n\n'
                return formatted_chunk, full_reply