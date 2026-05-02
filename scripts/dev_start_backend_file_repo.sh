#!/usr/bin/env bash
# ============================================================
# dev_start_backend_file_repo.sh
# TopoChecker — 使用 FileRepository 模式启动后端开发服务器
# 用法：bash scripts/dev_start_backend_file_repo.sh
# ============================================================

RED='\033[0;31m'
GRN='\033[0;32m'
YLW='\033[0;33m'
BLU='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
HOST="127.0.0.1"
PORT="8000"
LOG_FILE="$BACKEND_DIR/dev_server_file_repo.log"
PID_FILE="$BACKEND_DIR/dev_server_file_repo.pid"

echo "══════════════════════════════════════════════════════"
echo "  TopoChecker 后端开发服务器启动 (FileRepository 模式)"
echo "══════════════════════════════════════════════════════"
echo ""

# Check if backend is already running
if curl -s -f --max-time 1 "http://$HOST:$PORT/health" > /dev/null 2>&1; then
    echo -e "${YLW}⚠${NC} 后端已在运行: http://$HOST:$PORT"
    echo ""
    echo "使用以下命令停止后端："
    echo "  bash scripts/dev_stop_backend.sh"
    echo ""
    exit 0
fi

# Check Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗${NC} 未找到 python3"
    echo ""
    echo "请先安装 Python 3.9+"
    echo ""
    exit 1
fi

# Check if port is already in use
if lsof -i :$PORT &> /dev/null; then
    echo -e "${YLW}⚠${NC} 端口 $PORT 已被占用"
    echo ""
    echo "请先停止占用端口的进程或使用："
    echo "  bash scripts/dev_stop_backend.sh"
    echo ""
    exit 1
fi

# Ensure workspace fixtures exist
if [ ! -d "$PROJECT_ROOT/workspace/inputs" ]; then
    echo -e "${YLW}⚠${NC} workspace fixtures 不存在，先运行导出脚本..."
    bash "$PROJECT_ROOT/scripts/export_mock_to_workspace.sh"
    echo ""
fi

# Force mock engine (safe for local dev)
# Real engine scaffold is for dedicated testing only
unset TOPOCHECKER_ENGINE
export TOPOCHECKER_ENGINE=mock

# Start backend with FileRepository
export TOPOCHECKER_REPO=file

echo -e "${BLU}ℹ${NC} Repository 模式: FileRepository (TOPOCHECKER_REPO=file)"
echo "启动后端服务器..."
echo "  目录: $PROJECT_ROOT"
echo "  主机: $HOST"
echo "  端口: $PORT"
echo "  日志: $LOG_FILE"
echo ""

cd "$PROJECT_ROOT"
nohup python3 -m uvicorn backend.main:app --host "$HOST" --port "$PORT" --app-dir "$PROJECT_ROOT" > "$LOG_FILE" 2>&1 &
BACKEND_PID=$!

echo "后端 PID: $BACKEND_PID"
echo "$BACKEND_PID" > "$PID_FILE"

# Wait for backend to start
echo ""
echo "等待后端启动..."
for i in {1..10}; do
    if curl -s -f --max-time 1 "http://$HOST:$PORT/health" > /dev/null 2>&1; then
        echo ""
        echo -e "${GRN}✓${NC} 后端启动成功: http://$HOST:$PORT"
        echo ""
        echo "后端日志: $LOG_FILE"
        echo ""
        echo "使用以下命令停止后端："
        echo "  bash scripts/dev_stop_backend.sh"
        echo ""
        exit 0
    fi
    sleep 1
done

echo ""
echo -e "${RED}✗${NC} 后端启动失败"
echo ""
echo "请检查日志: $LOG_FILE"
echo ""
exit 1
