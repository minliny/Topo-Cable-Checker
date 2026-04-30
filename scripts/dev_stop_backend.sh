#!/usr/bin/env bash
# ============================================================
# dev_stop_backend.sh
# TopoChecker — 停止后端开发服务器
# 用法：bash scripts/dev_stop_backend.sh
# ============================================================

RED='\033[0;31m'
GRN='\033[0;32m'
YLW='\033[0;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
HOST="127.0.0.1"
PORT="8000"

echo "══════════════════════════════════════════════════════"
echo "  TopoChecker 后端开发服务器停止"
echo "══════════════════════════════════════════════════════"
echo ""

# Try to read PID from file
PID_FILE="$BACKEND_DIR/dev_server.pid"
KILLED=0

if [ -f "$PID_FILE" ]; then
    SAVED_PID=$(cat "$PID_FILE")
    if [ -n "$SAVED_PID" ] && kill -0 "$SAVED_PID" 2>/dev/null; then
        echo "停止后端进程 (PID: $SAVED_PID)..."
        kill "$SAVED_PID" 2>/dev/null
        KILLED=1
    fi
    rm -f "$PID_FILE"
fi

# Also try to kill by port
if lsof -i :$PORT 2>/dev/null | grep -q "LISTEN"; then
    echo "停止占用端口 $PORT 的进程..."
    lsof -ti :$PORT | xargs kill 2>/dev/null
    KILLED=1
fi

# Also try to kill by process name pattern (only uvicorn from this project)
for pid in $(pgrep -f "uvicorn.*backend.main:app" 2>/dev/null); do
    if [ -n "$pid" ]; then
        echo "停止 uvicorn 进程 (PID: $pid)..."
        kill "$pid" 2>/dev/null
        KILLED=1
    fi
done

sleep 1

# Verify backend is stopped
if curl -s -f --max-time 1 "http://$HOST:$PORT/health" > /dev/null 2>&1; then
    echo ""
    echo -e "${RED}✗${NC} 后端仍在运行，尝试强制停止..."
    for pid in $(pgrep -f "uvicorn.*backend.main:app" 2>/dev/null); do
        if [ -n "$pid" ]; then
            kill -9 "$pid" 2>/dev/null
        fi
    done
    sleep 1
fi

# Final check
if curl -s -f --max-time 1 "http://$HOST:$PORT/health" > /dev/null 2>&1; then
    echo ""
    echo -e "${RED}✗${NC} 无法停止后端"
    echo ""
    exit 1
else
    echo ""
    echo -e "${GRN}✓${NC} 后端已停止"
    echo ""
    exit 0
fi
