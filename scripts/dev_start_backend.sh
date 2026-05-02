#!/usr/bin/env bash
# ============================================================
# dev_start_backend.sh
# TopoChecker — 启动后端开发服务器（默认 FileRepository 模式）
# 使用本地 workspace JSON 文件，不接真实数据库或检查引擎
# 用法：bash scripts/dev_start_backend.sh
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
LOG_FILE="$BACKEND_DIR/dev_server.log"

echo "══════════════════════════════════════════════════════"
echo "  TopoChecker 后端开发服务器启动"
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

# Default to mock engine if TOPOCHECKER_ENGINE is not already set
# This ensures dev_start_backend.sh defaults to safe MockEngineAdapter
# while preserving explicit TOPOCHECKER_ENGINE=real when set externally
if [ -z "$TOPOCHECKER_ENGINE" ]; then
    export TOPOCHECKER_ENGINE=mock
fi

# Detect repository mode from environment
REPO_MODE="${TOPOCHECKER_REPO:-file}"
if [ "$REPO_MODE" = "mock" ]; then
    echo -e "${BLU}ℹ${NC} Repository 模式: MockRepository (显式回退)"
else
    echo -e "${BLU}ℹ${NC} Repository 模式: FileRepository (默认)"
fi
echo "启动后端服务器..."
echo "  目录: $PROJECT_ROOT"
echo "  主机: $HOST"
echo "  端口: $PORT"
echo "  日志: $LOG_FILE"
echo ""

cd "$PROJECT_ROOT"
export TOPOCHECKER_REPO="$REPO_MODE"
nohup python3 -m uvicorn backend.main:app --host "$HOST" --port "$PORT" --app-dir "$PROJECT_ROOT" > "$LOG_FILE" 2>&1 &
BACKEND_PID=$!

echo "后端 PID: $BACKEND_PID"
echo "$BACKEND_PID" > "$BACKEND_DIR/dev_server.pid"

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
