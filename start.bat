@echo off
REM 一键启动脚本 (Windows)
REM 分别打开两个窗口运行后端(8000)和前端(5173)。
REM 用法:  双击运行, 或命令行  start.bat        使用真实行情
REM        命令行  start.bat mock              使用演示数据(无需联网)
setlocal
cd /d "%~dp0"

set USE_MOCK_DATA=0
if /I "%1"=="mock" set USE_MOCK_DATA=1

echo [1/2] 准备并启动后端窗口...
start "后端 backend:8000" cmd /k ^
  "cd backend ^&^& (if not exist .venv python -m venv .venv) ^&^& call .venv\Scripts\activate.bat ^&^& pip install -q -r requirements.txt ^&^& set USE_MOCK_DATA=%USE_MOCK_DATA% ^&^& python -m uvicorn main:app --host 0.0.0.0 --port 8000"

echo [2/2] 准备并启动前端窗口...
start "前端 frontend:5173" cmd /k ^
  "cd frontend ^&^& (if not exist node_modules npm install) ^&^& npm run dev"

echo.
echo ======================================================
echo   两个窗口已打开, 等待依赖安装与启动完成后:
echo   电脑访问:  http://localhost:5173
echo   手机访问:  http://[本机IP]:5173   (需与电脑同一 Wi-Fi)
echo   查本机IP: 命令行运行 ipconfig 看 IPv4 地址
echo   关闭对应窗口即可停止服务
echo ======================================================
echo.
pause
