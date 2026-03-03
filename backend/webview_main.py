"""Chato应用的PyWebView入口"""
import webview
import threading
import screeninfo
import datetime

# 从配置中获取应用设置（使用默认值）
PORT = 5000


def start_backend():
    """启动后端服务"""
    # 导入uvicorn并启动FastAPI应用
    import uvicorn
    uvicorn.run(
        'main:app',
        host='127.0.0.1',
        port=PORT,
        reload=False  # 禁用reload，因为在子线程中运行时会导致信号处理错误
    )

def start_webview():
    """启动PyWebView应用"""
    # 构建前端URL
    frontend_url = f"http://127.0.0.1:{PORT}"
    
    # 计算屏幕中间位置
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
    
    # 启动WebView
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] 启动后端服务和WebView...")
    start_webview()
