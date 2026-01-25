"""API路由模块"""

# 导入路由模块
from app.api.chats_router import router as chats_router
from app.api.files_router import router as files_router
from app.api.health_router import router as health_router
from app.api.models_router import router as models_router
from app.api.mcp_router import router as mcp_router
from app.api.settings_router import router as settings_router
from app.api.vector_router import router as vector_router
from app.api.ollama_router import router as ollama_router

__all__ = ['register_routes']


def register_routes(app):
    """注册所有FastAPI路由"""
    # 注册健康检查路由
    app.include_router(health_router, tags=['health'])
    
    app.include_router(chats_router, tags=['chats'])
    app.include_router(files_router, tags=['files'])
    app.include_router(models_router, tags=['models'])
    app.include_router(mcp_router, tags=['mcp'])
    app.include_router(settings_router, tags=['settings'])
    app.include_router(vector_router, tags=['vectors'])
    app.include_router(ollama_router, tags=['ollama'])