"""Chato应用主包"""

# FastAPI应用实例
def create_app():
    """创建FastAPI应用实例"""
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    import os
    
    app = FastAPI(
        title="ChaTo API",
        description="ChaTo后端API服务",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc"
    )
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 首先注册API路由，确保API路由优先于静态文件服务
    from app.api import register_routes
    register_routes(app)
    
    # 然后添加静态文件服务，处理API路由没有匹配的请求
    # 获取前端构建目录路径
    # __file__ 是 N:\ChaTo\backend\app\__init__.py
    current_file_dir = os.path.dirname(os.path.abspath(__file__))  # N:\ChaTo\backend\app
    backend_dir = os.path.dirname(current_file_dir)  # N:\ChaTo\backend
    project_root_dir = os.path.dirname(backend_dir)  # N:\ChaTo
    frontend_dist = os.path.join(project_root_dir, "dist")
    
    # 使用日志记录调试信息
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Current file directory: {current_file_dir}")
    logger.info(f"Backend directory: {backend_dir}")
    logger.info(f"Project root directory: {project_root_dir}")
    logger.info(f"Frontend dist directory: {frontend_dist}")
    logger.info(f"Frontend dist exists: {os.path.exists(frontend_dist)}")
    
    # 检查前端构建目录是否存在，如果存在则添加静态文件服务
    if os.path.exists(frontend_dist):
        logger.info("Adding static file service...")
        try:
            from fastapi.staticfiles import StaticFiles
            # 添加静态文件服务，处理API路由没有匹配的请求
            app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
            logger.info("Static file service added successfully")
        except Exception as e:
            logger.error(f"Failed to add static file service: {e}")
    else:
        logger.warning("Frontend dist directory not found, skipping static file service")
    
    return app