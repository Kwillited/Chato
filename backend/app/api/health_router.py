"""健康检查API路由"""
from fastapi import APIRouter
import asyncio

# 创建健康检查API路由
router = APIRouter(prefix='/api')

# MCP初始化状态
mcp_initialized = False
mcp_initialization_task = None

async def initialize_mcp():
    """初始化MCP"""
    global mcp_initialized
    if not mcp_initialized:
        try:
            from app.core.service_container import service_container
            mcp_service = service_container.get_service('mcp_service')
            await mcp_service.initialize_mcp()
            mcp_initialized = True
        except Exception as e:
            from app.core.logger import logger
            logger.error(f"MCP 适配器初始化失败: {e}")

# 健康检查端点
@router.get('/health')
async def health_check():
    """健康检查端点"""
    global mcp_initialization_task
    
    # 启动MCP初始化（如果尚未启动）
    if not mcp_initialization_task:
        mcp_initialization_task = asyncio.create_task(initialize_mcp())
    
    # 不等待MCP初始化完成，立即返回健康状态
    # MCP初始化将在后台继续执行
    
    return {"status": "ok"}
