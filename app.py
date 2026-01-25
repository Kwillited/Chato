#!/usr/bin/env python3
"""
PyWebView 应用入口文件
"""
import webview
import subprocess
import sys
import os
import time
from threading import Thread
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 获取当前文件目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# Python 解释器路径
PYTHON_EXECUTABLE = sys.executable

# FastAPI 主文件路径
FASTAPI_MAIN = os.path.join(current_dir, "backend", "main.py")

# 前端构建目录
FRONTEND_DIST = os.path.join(current_dir, "dist")

# 前端本地服务器 URL
FRONTEND_URL = "http://localhost:5000"

# 启动 FastAPI 服务器
def start_fastapi_server():
    """启动 Python FastAPI 服务器"""
    logger.info(f"正在启动 FastAPI 服务器，主文件路径: {FASTAPI_MAIN}")
    
    try:
        # 启动 FastAPI 服务器
        process = subprocess.Popen(
            [PYTHON_EXECUTABLE, FASTAPI_MAIN],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 读取服务器输出
        def read_output(pipe, prefix):
            for line in iter(pipe.readline, ''):
                logger.info(f"{prefix}: {line.strip()}")
        
        # 启动线程读取 stdout 和 stderr
        Thread(target=read_output, args=(process.stdout, "SERVER OUTPUT"), daemon=True).start()
        Thread(target=read_output, args=(process.stderr, "SERVER ERROR"), daemon=True).start()
        
        logger.info(f"FastAPI 服务器已启动，进程 ID: {process.pid}")
        return process
    except Exception as e:
        logger.error(f"启动 FastAPI 服务器失败: {e}")
        raise

# 等待服务器启动
def wait_for_server(max_retries=10, delay=1):
    """等待服务器启动完成"""
    import requests
    
    for i in range(max_retries):
        try:
            response = requests.get(FRONTEND_URL + "/api/health", timeout=2)
            if response.status_code == 200:
                logger.info("服务器已启动并响应")
                return True
        except requests.RequestException:
            logger.info(f"等待服务器启动... ({i+1}/{max_retries})")
            time.sleep(delay)
    
    logger.error("服务器启动超时")
    return False

# 创建 PyWebView 窗口
def create_window():
    """创建 PyWebView 窗口"""
    logger.info("正在创建 PyWebView 窗口")
    
    # 启动 FastAPI 服务器
    server_process = start_fastapi_server()
    
    # 等待服务器启动
    wait_for_server()
    
    # 创建 WebView 窗口
    window = webview.create_window(
        title="chato",
        url=FRONTEND_URL,
        width=800,
        height=600,
        resizable=True,
        # 窗口属性配置
    # decorations=False,  # 无边框窗口，需要自定义标题栏
    # transparent=True,   # 透明窗口
    )
    
    # 应用关闭时关闭服务器进程
    def on_closed():
        logger.info("应用关闭，正在关闭服务器进程")
        if server_process:
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
        logger.info("服务器进程已关闭")
    
    window.events.closed += on_closed
    
    return window

# 主函数
def main():
    """主函数"""
    logger.info("正在启动 PyWebView 应用")
    
    # 创建窗口
    window = create_window()
    
    # 启动 PyWebView 应用
    webview.start(
        debug=True,  # 调试模式
        # gui="cef"  # 可选，指定 WebView 引擎
    )

if __name__ == "__main__":
    main()
