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

async def init_vector_system():
    """初始化向量系统"""
    global _initialized
    
    # 防止重复初始化
    if _initialized:
        logger.info("向量系统已初始化，跳过重复初始化")
        return True
    
    with _initialization_lock:
        if _initialized:
            logger.info("向量系统已初始化，跳过重复初始化")
            return True
        
        try:
            from app.services.vector.vector_store_service import VectorStoreService
            
            # 使用标准的用户数据目录
            user_data_dir = config_manager.get_user_data_dir()
            data_dir = os.path.join(user_data_dir, 'Retrieval-Augmented Generation', 'files')  # 文档目录
            
            # 确保目录存在
            os.makedirs(data_dir, exist_ok=True)
            
            # 从配置中获取向量数据库路径
            vector_db_path = config_manager.get('vector.vector_db_path', 
                                           os.path.join(user_data_dir, 'Retrieval-Augmented Generation', 'vectorDb'))
            # 获取嵌入模型配置
            embedder_model = config_manager.get('vector.embedder_model', 'qwen3-embedding-0.6b')
            
            # 创建向量存储服务实例
            vector_service = VectorStoreService(vector_db_path, embedder_model)
            
            # 触发向量存储初始化（同步执行，后续可优化为异步）
            _ = vector_service.vector_store
            
            logger.info(f"向量系统初始化成功: 模型={embedder_model}, 向量库={vector_db_path}")
            _initialized = True
            return True
        except Exception as e:
            logger.error(f"向量系统初始化失败: {e}")
            return False

def setup():
    """应用初始化"""
    # 加载初始数据
    load_data()
    logger.info("应用数据加载完成")

# 创建应用实例
app = create_app()

# 在应用启动前执行初始化
setup()

async def init_mcp_adapter():
    """初始化 MCP 适配器"""
    try:
        from app.utils.mcp.mcp_adapter import mcp_adapter
        await mcp_adapter.initialize()
        logger.info("MCP 适配器初始化完成")
        return True
    except Exception as e:
        logger.error(f"MCP 适配器初始化失败: {e}")
        return False

# 使用FastAPI的后台任务机制，在应用启动后异步初始化系统组件
@app.on_event("startup")
async def startup_event():
    """应用启动事件，用于异步初始化系统组件"""
    logger.info("应用启动，开始异步初始化系统组件")
    import asyncio
    
    # 并行初始化向量系统和 MCP 适配器
    await asyncio.gather(
        init_vector_system(),
        init_mcp_adapter()
    )

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