"""Chato应用入口"""
import os
from app import create_app
from app.core.config import ConfigManager
from app.core.data_manager import load_data

# 获取配置管理器单例实例
config_manager = ConfigManager.get_instance()

# 导入日志模块
from app.core.logging_config import logger, update_log_config

# 更新日志配置
update_log_config(config_manager)



import threading

# 初始化标志，防止重复初始化
_initialized = False
_initialization_lock = threading.Lock()

def init_rag():
    """初始化RAG系统"""
    global _initialized
    
    # 从配置中读取RAG参数
    if not config_manager.get('rag.enabled', False):
        return False
    
    # 防止重复初始化
    if _initialized:
        logger.info("RAG系统已初始化，跳过重复初始化")
        return True
    
    with _initialization_lock:
        if _initialized:
            logger.info("RAG系统已初始化，跳过重复初始化")
            return True
        
        try:
            from app.services.vector.vector_store_service import VectorStoreService
            
            # 使用标准的用户数据目录
            user_data_dir = config_manager.get_user_data_dir()
            data_dir = os.path.join(user_data_dir, 'Retrieval-Augmented Generation', 'files')  # 文档目录
            
            # 确保目录存在
            os.makedirs(data_dir, exist_ok=True)
            
            # 从配置中获取向量数据库路径
            vector_db_path = config_manager.get('rag.vector_db_path', 
                                           os.path.join(user_data_dir, 'Retrieval-Augmented Generation', 'vectorDb'))
            # 获取嵌入模型配置
            embedder_model = config_manager.get('rag.embedder_model', 'qwen3-embedding-0.6b')
            
            # 创建向量存储服务实例
            vector_service = VectorStoreService(vector_db_path, embedder_model)
            
            # 触发向量存储初始化（同步执行）
            _ = vector_service.vector_store
            
            logger.info(f"RAG系统初始化成功: 模型={embedder_model}, 向量库={vector_db_path}")
            _initialized = True
            return True
        except Exception as e:
            logger.error(f"RAG系统初始化失败: {e}")
            return False

def setup():
    """应用初始化"""
    # 加载初始数据
    load_data()
    # 初始化RAG（同步调用）
    init_rag()

# 创建应用实例
app = create_app()

# 在应用启动前执行初始化
setup()

if __name__ == '__main__':
    # 从配置中获取应用设置
    debug = config_manager.get('app.debug', True)
    host = config_manager.get('app.host', '0.0.0.0')
    port = config_manager.get('app.port', 5000)
    
    # 导入uvicorn并启动FastAPI应用
    import uvicorn
    uvicorn.run(
        'main:app',
        host=host,
        port=port,
        reload=debug
    )