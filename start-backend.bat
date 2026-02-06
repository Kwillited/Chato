@echo off
chcp 65001 >nul
echo 正在启动 Chato 后端服务...
echo.

IF EXIST ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" backend\main.py
) ELSE (
    echo 虚拟环境不存在，尝试使用系统Python...
    python backend\main.py
)

pause
