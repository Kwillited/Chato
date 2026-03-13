"""消息相关API路由"""
from fastapi import APIRouter, Body, Path, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from app.services.message.message_service import MessageService
from app.utils.error_handler import handle_api_errors
from app.dependencies import get_message_service
from app.models.schemas.pydantic_models import SendMessageRequest

# 创建消息API路由（前缀统一为 /api/chats/{chat_id}/messages）
router = APIRouter()

# 发送消息（应用层）
@router.post('/{chat_id}/messages')
@handle_api_errors()
async def send_message(chat_id: str = Path(...), data: SendMessageRequest = Body(...), message_service: MessageService = Depends(get_message_service)):
    # 这里的 result 应该是一个异步生成器函数
    result = await message_service.send_message(chat_id, data.dict())
    
    if callable(result):
        # 传入异步生成器给 StreamingResponse
        return StreamingResponse(result(), media_type='text/event-stream')
    else:
        # 普通响应返回json和状态码
        response_data, status_code = result
        return response_data, status_code

# WebSocket连接（后续实现）
@router.websocket('/ws/{chat_id}')
async def websocket_endpoint(websocket: WebSocket, chat_id: str, message_service: MessageService = Depends(get_message_service)):
    await websocket.accept()
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_json()
            # 处理消息
            result = await message_service.send_message(chat_id, data)
            # 返回结果
            if callable(result):
                # 流式响应
                async for chunk in result():
                    await websocket.send_text(chunk)
            else:
                # 普通响应
                response_data, _ = result
                await websocket.send_json(response_data)
    except WebSocketDisconnect:
        # 处理断开连接
        pass
