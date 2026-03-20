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
        """处理流式响应（直接返回LLM原始事件流）"""
        async def generate():
            try:
                ai_message = None
                
                # 使用工具类处理流式响应
                async for event in StreamSystem.handle_streaming_response(
                    chat_service, parsed_model_name, model_messages, 
                    parsed_version_name, model_params, use_agent, model
                ):
                    # 处理可能的非序列化对象
                    if isinstance(event, dict):
                        # 转换事件为可序列化格式
                        def convert_to_serializable(data):
                            if isinstance(data, dict):
                                return {k: convert_to_serializable(v) for k, v in data.items()}
                            elif isinstance(data, list):
                                return [convert_to_serializable(item) for item in data]
                            elif hasattr(data, 'dict'):
                                return convert_to_serializable(data.dict())
                            elif hasattr(data, '__dict__'):
                                return convert_to_serializable({k: v for k, v in data.__dict__.items() if not k.startswith('_')})
                            else:
                                return data
                        
                        serializable_event = convert_to_serializable(event)
                        yield f"data: {json.dumps(serializable_event, ensure_ascii=False)}\n\n"
                        
                        # 从 on_chat_model_end 事件中获取完整数据
                        event_type = event.get("event")
                        if event_type == "on_chat_model_end":
                            event_data = event.get("data", {})
                            output = event_data.get("output", {})
                            
                            # 获取完整的回复内容
                            content = ""
                            reasoning_content = None
                            
                            # 直接处理 AIMessageChunk 对象
                            if hasattr(output, "content"):
                                content = output.content
                            if hasattr(output, "additional_kwargs"):
                                additional_kwargs = output.additional_kwargs
                                if isinstance(additional_kwargs, dict):
                                    reasoning_content = additional_kwargs.get("reasoning_content")
                            
                            # 使用工具类创建AI消息
                            ai_message = MessageSystem.create_ai_message(
                                now, content, model_display_name,
                                reasoning_content=reasoning_content
                            )
                    else:
                        # 处理非字典类型的事件
                        yield f"data: {json.dumps({'event': 'unknown', 'data': str(event)}, ensure_ascii=False)}\n\n"
                
                # 只有当我们从 on_chat_model_end 事件中获取到数据时才保存消息
                if ai_message:
                    # 保存消息
                    chat_service.update_chat_and_save(chat, message_text, user_message, ai_message, now)
                    
                    # 发送完成信号
                    yield f'data: {json.dumps({"done": True, "ai_message": ai_message}, ensure_ascii=False)}\n\n'
                else:
                    # 如果没有从 on_chat_model_end 获取到数据，发送简单的完成信号
                    yield f'data: {json.dumps({"done": True}, ensure_ascii=False)}\n\n'
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