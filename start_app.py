#!/usr/bin/env python3
"""
Chato应用启动脚本
"""
import os
import sys
import subprocess
import time
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 获取当前脚本目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# PyWebView应用入口
PYWEBVIEW_APP = os.path.join(SCRIPT_DIR, "app.py")

# 启动PyWebView应用
def start_pywebview_app():
    """启动PyWebView应用"""
    logger.info("正在启动PyWebView应用...")
    
    try:
        # 启动PyWebView应用
        process = subprocess.Popen(
            [sys.executable, PYWEBVIEW_APP],
            cwd=SCRIPT_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 读取输出
        def read_output(pipe, prefix):
            for line in iter(pipe.readline, ''):
                logger.info(f"{prefix}: {line.strip()}")
        
        # 启动线程读取输出
        import threading
        threading.Thread(target=read_output, args=(process.stdout, "APP OUTPUT"), daemon=True).start()
        threading.Thread(target=read_output, args=(process.stderr, "APP ERROR"), daemon=True).start()
        
        logger.info(f"PyWebView应用已启动，进程ID: {process.pid}")
        return process
    except Exception as e:
        logger.error(f"启动PyWebView应用失败: {e}")
        raise

# 主函数
def main():
    """主函数"""
    logger.info("Chato应用启动脚本")
    
    # 启动PyWebView应用
    process = start_pywebview_app()
    
    # 等待应用退出
    try:
        process.wait()
    except KeyboardInterrupt:
        logger.info("收到键盘中断，正在关闭应用...")
        process.terminate()
        process.wait(timeout=5)
    
    logger.info("应用已退出")

if __name__ == "__main__":
    main()
