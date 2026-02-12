"""普通响应策略"""
import json
from app.utils.response_strategy.strategy.base import ResponseStrategy
from app.services.base_service import BaseService
from app.utils.message_handler import MessageHandler


class RegularResponseStrategy(ResponseStrategy):
    """普通非流式响应处理策略"""
    
    async def handle_response(self, chat, message_text, user_message, now, enhanced_question, 
                       parsed_model_name, parsed_version_name, model_params, 
                       model_display_name, deep_thinking=False, use_agent=False, 
                       selected_message_ids=None, chat_service=None):
        """处理普通响应"""
        try:
            # 验证模型
            model, error_response, error_code = chat_service.validate_model(parsed_model_name)
            if error_response:
                return error_response, error_code

            messages = chat_service._prepare_messages_for_model(chat['id'], enhanced_question, deep_thinking, selected_message_ids)
            version_config = chat_service.get_version_config(model, parsed_version_name)

            chat_service.log_info("使用普通对话模式")
            
            from app.llm.managers.model_manager import ModelManager
            # 即使是非流式调用，在异步链中也建议封装为异步执行
            response = ModelManager.chat(parsed_model_name, model, version_config, messages, model_params)
        
            if isinstance(response, dict):
                ai_reply = response['content']
                reasoning_content = response.get('reasoning_content')
            else:
                ai_reply = response
                reasoning_content = None
        except Exception as e:
            BaseService.log_error(f'调用模型失败: {str(e)}')
            # 模型调用失败，不保存任何消息
            return {'error': f'调用模型失败: {str(e)}'}, 500

        # 模型响应成功，创建AI消息并保存
        ai_message = MessageHandler.Response.process_full_reply(ai_reply, now, model_display_name)
        # 添加reasoning_content到AI消息
        if reasoning_content:
            ai_message['reasoning_content'] = reasoning_content
        # 一次性保存用户消息和AI消息（用户消息已在 _process_message 中添加）
        chat_service.update_chat_and_save(chat, message_text, user_message, ai_message, now)
        
        return {
            'success': True,
            'chat': chat
        }, 201