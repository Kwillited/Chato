"""对话相关API路由"""
from fastapi import APIRouter, Body, Path, HTTPException, Depends
from fastapi.responses import StreamingResponse
from app.services.chat.chat_service import ChatService  # 导入对话服务类
from app.utils.error_handler import handle_api_errors
from app.dependencies import get_chat_service
from app.models.schemas.pydantic_models import (
    ChatListResponse, ChatResponse,
    PinUpdateRequest, PinUpdateResponse, DeleteChatResponse,
    SuccessResponse, SendMessageRequest
)

# 创建对话API路由（前缀统一为 /api/chats）
router = APIRouter(prefix='/api/chats')

# 获取所有对话
@router.get('', response_model=ChatListResponse)
@handle_api_errors()
def get_chats(chat_service: ChatService = Depends(get_chat_service)):
    chats = chat_service.get_chats()
    return ChatListResponse(chats=chats)



# 获取单个对话记录（按ID）
@router.get('/{chat_id}', response_model=ChatResponse)
@handle_api_errors()
def get_chat(chat_id: str = Path(...), chat_service: ChatService = Depends(get_chat_service)):
    # 使用服务层获取对话
    chat = chat_service.get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail='对话不存在')
    
    return ChatResponse(chat=chat)

# 删除所有对话记录
@router.delete('/delete-all', response_model=SuccessResponse)
@handle_api_errors()
def delete_all_chats(chat_service: ChatService = Depends(get_chat_service)):
    # 使用服务层删除所有对话
    chat_service.delete_all_chats()
    return SuccessResponse(success=True, message='所有对话已删除')

# 删除单个对话记录（按ID）
@router.delete('/{chat_id}', response_model=DeleteChatResponse)
@handle_api_errors()
def delete_chat(chat_id: str = Path(...), chat_service: ChatService = Depends(get_chat_service)):
    # 使用服务层删除对话
    success = chat_service.delete_chat(chat_id)
    if not success:
        raise HTTPException(status_code=404, detail='对话不存在')
    
    return DeleteChatResponse(success=True, message='对话已删除')

# 更新对话置顶状态
@router.patch('/{chat_id}/pin', response_model=PinUpdateResponse)
@handle_api_errors()
def update_chat_pin(chat_id: str = Path(...), data: PinUpdateRequest = Body(...), chat_service: ChatService = Depends(get_chat_service)):
    pinned = data.pinned
    
    # 使用服务层更新对话置顶状态
    success = chat_service.update_chat_pin(chat_id, pinned)
    if not success:
        raise HTTPException(status_code=404, detail='对话不存在')
    
    return PinUpdateResponse(success=True, message=f'对话已{"置顶" if pinned else "取消置顶"}')

# 发送消息（应用层）
@router.post('/{chat_id}/messages')
@handle_api_errors()
async def send_message(chat_id: str = Path(...), data: SendMessageRequest = Body(...), chat_service: ChatService = Depends(get_chat_service)):
    # 这里的 result 应该是一个异步生成器函数
    result = await chat_service.send_message(chat_id, data.dict())
    
    if callable(result):
        # 传入异步生成器给 StreamingResponse
        return StreamingResponse(result(), media_type='text/event-stream')
    else:
        # 普通响应返回json和状态码
        response_data, status_code = result
        return response_data, status_code