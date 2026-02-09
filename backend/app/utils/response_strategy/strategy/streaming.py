"""流式响应策略"""
import json
from app.utils.response_strategy.strategy.base import ResponseStrategy
from app.services.base_service import BaseService
from app.utils.message_handler import MessageHandler
from app.utils.response_strategy.stream import StreamUtils


class StreamingResponseStrategy(ResponseStrategy):
    """标准流式响应处理策略（使用 AStream 实现）"""
    
    async def handle_response(self, chat, message_text, user_message, now, enhanced_question, 
                       parsed_model_name, parsed_version_name, model_params, 
                       model_display_name, deep_thinking=False, use_agent=False, 
                       chat_service=None):
        
        async def generate():
            try:
                messages = chat_service._prepare_messages_for_model(chat['id'], enhanced_question, deep_thinking)
                full_reply = ""
                
                # ！！！关键：使用 async for 遍历异步生成器（AStream 实现）
                async for chunk in chat_service.chat_with_model_stream(parsed_model_name, messages, parsed_version_name, model_params, use_agent):
                    if isinstance(chunk, dict):
                        # 处理字典类型的响应块
                        yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                        full_reply += chunk.get('chunk', chunk.get('content', ''))
                    else:
                        # 处理字符串类型的响应块
                        yield f"data: {json.dumps({'chunk': str(chunk)}, ensure_ascii=False)}\n\n"
                        full_reply += str(chunk)
                
                # 模型响应成功，创建AI消息并保存
                ai_message = MessageHandler.Response.process_full_reply(full_reply, now, model_display_name)
                # 将用户消息添加到对话中
                chat['messages'].append(user_message)
                # 一次性保存用户消息和AI消息
                chat_service.update_chat_and_save(chat, message_text, user_message, ai_message, now)
                
                # 发送完成信号
                yield f'data: {json.dumps({"done": True, "ai_message": ai_message}, ensure_ascii=False)}\n\n'
            except Exception as e:
                BaseService.log_error(f'流式处理失败: {str(e)}')
                # 模型调用失败，不保存任何消息
                yield f'data: {json.dumps({"error": str(e)}, ensure_ascii=False)}\n\n'
        return generate