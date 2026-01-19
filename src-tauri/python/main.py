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



def init_rag():
    """初始化RAG系统"""
    # 从配置中读取RAG参数
    if config_manager.get('rag.enabled', False):
        try:
            from app.services.vector_store_service import VectorStoreService
            
            # 使用标准的用户数据目录
            user_data_dir = config_manager.get_user_data_dir()
            data_dir = os.path.join(user_data_dir, 'Retrieval-Augmented Generation', 'files')  # 文档目录
            
            # 确保目录存在
            os.makedirs(data_dir, exist_ok=True)
            
            # 使用配置文件中的向量数据库路径
            vector_db_path = config_manager.get('rag.vector_db_path', 
                                           os.path.join(user_data_dir, 'Retrieval-Augmented Generation', 'vectorDb'))
            # 获取嵌入模型配置
            embedder_model = config_manager.get('rag.embedder_model', 'qwen3-embedding-0.6b')
            
            # 创建向量存储服务实例
            vector_service = VectorStoreService(vector_db_path, embedder_model)
            
            logger.info(f"RAG系统初始化成功: 模型={embedder_model}, 向量库={vector_db_path}")
            return True
        except Exception as e:
            logger.error(f"RAG系统初始化失败: {e}")
            return False
    return False

def setup():
    """应用初始化"""
    # 加载初始数据
    load_data()
    # 初始化RAG
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