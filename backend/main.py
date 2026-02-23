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
            
            # 从配置中获取必要的参数
            vector_db_path = config_manager.get('vector.vector_db_path')
            embedder_model = config_manager.get('vector.embedder_model')
            
            # 验证配置是否完整
            if not vector_db_path:
                logger.error("向量系统初始化失败: 缺少 vector.vector_db_path 配置")
                return False
            if not embedder_model:
                logger.error("向量系统初始化失败: 缺少 vector.embedder_model 配置")
                return False
            
            # 确保向量数据库目录存在
            os.makedirs(os.path.dirname(vector_db_path), exist_ok=True)
            
            # 创建向量存储服务实例
            vector_service = VectorStoreService(vector_db_path, embedder_model)
            
            # 注意：不再主动触发向量存储初始化，让它在首次使用时自动初始化
            # 这样嵌入模型会在真正需要时才加载，实现即用即加载
            
            logger.info(f"向量系统初始化成功: 向量库={vector_db_path}, 嵌入模型={embedder_model}")
            _initialized = True
            return True
        except Exception as e:
            logger.error(f"向量系统初始化失败: {e}")
            return False

def setup():
    """应用初始化"""
    # 验证向量系统配置
    from app.core.config import config_manager
    is_valid, errors = config_manager.validate_vector_config()
    if not is_valid:
        logger.warning("向量系统配置不完整:")
        for error in errors:
            logger.warning(f"  - {error}")
        logger.warning("请在使用向量系统前配置完整的参数")
    else:
        logger.info("向量系统配置验证通过")
    
    # 初始化数据库，更新表结构
    from app.core.database import init_alembic_db
    init_alembic_db()
    logger.info("数据库初始化完成")
    
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
        from app.services.mcp.mcp_adapter_service import MCPAdapterService
        mcp_adapter_service = MCPAdapterService()
        await mcp_adapter_service.initialize()
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