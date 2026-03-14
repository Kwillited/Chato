"""Chato应用主包"""
import os
import sys
from fastapi.staticfiles import StaticFiles

# 注册服务到服务容器
def register_services():
    """注册所有服务到服务容器"""
    from app.core.service_container import service_container
    
    # 注册配置管理器
    from app.core.config import ConfigManager
    service_container.register_service('config_manager', ConfigManager.get_instance)
    
    # 注册数据服务
    from app.services.data_service import DataService
    service_container.register_service('data_service', DataService)
    
    # 注册仓库服务
    from app.repositories.chat_repository import ChatRepository
    from app.repositories.message_repository import MessageRepository
    from app.repositories.model_repository import ModelRepository
    from app.repositories.setting_repository import SettingRepository
    from app.repositories.embedding_model_repository import EmbeddingModelRepository
    from app.repositories.document_repository import DocumentRepository
    from app.repositories.document_chunk_repository import DocumentChunkRepository
    from app.repositories.folder_repository import FolderRepository
    from app.repositories.vector_repository import VectorRepository
    
    service_container.register_service('chat_repository', ChatRepository)
    service_container.register_service('message_repository', MessageRepository)
    service_container.register_service('model_repository', ModelRepository)
    service_container.register_service('setting_repository', SettingRepository)
    service_container.register_service('embedding_model_repository', EmbeddingModelRepository)
    service_container.register_service('document_repository', DocumentRepository)
    service_container.register_service('document_chunk_repository', DocumentChunkRepository)
    service_container.register_service('folder_repository', FolderRepository)
    service_container.register_service('vector_repository', VectorRepository)
    
    # 注册业务服务
    from app.services.chat.chat_service import ChatService
    from app.services.model.model_service import ModelService
    from app.services.model.embedding_model_service import EmbeddingModelService
    from app.services.settings.setting_service import SettingService
    from app.services.mcp.mcp_service import MCPService
    from app.services.file.document_service import DocumentService
    from app.services.vector.vector_service import VectorService
    from app.services.message.message_service import MessageService
    from app.services.web.web_search_service import WebSearchService
    
    service_container.register_service('chat_service', ChatService)
    service_container.register_service('model_service', ModelService, 'model_repository')
    service_container.register_service('embedding_model_service', EmbeddingModelService)
    service_container.register_service('setting_service', SettingService, 'setting_repository')
    service_container.register_service('mcp_service', MCPService, 'setting_service')
    service_container.register_service('vector_service', VectorService)
    service_container.register_service('web_search_service', WebSearchService)
    service_container.register_service('document_service', DocumentService, 'data_service', 'vector_service')
    service_container.register_service('message_service', MessageService, 'chat_service', 'vector_service', 'web_search_service')

# FastAPI应用实例
def create_app(lifespan=None):
    """创建FastAPI应用实例"""
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from app.core.logger import logger
    
    # 注册服务
    register_services()
    
    app = FastAPI(
        title="ChaTo API",
        description="ChaTo后端API服务",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        lifespan=lifespan
    )
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    from app.api import register_routes
    register_routes(app)
    
    # 配置静态文件服务
    _configure_static_files(app, logger)
    
    return app

def _configure_static_files(app, logger):
    """配置静态文件服务"""
    # 确定基础目录和需要尝试的路径
    if hasattr(sys, '_MEIPASS'):
        # 在PyInstaller打包环境中，web_dist内容直接复制到根目录
        base_dir = sys._MEIPASS
        logger.info(f"PyInstaller环境: {base_dir}")
        # 只需要尝试PyInstaller基础目录
        possible_paths = [base_dir]
        path_names = ["PyInstaller基础目录"]
    else:
        # 在开发环境中，前端文件位于项目根目录下的web_dist文件夹
        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
        logger.info(f"开发环境: {base_dir}")
        # 只需要尝试开发环境路径
        possible_paths = [os.path.join(base_dir, "web_dist")]
        path_names = ["开发环境路径"]
    
    # 查找合适的静态文件目录
    frontend_dist = None
    selected_path = ""
    
    for i, path in enumerate(possible_paths):
        if os.path.exists(path) and os.path.exists(os.path.join(path, "index.html")):
            frontend_dist = path
            selected_path = path_names[i]
            break
    
    # 配置静态文件服务
    if frontend_dist:
        logger.info(f"静态文件目录: {frontend_dist} ({selected_path})")
        app.mount("", StaticFiles(directory=frontend_dist, html=True), name="static")
        logger.info("静态文件服务已配置")
    else:
        logger.error("未找到包含index.html的静态文件目录")
        logger.error(f"尝试的路径: {possible_paths}")