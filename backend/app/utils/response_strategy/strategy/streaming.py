"""流式响应策略"""
import json
from app.utils.response_strategy.strategy.base import BaseResponseStrategyImpl
from app.utils.message.base import MessageSystem
from app.utils.stream import StreamSystem


class StreamingResponseStrategy(BaseResponseStrategyImpl):
    """标准流式响应处理策略（使用 AStream 实现）"""
    
    async def _handle_response(self, chat, message_text, user_message, now, model_messages, 
                       parsed_model_name, parsed_version_name, model_params, 
                       model_display_name, use_agent=False, 
                       model=None, chat_service=None):
        """处理流式响应"""
        async def generate():
            try:
                full_reply = ""
                full_reasoning = ""
                
                # 使用工具类处理流式响应
                async for chunk in StreamSystem.handle_streaming_response(
                    chat_service, parsed_model_name, model_messages, 
                    parsed_version_name, model_params, use_agent, model
                ):
                    if isinstance(chunk, dict):
                        # 处理字典类型的响应块
                        yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                        # 先提取 reasoning_content
                        if 'reasoning_content' in chunk:
                            reasoning_part = chunk.get('reasoning_content', '')
                            if reasoning_part:
                                full_reasoning += reasoning_part
                        # 从 content 字段提取内容
                        content_part = chunk.get('content', '')
                        if content_part:
                            full_reply += content_part
                    else:
                        # 处理字符串类型的响应块
                        yield f"data: {json.dumps({'chunk': str(chunk)}, ensure_ascii=False)}\n\n"
                        full_reply += str(chunk)
                
                # 使用工具类创建AI消息
                ai_message = MessageSystem.create_ai_message(
                    now, full_reply, model_display_name,
                    reasoning_content=full_reasoning
                )
                
                # 保存消息
                chat_service.update_chat_and_save(chat, message_text, user_message, ai_message, now)
                
                # 发送完成信号
                yield f'data: {json.dumps({"done": True, "ai_message": ai_message}, ensure_ascii=False)}\n\n'
            except Exception as e:
                error_msg = f'流式处理失败: {str(e)}'
                from app.services.base_service import BaseService
                BaseService.log_error(error_msg)
                yield f'data: {json.dumps({"error": str(e)}, ensure_ascii=False)}\n\n'
        return generate
    
    def _handle_error(self, e):
        """处理错误，返回流式错误响应"""
        async def generate_error():
            yield f'data: {json.dumps({"error": str(e)}, ensure_ascii=False)}\n\n'
        return generate_error