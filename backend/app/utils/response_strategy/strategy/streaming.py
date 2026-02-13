"""流式响应策略"""
import json
from app.utils.response_strategy.strategy.base import ResponseStrategy
from app.services.base_service import BaseService
from app.utils.message_handler import MessageHandler
from app.utils.response_strategy.stream import StreamUtils


class StreamingResponseStrategy(ResponseStrategy):
    """标准流式响应处理策略（使用 AStream 实现）"""
    
    async def handle_response(self, chat, message_text, user_message, now, model_messages, 
                       parsed_model_name, parsed_version_name, model_params, 
                       model_display_name, use_agent=False, 
                       model=None, chat_service=None):
        
        async def generate():
            try:
                # 直接使用传入的 model_messages
                full_reply = ""
                full_reasoning = ""
                
                # ！！！关键：使用 async for 遍历异步生成器（AStream 实现）
                async for chunk in chat_service.chat_with_model_stream(parsed_model_name, model_messages, parsed_version_name, model_params, use_agent, model=model):
                    if isinstance(chunk, dict):
                        # 处理字典类型的响应块
                        yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                        # 先提取 reasoning_content
                        if 'reasoning_content' in chunk:
                            reasoning_part = chunk.get('reasoning_content', '')
                            if reasoning_part:  # 只有当 reasoning_part 不为空时才累积
                                full_reasoning += reasoning_part
                        # 从 content 字段提取内容
                        content_part = chunk.get('content', '')
                        if content_part:  # 只有当 content_part 不为空时才累积
                            full_reply += content_part
                    else:
                        # 处理字符串类型的响应块
                        yield f"data: {json.dumps({'chunk': str(chunk)}, ensure_ascii=False)}\n\n"
                        full_reply += str(chunk)
                
                # 模型响应成功，创建AI消息并保存
                ai_message = MessageHandler.Response.process_full_reply(full_reply, now, model_display_name, full_reasoning)
                # 一次性保存用户消息和AI消息
                chat_service.update_chat_and_save(chat, message_text, user_message, ai_message, now)
                
                # 发送完成信号
                yield f'data: {json.dumps({"done": True, "ai_message": ai_message}, ensure_ascii=False)}\n\n'
            except Exception as e:
                BaseService.log_error(f'流式处理失败: {str(e)}')
                # 模型调用失败，不保存任何消息
                yield f'data: {json.dumps({"error": str(e)}, ensure_ascii=False)}\n\n'
        return generate