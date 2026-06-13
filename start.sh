#!/usr/bin/env bash
# 一键启动脚本 (macOS / Linux)
# 同时拉起后端(FastAPI, 8000)和前端(Vite, 5173), 按 Ctrl+C 一起退出。
#
# 用法:
#   ./start.sh              使用真实行情(需联网)
#   ./start.sh --mock       使用演示数据(无需联网, 页面顶部会显示提示)
set -e
cd "$(dirname "$0")"

USE_MOCK=0
if [ "$1" = "--mock" ]; then USE_MOCK=1; fi

# ---------- 后端 ----------
cd backend
if [ ! -d ".venv" ]; then
  echo "[1/4] 创建 Python 虚拟环境..."
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
if [ ! -f ".venv/.deps_installed" ]; then
  echo "[2/4] 安装后端依赖(首次较慢)..."
  pip install -q -r requirements.txt && touch .venv/.deps_installed
fi
echo "[3/4] 启动后端 http://localhost:8000 ..."
USE_MOCK_DATA=$USE_MOCK python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# 退出时清理后端进程
cleanup() { echo; echo "正在停止服务..."; kill $BACKEND_PID 2>/dev/null || true; }
trap cleanup EXIT INT TERM

# ---------- 前端 ----------
cd frontend
if [ ! -d "node_modules" ]; then
  echo "[4/4] 安装前端依赖(首次较慢)..."
  npm install
fi

# 显示局域网地址, 方便手机访问
IP=$(ipconfig getifaddr en0 2>/dev/null || hostname -I 2>/dev/null | awk '{print $1}')
echo
echo "======================================================"
echo "  电脑访问:  http://localhost:5173"
[ -n "$IP" ] && echo "  手机访问:  http://$IP:5173   (需与电脑同一 Wi-Fi)"
echo "  按 Ctrl+C 停止全部服务"
echo "======================================================"
echo
npm run dev
