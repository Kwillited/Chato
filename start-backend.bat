@echo off
chcp 65001 >nul
echo 正在启动 Chato 后端服务...
echo.

"C:\ProgramData\anaconda3\python.exe" backend\main.py

pause
