"""Chato 工具函数模块"""

# 统一验证工具
from .validators import ValidationUtils

# 统一错误处理工具
from .error_handler import ErrorHandler, handle_errors, handle_api_errors, handle_db_errors, handle_vector_errors

# 统一文件工具
from .file_utils import FileUtils



# 提示词管理工具
from .prompt_manager import prompt_manager, PromptManager
from .message_builder import MessageBuilder



# 消息处理模块
from .message import MessageSystem, AgentSystem

# 流式处理模块
from .stream import StreamSystem

# 数据处理模块
from .data import (
    generate_unique_id,
    format_timestamp,
    serialize_to_json,
    deserialize_from_json,
    normalize_path,
    format_bytes,
    flatten_dict,
    merge_dicts,
    sanitize_filename,
    create_pagination_metadata,
    paginate_list,
    build_message_list,
    build_chat_dict,
    ModelConverter,
    NamingUtils
)

# 模型相关模块
from .model import ModelUtils

# RAG和向量模块
from .rag import DocumentLoader, TextSplitter, VectorUtils

__all__ = [
    # 统一验证工具
    'ValidationUtils',
    
    # 统一错误处理工具
    'ErrorHandler',
    'handle_errors',
    'handle_api_errors',
    'handle_db_errors',
    'handle_vector_errors',
    
    # 统一文件工具
    'FileUtils',
    

    
    # 提示词管理工具
    'prompt_manager',
    'PromptManager',
    'MessageBuilder',
    

    
    # 消息处理模块
    'MessageSystem',
    'AgentSystem',
    
    # 流式处理模块
    'StreamSystem',
    
    # 数据处理模块
    'generate_unique_id',
    'format_timestamp',
    'serialize_to_json',
    'deserialize_from_json',
    'normalize_path',
    'format_bytes',
    'flatten_dict',
    'merge_dicts',
    'sanitize_filename',
    'create_pagination_metadata',
    'paginate_list',
    'build_message_list',
    'build_chat_dict',
    'ModelConverter',
    'NamingUtils',
    
    # 模型相关模块
    'ModelUtils',
    
    # RAG和向量模块
    'DocumentLoader',
    'TextSplitter',
    'VectorUtils'
]