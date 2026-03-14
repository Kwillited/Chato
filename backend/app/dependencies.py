"""应用依赖项管理"""
from app.core.service_container import service_container


def get_chat_service():
    """获取对话服务实例"""
    return service_container.get_service('chat_service')


def get_message_service():
    """获取消息服务实例"""
    return service_container.get_service('message_service')


def get_data_service():
    """获取数据服务实例"""
    return service_container.get_service('data_service')


def get_document_service():
    """获取文档服务实例"""
    return service_container.get_service('document_service')


def get_model_service():
    """获取模型服务实例"""
    return service_container.get_service('model_service')


def get_embedding_model_service():
    """获取嵌入模型服务实例"""
    return service_container.get_service('embedding_model_service')


def get_mcp_service():
    """获取MCP服务实例"""
    return service_container.get_service('mcp_service')


def get_setting_service():
    """获取设置服务实例"""
    return service_container.get_service('setting_service')


def get_vector_service():
    """获取向量服务实例"""
    return service_container.get_service('vector_service')
