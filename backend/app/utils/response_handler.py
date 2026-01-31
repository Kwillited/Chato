"""响应处理器工具类"""
import json
from typing import Dict, Any, Generator

from app.utils.response_formatter import ResponseFormatter
from app.services.base_service import BaseService


class ResponseHandler:
    """响应处理器，处理不同类型的响应"""
    
    @staticmethod
    def handle_regular_response(chat, message_text, user_message, now,
                               enhanced_question, parsed_model_name, parsed_version_name, 
                               model_params, model_display_name, deep_thinking=False, use_agent=False,
                               chat_service=None):
        """处理普通响应"""
        try:
            # 使用通用验证函数验证模型
            model, error_response, error_code = chat_service.validate_model(parsed_model_name)
            if error_response:
                return error_response, error_code

            # 准备消息格式
            messages = chat_service._prepare_messages_for_model(chat['id'], enhanced_question, deep_thinking)
            
            # 获取temperature参数
            temperature = model_params.get('temperature', 0.7)
            
            # 获取版本配置
            version_id = parsed_version_name
            version_config = chat_service.get_version_config(model, version_id)

            if use_agent:
                # 使用智能体模式
                chat_service.log_info("使用智能体模式，直接返回原始响应")
                
                from app.models.model_manager import ModelManager
                from app.models.agent_wrapper import AgentWrapper
                import asyncio
                
                # 获取基础模型驱动
                base_driver = ModelManager.get_model_driver(parsed_model_name, model, version_config)
                
                # 创建智能体包装器
                agent_wrapper = AgentWrapper(base_driver)
                
                # 初始化智能体
                asyncio.run(agent_wrapper.initialize())
                
                # 调用智能体聊天方法
                response = asyncio.run(agent_wrapper.chat(messages, temperature, stream=False, use_agent=True))
                
                # 处理智能体响应
                ai_reply = ""
                if isinstance(response, dict):
                    ai_reply = response.get('content', '') or response.get('output', '') or response.get('answer', '')
                elif isinstance(response, str):
                    ai_reply = response
                else:
                    ai_reply = str(response)
                
                # 使用已有的方法处理完整回复
                ai_message = ResponseFormatter.process_full_reply(ai_reply, now, model_display_name)
                
                # 更新对话并保存
                chat_service.update_chat_and_save(chat, message_text, user_message, ai_message, now)
                
                # 返回智能体响应，添加agent标记
                return {
                    'success': True,
                    'agent': True,
                    'chat': chat,
                    'user_message': user_message,
                    'ai_message': ai_message,
                    'raw_response': response  # 添加原始响应
                }, 201
            else:
                # 使用普通模式
                chat_service.log_info("使用普通对话模式，统一格式化响应")
                
                from app.models.model_manager import ModelManager
                response = ModelManager.chat(parsed_model_name, model, version_config, messages, temperature)
            
            # 获取模型回复内容 - 处理不同返回格式
            if isinstance(response, dict) and 'content' in response:
                ai_reply = response['content']
            else:
                # 直接返回字符串的情况
                ai_reply = response
        except Exception as e:
            # 捕获所有异常并返回错误信息
            BaseService.log_error(f'调用模型失败: {str(e)}')
            return {'error': f'调用模型失败: {str(e)}'}, 500
        
        # 使用已有的方法处理完整回复
        ai_message = ResponseFormatter.process_full_reply(ai_reply, now, model_display_name)
        
        # 更新对话并保存
        chat_service.update_chat_and_save(chat, message_text, user_message, ai_message, now)
        
        return {
            'success': True,
            'chat': chat,
            'user_message': user_message,
            'ai_message': ai_message
        }, 201
    
    @staticmethod
    def handle_streaming_response(chat, message_text, user_message, now,
                                 enhanced_question, parsed_model_name, parsed_version_name, 
                                 model_params, model_display_name, deep_thinking=False, use_agent=False,
                                 chat_service=None):
        """处理流式响应"""
        def generate():
            try:
                # 准备消息格式
                messages = chat_service._prepare_messages_for_model(chat['id'], enhanced_question, deep_thinking)
                
                # 获取temperature参数
                temperature = model_params.get('temperature', 0.7)
                
                if use_agent:
                    # 智能体模式：使用特殊格式返回
                    chat_service.log_info("使用智能体模式，返回特殊格式响应")
                    
                    # 初始化完整回复
                    full_reply = ""
                    
                    # 使用流式模型回复函数获取响应
                    for chunk in chat_service.chat_with_model_stream(parsed_model_name, messages, parsed_version_name, temperature, use_agent):
                        # 确保chunk是字符串格式
                        if isinstance(chunk, str):
                            # 检查是否已经是SSE格式
                            if not chunk.startswith('data: '):
                                # 如果不是SSE格式，包装成SSE格式
                                try:
                                    # 尝试解析chunk，看是否是JSON格式
                                    chunk_data = json.loads(chunk)
                                    # 包装成SSE格式
                                    formatted_chunk = f'data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n'
                                    yield formatted_chunk
                                    # 累积完整回复
                                    if 'chunk' in chunk_data:
                                        full_reply += chunk_data['chunk']
                                    elif 'content' in chunk_data:
                                        full_reply += chunk_data['content']
                                except:
                                    # 如果不是JSON格式，直接作为内容包装
                                    content_data = {'chunk': chunk, 'agent': True}
                                    formatted_chunk = f'data: {json.dumps(content_data, ensure_ascii=False)}\n\n'
                                    yield formatted_chunk
                                    full_reply += chunk
                            else:
                                # 已经是SSE格式，直接返回
                                yield chunk
                                # 累积完整回复用于后续保存
                                chunk_str = chunk[6:].strip()
                                try:
                                    chunk_data = json.loads(chunk_str)
                                    if 'chunk' in chunk_data:
                                        full_reply += chunk_data['chunk']
                                    elif 'content' in chunk_data:
                                        full_reply += chunk_data['content']
                                except:
                                    pass
                        else:
                            # 如果不是字符串，转换为字符串并包装
                            chunk_str = str(chunk)
                            content_data = {'chunk': chunk_str, 'agent': True}
                            formatted_chunk = f'data: {json.dumps(content_data, ensure_ascii=False)}\n\n'
                            yield formatted_chunk
                            full_reply += chunk_str
                    
                    # 处理完整回复并保存
                    ai_message = ResponseFormatter.process_full_reply(full_reply, now, model_display_name)
                    chat_service.update_chat_and_save(chat, message_text, user_message, ai_message, now)
                    
                    # 发送智能体最终完成信号
                    final_data = {
                        'agent': True,
                        'done': True,
                        'chat': chat,
                        'user_message': user_message,
                        'ai_message': ai_message
                    }
                    yield f'data: {json.dumps(final_data, ensure_ascii=False)}\n\n'
                else:
                    # 普通对话模式：保持现有处理逻辑
                    chat_service.log_info("使用普通对话模式，统一格式化响应")
                    
                    # 初始化完整回复
                    full_reply = ""
                    
                    # 使用流式模型回复函数获取响应
                    for chunk in chat_service.chat_with_model_stream(parsed_model_name, messages, parsed_version_name, temperature, use_agent):
                        formatted_chunk, full_reply = ResponseFormatter.process_streaming_chunk(chunk, full_reply)
                        yield formatted_chunk
                    
                    # 处理完整回复
                    ai_message = ResponseFormatter.process_full_reply(full_reply, now, model_display_name)
                    
                    # 更新对话并保存
                    chat_service.update_chat_and_save(chat, message_text, user_message, ai_message, now)
                    
                    # 发送最终完成信号
                    final_data = {
                        'done': True,
                        'chat': chat,
                        'user_message': user_message,
                        'ai_message': ai_message
                    }
                    yield f'data: {json.dumps(final_data, ensure_ascii=False)}\n\n'
            except Exception as e:
                # 捕获所有异常并返回错误信息
                BaseService.log_error(f'流式处理失败: {str(e)}')
                response_data = {'error': str(e)}
                yield f'data: {json.dumps(response_data, ensure_ascii=False)}\n\n'
        
        return generate
    
    @staticmethod
    def handle_astream_response(chat, message_text, user_message, now,
                               enhanced_question, parsed_model_name, parsed_version_name, 
                               model_params, model_display_name, deep_thinking=False, use_agent=False,
                               chat_service=None):
        """处理astream响应"""
        def generate():
            try:
                # 准备消息格式
                messages = chat_service._prepare_messages_for_model(chat['id'], enhanced_question, deep_thinking)
                
                # 获取temperature参数
                temperature = model_params.get('temperature', 0.7)
                
                chat_service.log_info("使用astream模式，返回异步流式响应")
                
                # 初始化完整回复
                full_reply = ""
                
                # 使用流式模型回复函数获取响应
                for chunk in chat_service.chat_with_model_stream(parsed_model_name, messages, parsed_version_name, temperature, use_agent):
                    # 确保chunk是字符串格式
                    if isinstance(chunk, str):
                        # 检查是否已经是SSE格式
                        if not chunk.startswith('data: '):
                            # 如果不是SSE格式，包装成SSE格式
                            try:
                                # 尝试解析chunk，看是否是JSON格式
                                chunk_data = json.loads(chunk)
                                # 添加astream标记
                                chunk_data['astream'] = True
                                # 包装成SSE格式
                                formatted_chunk = f'data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n'
                                yield formatted_chunk
                                # 累积完整回复
                                if 'chunk' in chunk_data:
                                    full_reply += chunk_data['chunk']
                                elif 'content' in chunk_data:
                                    full_reply += chunk_data['content']
                            except:
                                # 如果不是JSON格式，直接作为内容包装
                                content_data = {'chunk': chunk, 'astream': True}
                                formatted_chunk = f'data: {json.dumps(content_data, ensure_ascii=False)}\n\n'
                                yield formatted_chunk
                                full_reply += chunk
                        else:
                            # 已经是SSE格式，直接返回
                            yield chunk
                            # 累积完整回复用于后续保存
                            chunk_str = chunk[6:].strip()
                            try:
                                chunk_data = json.loads(chunk_str)
                                # 添加astream标记
                                chunk_data['astream'] = True
                                if 'chunk' in chunk_data:
                                    full_reply += chunk_data['chunk']
                                elif 'content' in chunk_data:
                                    full_reply += chunk_data['content']
                            except:
                                pass
                    else:
                        # 如果不是字符串，转换为字符串并包装
                        chunk_str = str(chunk)
                        content_data = {'chunk': chunk_str, 'astream': True}
                        formatted_chunk = f'data: {json.dumps(content_data, ensure_ascii=False)}\n\n'
                        yield formatted_chunk
                        full_reply += chunk_str
                
                # 处理完整回复并保存
                ai_message = ResponseFormatter.process_full_reply(full_reply, now, model_display_name)
                chat_service.update_chat_and_save(chat, message_text, user_message, ai_message, now)
                
                # 发送astream最终完成信号
                final_data = {
                    'astream': True,
                    'done': True,
                    'chat': chat,
                    'user_message': user_message,
                    'ai_message': ai_message
                }
                yield f'data: {json.dumps(final_data, ensure_ascii=False)}\n\n'
            except Exception as e:
                # 捕获所有异常并返回错误信息
                BaseService.log_error(f'astream处理失败: {str(e)}')
                response_data = {'error': str(e), 'astream': True}
                yield f'data: {json.dumps(response_data, ensure_ascii=False)}\n\n'
        
        return generate
    
    @staticmethod
    def handle_astream_events_response(chat, message_text, user_message, now,
                                      enhanced_question, parsed_model_name, parsed_version_name, 
                                      model_params, model_display_name, deep_thinking=False, use_agent=False,
                                      chat_service=None):
        """处理astream_events响应"""
        def generate():
            try:
                # 准备消息格式
                messages = chat_service._prepare_messages_for_model(chat['id'], enhanced_question, deep_thinking)
                
                # 获取temperature参数
                temperature = model_params.get('temperature', 0.7)
                
                chat_service.log_info("使用astream_events模式，返回事件流响应")
                
                # 初始化完整回复
                full_reply = ""
                
                # 使用流式模型回复函数获取响应
                for chunk in chat_service.chat_with_model_stream(parsed_model_name, messages, parsed_version_name, temperature, use_agent):
                    # 确保chunk是字符串格式
                    if isinstance(chunk, str):
                        # 检查是否已经是SSE格式
                        if not chunk.startswith('data: '):
                            # 如果不是SSE格式，包装成SSE格式
                            try:
                                # 尝试解析chunk，看是否是JSON格式
                                chunk_data = json.loads(chunk)
                                # 添加astream_events标记
                                chunk_data['astream_events'] = True
                                # 包装成SSE格式
                                formatted_chunk = f'data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n'
                                yield formatted_chunk
                                # 累积完整回复
                                if 'chunk' in chunk_data:
                                    full_reply += chunk_data['chunk']
                                elif 'content' in chunk_data:
                                    full_reply += chunk_data['content']
                            except:
                                # 如果不是JSON格式，直接作为内容包装
                                content_data = {'chunk': chunk, 'astream_events': True}
                                formatted_chunk = f'data: {json.dumps(content_data, ensure_ascii=False)}\n\n'
                                yield formatted_chunk
                                full_reply += chunk
                        else:
                            # 已经是SSE格式，直接返回
                            yield chunk
                            # 累积完整回复用于后续保存
                            chunk_str = chunk[6:].strip()
                            try:
                                chunk_data = json.loads(chunk_str)
                                # 添加astream_events标记
                                chunk_data['astream_events'] = True
                                if 'chunk' in chunk_data:
                                    full_reply += chunk_data['chunk']
                                elif 'content' in chunk_data:
                                    full_reply += chunk_data['content']
                            except:
                                pass
                    else:
                        # 如果不是字符串，转换为字符串并包装
                        chunk_str = str(chunk)
                        content_data = {'chunk': chunk_str, 'astream_events': True}
                        formatted_chunk = f'data: {json.dumps(content_data, ensure_ascii=False)}\n\n'
                        yield formatted_chunk
                        full_reply += chunk_str
                
                # 处理完整回复并保存
                ai_message = ResponseFormatter.process_full_reply(full_reply, now, model_display_name)
                chat_service.update_chat_and_save(chat, message_text, user_message, ai_message, now)
                
                # 发送astream_events最终完成信号
                final_data = {
                    'astream_events': True,
                    'done': True,
                    'chat': chat,
                    'user_message': user_message,
                    'ai_message': ai_message
                }
                yield f'data: {json.dumps(final_data, ensure_ascii=False)}\n\n'
            except Exception as e:
                # 捕获所有异常并返回错误信息
                BaseService.log_error(f'astream_events处理失败: {str(e)}')
                response_data = {'error': str(e), 'astream_events': True}
                yield f'data: {json.dumps(response_data, ensure_ascii=False)}\n\n'
        
        return generate
