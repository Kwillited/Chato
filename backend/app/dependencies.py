"""应用依赖项管理"""
from app.core.service_container import service_container
from app.services.chat.chat_service import ChatService
from app.services.message.message_service import MessageService


def get_chat_service():
    """获取对话服务实例"""
    return service_container.get_service('chat_service')


def get_message_service():
    """获取消息服务实例"""
    return service_container.get_service('message_service')
