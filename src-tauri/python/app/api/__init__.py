"""API路由模块"""

# 导入路由模块
from app.api.chats import router as chats_router
from app.api.files import router as files_router
from app.api.health import router as health_router
from app.api.models import router as models_router
from app.api.mcp import router as mcp_router
from app.api.rag import router as rag_router
from app.api.settings import router as settings_router

__all__ = ['register_routes']


def register_routes(app):
    """注册所有FastAPI路由"""
    # 注册健康检查路由
    app.include_router(health_router, tags=['health'])
    
    app.include_router(chats_router, tags=['chats'])
    app.include_router(files_router, tags=['files'])
    app.include_router(models_router, tags=['models'])
    app.include_router(mcp_router, tags=['mcp'])
    app.include_router(rag_router, tags=['rag'])
    app.include_router(settings_router, tags=['settings'])