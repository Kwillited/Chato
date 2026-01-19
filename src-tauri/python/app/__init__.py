"""Chato应用主包"""

# FastAPI应用实例
def create_app():
    """创建FastAPI应用实例"""
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
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
    
    return app