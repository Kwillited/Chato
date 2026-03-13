"""应用依赖项管理"""
from app.services.chat.chat_service import ChatService
from app.services.message.message_service import MessageService


def get_chat_service():
    """获取对话服务实例"""
    return ChatService()


def get_message_service():
    """获取消息服务实例"""
    return MessageService()
