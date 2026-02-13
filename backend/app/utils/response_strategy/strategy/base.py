"""基础响应策略"""


class ResponseStrategy:
    """响应处理策略接口"""
    
    async def handle_response(self, chat, message_text, user_message, now, model_messages, 
                       parsed_model_name, parsed_version_name, model_params, 
                       model_display_name, use_agent=False, 
                       model=None, chat_service=None):
        """处理响应 - 改为异步"""
        raise NotImplementedError
