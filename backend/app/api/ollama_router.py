"""Ollama服务管理API路由"""
from fastapi import APIRouter
import subprocess
import sys

router = APIRouter(prefix="/api/ollama", tags=["ollama"])

# 检查Ollama服务状态
@router.get("/status")
async def check_ollama_status():
    """检查Ollama服务状态"""
    # 首先检查Ollama是否安装
    try:
        ollama_check = subprocess.run(
            ["where", "ollama"] if sys.platform == "win32" else ["which", "ollama"],
            capture_output=True,
            text=True,
            check=True
        )
        installed = True
    except subprocess.CalledProcessError:
        installed = False
    
    # 如果Ollama已安装，检查服务是否正在运行
    if installed:
        try:
            import requests
            response = requests.get("http://localhost:11434/api/version", timeout=2)
            running = response.status_code == 200
        except requests.RequestException:
            running = False
    else:
        running = False
    
    return {
        "installed": installed,
        "running": running
    }

# 启动Ollama服务
@router.post("/start")
async def start_ollama_service():
    """启动Ollama服务"""
    try:
        # 检查Ollama是否安装
        subprocess.run(
            ["where", "ollama"] if sys.platform == "win32" else ["which", "ollama"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # 启动Ollama服务
        if sys.platform == "win32":
            # Windows系统
            subprocess.Popen(
                ["ollama", "serve"],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:
            # 非Windows系统
            subprocess.Popen(["ollama", "serve"])
        
        return {
            "success": True,
            "message": "Ollama服务已启动"
        }
    except subprocess.CalledProcessError:
        return {
            "success": False,
            "message": "Ollama未安装"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"启动Ollama服务失败: {str(e)}"
        }
