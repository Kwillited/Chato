"""响应处理器工具类"""
import json
import asyncio
from typing import Dict, Any, Generator, Callable

from app.utils.response_formatter import ResponseFormatter
from app.services.base_service import BaseService


class ResponseStrategy:
    """响应处理策略接口"""
    
    async def handle_response(self, chat, message_text, user_message, now, enhanced_question, 
                       parsed_model_name, parsed_version_name, model_params, 
                       model_display_name, deep_thinking=False, use_agent=False, 
                       chat_service=None):
        """处理响应 - 改为异步"""
        raise NotImplementedError


class RegularResponseStrategy(ResponseStrategy):
    """普通非流式响应处理策略"""
    
    async def handle_response(self, chat, message_text, user_message, now, enhanced_question, 
                       parsed_model_name, parsed_version_name, model_params, 
                       model_display_name, deep_thinking=False, use_agent=False, 
                       chat_service=None):
        """处理普通响应"""
        try:
            # 验证模型
            model, error_response, error_code = chat_service.validate_model(parsed_model_name)
            if error_response:
                return error_response, error_code

            messages = chat_service._prepare_messages_for_model(chat['id'], enhanced_question, deep_thinking)
            temperature = model_params.get('temperature', 0.7)
            version_config = chat_service.get_version_config(model, parsed_version_name)

            chat_service.log_info("使用普通对话模式")
            
            from app.models.model_manager import ModelManager
            # 即使是非流式调用，在异步链中也建议封装为异步执行
            response = ModelManager.chat(parsed_model_name, model, version_config, messages, temperature)
        
            if isinstance(response, dict) and 'content' in response:
                ai_reply = response['content']
            else:
                ai_reply = response
        except Exception as e:
            BaseService.log_error(f'调用模型失败: {str(e)}')
            return {'error': f'调用模型失败: {str(e)}'}, 500

        ai_message = ResponseFormatter.process_full_reply(ai_reply, now, model_display_name)
        chat_service.update_chat_and_save(chat, message_text, user_message, ai_message, now)
        
        return {
            'success': True,
            'chat': chat,
            'user_message': user_message,
            'ai_message': ai_message
        }, 201


class StreamingResponseStrategy(ResponseStrategy):
    """标准流式响应处理策略"""
    
    async def handle_response(self, chat, message_text, user_message, now, enhanced_question, 
                       parsed_model_name, parsed_version_name, model_params, 
                       model_display_name, deep_thinking=False, use_agent=False, 
                       chat_service=None):
        
        # 必须定义为异步生成器
        async def generate():
            try:
                messages = chat_service._prepare_messages_for_model(chat['id'], enhanced_question, deep_thinking)
                temperature = model_params.get('temperature', 0.7)
                full_reply = ""
                
                # ！！！关键：改用 async for 遍历异步生成器
                async for chunk in chat_service.chat_with_model_stream(parsed_model_name, messages, parsed_version_name, temperature, use_agent):
                    formatted_chunk, full_reply = ResponseFormatter.process_streaming_chunk(chunk, full_reply)
                    yield formatted_chunk
                
                ai_message = ResponseFormatter.process_full_reply(full_reply, now, model_display_name)
                chat_service.update_chat_and_save(chat, message_text, user_message, ai_message, now)
                
                final_data = {'done': True, 'chat': chat, 'ai_message': ai_message}
                yield f'data: {json.dumps(final_data, ensure_ascii=False)}\n\n'
            except Exception as e:
                BaseService.log_error(f'流式处理失败: {str(e)}')
                yield f'data: {json.dumps({"error": str(e)}, ensure_ascii=False)}\n\n'
        return generate


class AgentResponseStrategy(ResponseStrategy):
    """智能体响应处理策略"""
    
    async def handle_response(self, chat, message_text, user_message, now, enhanced_question, 
                       parsed_model_name, parsed_version_name, model_params, 
                       model_display_name, deep_thinking=False, use_agent=False, 
                       chat_service=None):
        
        async def generate():
            try:
                messages = chat_service._prepare_messages_for_model(chat['id'], enhanced_question, deep_thinking)
                temperature = model_params.get('temperature', 0.7)
                full_reply = ""
                
                # ！！！关键：改用 async for
                async for chunk in chat_service.chat_with_model_stream(parsed_model_name, messages, parsed_version_name, temperature, use_agent):
                    if isinstance(chunk, dict):
                        chunk['agent'] = True
                        yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                        full_reply += chunk.get('chunk', chunk.get('content', ''))
                    else:
                        yield f"data: {json.dumps({'chunk': str(chunk), 'agent': True}, ensure_ascii=False)}\n\n"
                        full_reply += str(chunk)
                
                ai_message = ResponseFormatter.process_full_reply(full_reply, now, model_display_name)
                chat_service.update_chat_and_save(chat, message_text, user_message, ai_message, now)
                yield f'data: {json.dumps({"agent": True, "done": True, "ai_message": ai_message}, ensure_ascii=False)}\n\n'
            except Exception as e:
                yield f'data: {json.dumps({"error": str(e)}, ensure_ascii=False)}\n\n'
        return generate


