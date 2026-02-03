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

# 初始化标志，防止重复初始化
_initialized = False
_initialization_lock = threading.Lock()

async def init_vector_system():
    """初始化向量系统"""
    global _initialized
    
    # 防止重复初始化
    if _initialized:
        logger.info("向量系统已初始化，跳过重复初始化")
        return True
    
    with _initialization_lock:
        if _initialized:
            logger.info("向量系统已初始化，跳过重复初始化")
            return True
        
        try:
            from app.services.vector.vector_store_service import VectorStoreService
            
            # 使用标准的用户数据目录
            user_data_dir = config_manager.get_user_data_dir()
            data_dir = os.path.join(user_data_dir, 'Retrieval-Augmented Generation', 'files')  # 文档目录
            
            # 确保目录存在
            os.makedirs(data_dir, exist_ok=True)
            
            # 从配置中获取向量数据库路径
            vector_db_path = config_manager.get('vector.vector_db_path', 
                                           os.path.join(user_data_dir, 'Retrieval-Augmented Generation', 'vectorDb'))
            # 获取嵌入模型配置
            embedder_model = config_manager.get('vector.embedder_model', 'qwen3-embedding-0.6b')
            
            # 创建向量存储服务实例
            vector_service = VectorStoreService(vector_db_path, embedder_model)
            
            # 触发向量存储初始化（同步执行，后续可优化为异步）
            _ = vector_service.vector_store
            
            logger.info(f"向量系统初始化成功: 模型={embedder_model}, 向量库={vector_db_path}")
            _initialized = True
            return True
        except Exception as e:
            logger.error(f"向量系统初始化失败: {e}")
            return False

def setup():
    """应用初始化"""
    # 加载初始数据
    load_data()
    logger.info("应用数据加载完成")

# 使用FastAPI的lifespan事件处理机制
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("应用启动，开始异步初始化向量系统")
    import asyncio
    asyncio.create_task(init_vector_system())
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
    
    # 窗口状态跟踪
    is_maximized = False
    
    # 定义窗口控制API
    class Api:
        def minimize_window(self):
            window.minimize()
        
        def maximize_window(self):
            nonlocal is_maximized
            if is_maximized:
                window.restore()
                is_maximized = False
            else:
                window.maximize()
                is_maximized = True
        
        def close_window(self):
            window.destroy()
    
    # 创建webview窗口
    window = webview.create_window(
        "Chato",
        frontend_url,
        width=800,
        height=600,
        resizable=True,
        fullscreen=False,
        min_size=(600, 400),
        js_api=Api()
    )
    
    # 启动webview主循环
    webview.start()

if __name__ == '__main__':
    # 启动后端服务线程
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # 等待后端服务启动完成
    import time
    import requests
    
    port = config_manager.get('app.port', 5000)
    backend_url = f"http://127.0.0.1:{port}/api/health"
    
    # 尝试连接后端服务，最多等待30秒
    max_wait_time = 30
    start_time = time.time()
    
    logger.info("等待后端服务启动...")
    while time.time() - start_time < max_wait_time:
        try:
            response = requests.get(backend_url, timeout=1)
            if response.status_code == 200:
                logger.info("后端服务已就绪，启动WebView")
                break
        except:
            pass
        time.sleep(1)
    
    # 启动PyWebView
    start_webview()
