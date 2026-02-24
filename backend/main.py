"""Chato应用入口"""
import os
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

def setup():
    """应用初始化"""
    # 向量系统现在采用按需初始化，不再在启动时验证配置
    # 用户可在使用前通过设置界面配置向量系统参数
    
    # 初始化数据库，更新表结构
    from app.core.database import init_alembic_db
    init_alembic_db()
    logger.info("数据库初始化完成")
    
    # 加载初始数据
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
    
    # 只初始化 MCP 适配器，向量系统采用按需初始化
    await asyncio.gather(
        init_mcp_adapter()
    )
    
    yield
    
    # 关闭时的清理操作（如果需要）
    logger.info("应用关闭，开始清理资源")

# 创建应用实例，传入 lifespan
app = create_app(lifespan=lifespan)

if __name__ == '__main__':
    # 在应用启动前执行初始化
    setup()
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