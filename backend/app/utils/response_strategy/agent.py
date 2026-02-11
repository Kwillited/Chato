"""智能体处理工具类"""
import json
from app.services.base_service import BaseService
from app.utils.response_strategy.stream import StreamUtils


class AgentProcessor:
    """智能体处理工具类，用于处理智能体相关的响应"""
    
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
                    formatted_chunk = StreamUtils.format_stream_chunk(chunk_data.get('chunk', chunk_data.get('content', str(chunk))), agent=True)
                    # 累积完整回复
                    if 'chunk' in chunk_data:
                        full_reply += chunk_data['chunk']
                    elif 'content' in chunk_data:
                        full_reply += chunk_data['content']
                    return formatted_chunk, full_reply
                except:
                    # 如果不是JSON格式，直接作为内容包装
                    formatted_chunk = StreamUtils.format_stream_chunk(chunk, agent=True)
                    full_reply += chunk
                    return formatted_chunk, full_reply
        except Exception as e:
            BaseService.log_error(f"处理智能体事件流响应块失败: {e}")
            # 尝试作为直接内容处理
            full_reply += str(chunk)
            formatted_chunk = StreamUtils.format_stream_chunk(str(chunk), agent=True)
            return formatted_chunk, full_reply
    
    @staticmethod
    def format_agent_message(message, now, model_display_name, session_id=None, node=None, step=None, full_reasoning=None):
        """格式化智能体消息

        Args:
            message: 智能体消息内容
            now: 当前时间戳
            model_display_name: 模型显示名称
            session_id: 智能体会话ID
            node: 智能体节点名称
            step: 智能体步骤
            full_reasoning: 累积的思考内容

        Returns:
            格式化后的智能体消息
        """
        from app.utils.message_handler import MessageHandler
        
        # 创建基础AI消息
        ai_message = MessageHandler.Response.process_full_reply(message, now, model_display_name, full_reasoning)
        
        # 添加智能体相关字段
        ai_message['message_type'] = 'agent'
        if session_id:
            ai_message['agent_session_id'] = session_id
        if node:
            ai_message['agent_node'] = node
        if step is not None:
            ai_message['agent_step'] = step
        
        return ai_message