class AStreamResponseStrategy(ResponseStrategy):
    """AStream响应处理策略"""
    
    async def handle_response(self, chat, message_text, user_message, now, enhanced_question, 
                       parsed_model_name, parsed_version_name, model_params, 
                       model_display_name, deep_thinking=False, use_agent=False, 
                       chat_service=None):
        
        async def generate():
            try:
                messages = chat_service._prepare_messages_for_model(chat['id'], enhanced_question, deep_thinking)
                temperature = model_params.get('temperature', 0.7)
                full_reply = ""
                
                async for chunk in chat_service.chat_with_model_stream(parsed_model_name, messages, parsed_version_name, temperature, use_agent):
                    if isinstance(chunk, dict):
                        chunk['astream'] = True
                        yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                        full_reply += chunk.get('chunk', chunk.get('content', ''))
                    else:
                        yield f"data: {json.dumps({'chunk': str(chunk), 'astream': True}, ensure_ascii=False)}\n\n"
                        full_reply += str(chunk)
                
                ai_message = ResponseFormatter.process_full_reply(full_reply, now, model_display_name)
                chat_service.update_chat_and_save(chat, message_text, user_message, ai_message, now)
                yield f'data: {json.dumps({"astream": True, "done": True, "ai_message": ai_message}, ensure_ascii=False)}\n\n'
            except Exception as e:
                yield f'data: {json.dumps({"error": str(e)}, ensure_ascii=False)}\n\n'
        return generate


class AStreamEventsResponseStrategy(ResponseStrategy):
    """异步事件流响应处理策略"""
    
    async def handle_response(self, chat, message_text, user_message, now, enhanced_question, 
                       parsed_model_name, parsed_version_name, model_params, 
                       model_display_name, deep_thinking=False, use_agent=False, 
                       chat_service=None):
        
        async def generate():
            full_reply = ""
            try:
                messages = chat_service._prepare_messages_for_model(chat['id'], enhanced_question, deep_thinking)
                temperature = model_params.get('temperature', 0.7)
                
                # ！！！关键：async for
                async for chunk in chat_service.chat_with_model_stream(parsed_model_name, messages, parsed_version_name, temperature, use_agent):
                    if isinstance(chunk, str) and chunk.startswith('data: '):
                        yield chunk
                    else:
                        if isinstance(chunk, dict):
                            chunk['astream_events'] = True
                        else:
                            chunk = {'chunk': str(chunk), 'astream_events': True}
                        yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                        full_reply += chunk.get('chunk', chunk.get('content', ''))

                ai_message = ResponseFormatter.process_full_reply(full_reply, now, model_display_name)
                chat_service.update_chat_and_save(chat, message_text, user_message, ai_message, now)
                yield f"data: {json.dumps({'astream_events': True, 'done': True, 'ai_message': ai_message}, ensure_ascii=False)}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
        return generate


class ResponseStrategyContext:
    """响应策略上下文"""
    
    def __init__(self, strategy: ResponseStrategy):
        self._strategy = strategy
    
    def set_strategy(self, strategy: ResponseStrategy):
        self._strategy = strategy
    
    async def handle_response(self, chat, message_text, user_message, now, enhanced_question, 
                       parsed_model_name, parsed_version_name, model_params, 
                       model_display_name, deep_thinking=False, use_agent=False, 
                       chat_service=None):
        # 必须 await 策略的异步方法
        return await self._strategy.handle_response(chat, message_text, user_message, now, 
                                             enhanced_question, parsed_model_name, 
                                             parsed_version_name, model_params, 
                                             model_display_name, deep_thinking, 
                                             use_agent, chat_service)


class ResponseHandler:
    """响应处理器，处理不同类型的响应"""
    
    @staticmethod
    async def handle_regular_response(chat, message_text, user_message, now,
                               enhanced_question, parsed_model_name, parsed_version_name, 
                               model_params, model_display_name, deep_thinking=False, use_agent=False,
                               chat_service=None):
        strategy = RegularResponseStrategy()
        context = ResponseStrategyContext(strategy)
        return await context.handle_response(chat, message_text, user_message, now, 
                                      enhanced_question, parsed_model_name, parsed_version_name, 
                                      model_params, model_display_name, deep_thinking, use_agent, 
                                      chat_service)
    
    @staticmethod
    async def handle_streaming_response(chat, message_text, user_message, now,
                                 enhanced_question, parsed_model_name, parsed_version_name, 
                                 model_params, model_display_name, deep_thinking=False, use_agent=False,
                                 chat_service=None):
        if use_agent:
            strategy = AgentResponseStrategy()
        else:
            strategy = StreamingResponseStrategy()
        context = ResponseStrategyContext(strategy)
        return await context.handle_response(chat, message_text, user_message, now, 
                                      enhanced_question, parsed_model_name, parsed_version_name, 
                                      model_params, model_display_name, deep_thinking, use_agent, 
                                      chat_service)
    
    @staticmethod
    async def handle_astream_response(chat, message_text, user_message, now,
                               enhanced_question, parsed_model_name, parsed_version_name, 
                               model_params, model_display_name, deep_thinking=False, use_agent=False,
                               chat_service=None):
        strategy = AStreamResponseStrategy()
        context = ResponseStrategyContext(strategy)
        return await context.handle_response(chat, message_text, user_message, now, 
                                      enhanced_question, parsed_model_name, parsed_version_name, 
                                      model_params, model_display_name, deep_thinking, use_agent, 
                                      chat_service)
    
    @staticmethod
    async def handle_astream_events_response(chat, message_text, user_message, now,
                                      enhanced_question, parsed_model_name, parsed_version_name, 
                                      model_params, model_display_name, deep_thinking=False, use_agent=False,
                                      chat_service=None):
        strategy = AStreamEventsResponseStrategy()
        context = ResponseStrategyContext(strategy)
        return await context.handle_response(chat, message_text, user_message, now, 
                                      enhanced_question, parsed_model_name, parsed_version_name, 
                                      model_params, model_display_name, deep_thinking, use_agent, 
                                      chat_service)