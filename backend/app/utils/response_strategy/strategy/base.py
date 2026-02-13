"""基础响应策略"""


class ResponseStrategy:
    """响应处理策略接口"""
    
    async def handle_response(self, chat, message_text, user_message, now, model_messages, 
                       parsed_model_name, parsed_version_name, model_params, 
                       model_display_name, use_agent=False, 
                       model=None, chat_service=None):
        """处理响应 - 改为异步"""
        raise NotImplementedError


class BaseResponseStrategyImpl(ResponseStrategy):
    """基础响应策略实现，提供通用功能"""
    
    async def handle_response(self, chat, message_text, user_message, now, model_messages, 
                       parsed_model_name, parsed_version_name, model_params, 
                       model_display_name, use_agent=False, 
                       model=None, chat_service=None):
        """处理响应的通用框架"""
        try:
            return await self._handle_response(chat, message_text, user_message, now, model_messages, 
                                           parsed_model_name, parsed_version_name, model_params, 
                                           model_display_name, use_agent, 
                                           model, chat_service)
        except Exception as e:
            error_msg = self._get_error_message(e)
            # 延迟导入以避免循环导入
            from app.services.base_service import BaseService
            BaseService.log_error(error_msg)
            return self._handle_error(e)
    
    async def _handle_response(self, chat, message_text, user_message, now, model_messages, 
                          parsed_model_name, parsed_version_name, model_params, 
                          model_display_name, use_agent=False, 
                          model=None, chat_service=None):
        """具体响应处理逻辑，由子类实现"""
        raise NotImplementedError
    
    def _get_error_message(self, e):
        """获取错误消息，可由子类重写"""
        return f'处理响应失败: {str(e)}'
    
    def _handle_error(self, e):
        """处理错误，可由子类重写"""
        return {'error': f'处理响应失败: {str(e)}'}, 500
