"""Chato应用主包"""
import os

# FastAPI应用实例
def create_app():
    """创建FastAPI应用实例"""
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    
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
    
    # 注册路由
    from app.api import register_routes
    register_routes(app)
    
    # 配置静态文件服务
    # 计算正确的静态文件目录路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 从 app/__init__.py 向上三级目录到项目根目录
    project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
    frontend_dist = os.path.join(project_root, "dist")
    print(f"项目根目录: {project_root}")
    print(f"静态文件目录: {frontend_dist}")
    print(f"静态文件目录存在: {os.path.exists(frontend_dist)}")
    if os.path.exists(frontend_dist):
        app.mount("", StaticFiles(directory=frontend_dist, html=True), name="static")
        print("静态文件服务已配置")
    else:
        print("静态文件目录不存在，跳过静态文件服务配置")
    
    return app