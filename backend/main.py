"""Chato应用入口"""
from contextlib import asynccontextmanager
from app import create_app
from app.core.config import ConfigManager
from app.core.data_manager import load_data

# 获取配置管理器单例实例
config_manager = ConfigManager.get_instance()

# 导入日志模块
from app.core.logging_config import logger, update_log_config

# 更新日志配置
update_log_config(config_manager)

async def setup():
    """应用初始化"""
    
    # 加载初始数据（会自动初始化数据库）
    load_data()
    logger.info("应用数据加载完成")

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

# 使用FastAPI的 lifespan event handlers 替代 deprecated 的 on_event
@asynccontextmanager
async def lifespan(app):
    """应用生命周期管理"""
    # 启动时的初始化操作
    logger.info("应用启动，开始异步初始化系统组件")
    import asyncio
    
    # 执行异步初始化操作
    # 使用后台任务执行数据和MCP初始化，不阻塞应用启动
    # 向量系统采用按需初始化
    asyncio.create_task(setup())
    asyncio.create_task(init_mcp_adapter())
    
    yield
    
    # 关闭时的清理操作（如果需要）
    logger.info("应用关闭，开始清理资源")

# 创建应用实例，传入 lifespan
app = create_app(lifespan=lifespan)

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
        reload=False
    )