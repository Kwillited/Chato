"""普通响应策略"""
import json
from app.utils.response_strategy.strategy.base import BaseResponseStrategyImpl
from app.utils.response_strategy.message_utils import ResponseMessageUtils


class RegularResponseStrategy(BaseResponseStrategyImpl):
    """普通非流式响应处理策略"""
    
    async def _handle_response(self, chat, message_text, user_message, now, model_messages, 
                       parsed_model_name, parsed_version_name, model_params, 
                       model_display_name, use_agent=False, 
                       model=None, chat_service=None):
        """处理普通响应"""
        # 验证模型（如果没有传入 model，则验证）
        if not model:
            model, error_response, error_code = chat_service.validate_model(parsed_model_name)
            if error_response:
                return error_response, error_code

        # 直接使用传入的 model_messages
        messages = model_messages
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

        # 使用工具类创建AI消息
        ai_message = ResponseMessageUtils.create_ai_message(ai_reply, now, model_display_name, reasoning_content)
        
        # 保存消息
        chat_service.update_chat_and_save(chat, message_text, user_message, ai_message, now)
        
        return {
            'success': True,
            'chat': chat
        }, 201
    
    def _get_error_message(self, e):
        """获取错误消息"""
        return f'调用模型失败: {str(e)}'
    
    def _handle_error(self, e):
        """处理错误"""
        return {'error': f'调用模型失败: {str(e)}'}, 500