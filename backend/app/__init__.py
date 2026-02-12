"""Chato应用主包"""
import os
import sys
from fastapi.staticfiles import StaticFiles

# FastAPI应用实例
def create_app(lifespan=None):
    """创建FastAPI应用实例"""
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from app.core.logging_config import logger
    
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