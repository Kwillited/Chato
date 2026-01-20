"""依赖项提供函数"""
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.chat_repository import ChatRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.model_repository import ModelRepository
from app.repositories.setting_repository import SettingRepository
from app.services.chat.chat_service import ChatService
from app.services.data_service import DataService
from app.services.model.model_service import ModelService
from app.services.mcp.mcp_service import MCPService
from app.services.file.document_service import DocumentService

from app.services.settings.setting_service import SettingService
from app.services.vector.vector_store_service import VectorStoreService
from app.services.vector.vector_db_service import VectorDBService


# 数据库会话依赖
def get_db_session():
    """获取数据库会话"""
    return Depends(get_db)


# 仓库依赖
def get_chat_repository(db: Session = Depends(get_db)):
    """获取对话仓库实例"""
    return ChatRepository(db)


def get_message_repository(db: Session = Depends(get_db)):
    """获取消息仓库实例"""
    return MessageRepository(db)


def get_model_repository(db: Session = Depends(get_db)):
    """获取模型仓库实例"""
    return ModelRepository(db)


def get_setting_repository(db: Session = Depends(get_db)):
    """获取设置仓库实例"""
    return SettingRepository(db)


# 服务依赖
def get_chat_service(
    chat_repo: ChatRepository = Depends(get_chat_repository),
    message_repo: MessageRepository = Depends(get_message_repository)
):
    """获取对话服务实例"""
    return ChatService(chat_repo, message_repo)


def get_model_service(
    model_repo: ModelRepository = Depends(get_model_repository)
):
    """获取模型服务实例"""
    return ModelService(model_repo)


def get_setting_service(
    setting_repo: SettingRepository = Depends(get_setting_repository)
):
    """获取设置服务实例"""
    return SettingService(setting_repo)


def get_mcp_service(setting_service: SettingService = Depends(get_setting_service)):
    """获取MCP服务实例"""
    return MCPService(setting_service)


def get_vector_db_service():
    """获取向量数据库服务实例"""
    return VectorDBService()


def get_vector_store_service():
    """获取向量存储服务实例"""
    return VectorStoreService()





def get_document_service():
    """获取文档服务实例"""
    return DocumentService()


def get_data_service():
    """获取数据服务实例"""
    return DataService()