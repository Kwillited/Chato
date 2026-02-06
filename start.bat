@echo off
chcp 65001 >nul
echo 正在启动 Chato 应用...
echo.

IF EXIST ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" backend\webview_main.py
) ELSE (
    echo 虚拟环境不存在，尝试使用系统Python...
    python backend\webview_main.py
)

pause
