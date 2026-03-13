"""依赖项提供函数"""
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.service_container import service_container


# 数据库会话依赖
def get_db_session():
    """获取数据库会话"""
    return Depends(get_db)


# 服务容器依赖
def get_service_container():
    """获取服务容器实例"""
    return service_container


# 仓库依赖
def get_chat_repository():
    """获取对话仓库实例"""
    return service_container.get_service('chat_repository')


def get_message_repository():
    """获取消息仓库实例"""
    return service_container.get_service('message_repository')


def get_model_repository():
    """获取模型仓库实例"""
    return service_container.get_service('model_repository')


def get_setting_repository():
    """获取设置仓库实例"""
    return service_container.get_service('setting_repository')


def get_embedding_model_repository():
    """获取嵌入模型仓库实例"""
    return service_container.get_service('embedding_model_repository')


def get_document_repository():
    """获取文档仓库实例"""
    return service_container.get_service('document_repository')


def get_document_chunk_repository():
    """获取文档分块仓库实例"""
    return service_container.get_service('document_chunk_repository')


def get_folder_repository():
    """获取文件夹仓库实例"""
    return service_container.get_service('folder_repository')


def get_vector_repository():
    """获取向量仓库实例"""
    return service_container.get_service('vector_repository')


# 服务依赖
def get_config_manager():
    """获取配置管理器实例"""
    return service_container.get_service('config_manager')


def get_data_service():
    """获取数据服务实例"""
    return service_container.get_service('data_service')


def get_chat_service():
    """获取对话服务实例"""
    return service_container.get_service('chat_service')


def get_model_service():
    """获取模型服务实例"""
    return service_container.get_service('model_service')


def get_setting_service():
    """获取设置服务实例"""
    return service_container.get_service('setting_service')


def get_mcp_service():
    """获取MCP服务实例"""
    return service_container.get_service('mcp_service')


def get_document_service():
    """获取文档服务实例"""
    return service_container.get_service('document_service')


def get_vector_service():
    """获取向量服务实例"""
    return service_container.get_service('vector_service')


def get_message_service():
    """获取消息服务实例"""
    return service_container.get_service('message_service')


# 向量服务相关依赖
def get_vector_db_service(vector_db_path: str = '', embedder_model: str = '', knowledge_base_name: str = 'default'):
    """获取向量数据库服务实例"""
    from app.services.vector.vector_db_service_mp import VectorDBServiceMP
    return VectorDBServiceMP(
        vector_db_path=vector_db_path,
        embedder_model=embedder_model,
        knowledge_base_name=knowledge_base_name
    )


def get_vector_store_service():
    """获取向量存储服务实例"""
    from app.services.vector.vector_store_service import VectorStoreService
    return VectorStoreService()