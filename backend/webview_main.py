"""Chato应用的PyWebView入口"""
import webview
import threading
import time
import os
from app import create_app
from app.core.config import ConfigManager
from app.core.data_manager import load_data
from app.core.logging_config import logger, update_log_config

# 获取配置管理器单例实例
config_manager = ConfigManager.get_instance()

# 更新日志配置
update_log_config(config_manager)

# 使用FastAPI的lifespan事件处理机制
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("应用启动")
    yield
    # 关闭时执行
    logger.info("应用关闭")

def start_backend():
    """启动后端服务"""
    # 从配置中获取应用设置
    debug = config_manager.get('app.debug', True)
    host = config_manager.get('app.host', '127.0.0.1')
    port = config_manager.get('app.port', 5000)
    
    # 导入uvicorn并启动FastAPI应用
    import uvicorn
    uvicorn.run(
        'main:app',
        host=host,
        port=port,
        reload=False  # 禁用reload，因为在子线程中运行时会导致信号处理错误
    )

def start_webview():
    """启动PyWebView应用"""
    
    # 从配置中获取应用设置
    port = config_manager.get('app.port', 5000)
    
    # 构建前端URL，使用127.0.0.1而不是0.0.0.0
    frontend_url = f"http://127.0.0.1:{port}"
    
    # 计算屏幕中间位置
    import screeninfo
    screen = screeninfo.get_monitors()[0]
    window_width = 800
    window_height = 600
    x = (screen.width - window_width) // 2
    y = (screen.height - window_height) // 2
    
    # 创建webview窗口
    window = webview.create_window(
        "Chato",
        frontend_url,
        width=window_width,
        height=window_height,
        x=x,
        y=y,
        resizable=True,
        fullscreen=False,
        min_size=(600, 400),
    )
    
    # 启动webview主循环
    webview.start()

if __name__ == '__main__':
    # 启动后端服务线程
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # 直接启动WebView，不等待后端就绪
    logger.info("启动后端服务和WebView...")
    start_webview()
