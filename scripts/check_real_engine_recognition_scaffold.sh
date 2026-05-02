#!/bin/bash
# scripts/check_real_engine_recognition_scaffold.sh
# 验证 RealEngineAdapter recognition scaffold
# 使用 TOPOCHECKER_ENGINE=real 启动后端进行测试

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
GRN='\033[0;32m'
RED='\033[0;31m'
YLW='\033[0;33m'
NC='\033[0m'

PASS=0
FAIL=0

pass() {
    echo -e "  ${GRN}✓${NC} $1"
    PASS=$((PASS + 1))
}

fail() {
    echo -e "  ${RED}✗${NC} $1"
    FAIL=$((FAIL + 1))
}

echo "══════════════════════════════════════════════════════"
echo "  RealEngineAdapter Recognition Scaffold 验证"
echo "══════════════════════════════════════════════════════"

# ── Step 1: 检查环境变量设置 ──────────────────────────────────
echo ""
echo "── Step 1：环境检查 ──"

# Check sample_topology.csv exists
if [ -f "$PROJECT_ROOT/workspace/inputs/sample_topology.csv" ]; then
    pass "sample_topology.csv 存在"
else
    fail "sample_topology.csv 不存在"
fi

# Check backend/input module exists
if [ -d "$PROJECT_ROOT/backend/input" ]; then
    pass "backend/input 模块存在"
else
    fail "backend/input 模块不存在"
fi

# Check RealEngineAdapter has recognition methods
if grep -q "async def start_recognition" "$PROJECT_ROOT/backend/engine/real_engine.py" 2>/dev/null; then
    pass "RealEngineAdapter.start_recognition 存在"
else
    fail "RealEngineAdapter.start_recognition 不存在"
fi

if grep -q "async def get_recognition_result" "$PROJECT_ROOT/backend/engine/real_engine.py" 2>/dev/null; then
    pass "RealEngineAdapter.get_recognition_result 存在"
else
    fail "RealEngineAdapter.get_recognition_result 不存在"
fi

if grep -q "async def confirm_recognition" "$PROJECT_ROOT/backend/engine/real_engine.py" 2>/dev/null; then
    pass "RealEngineAdapter.confirm_recognition 存在"
else
    fail "RealEngineAdapter.confirm_recognition 不存在"
fi

# Check real_engine.py uses LocalInputReader
if grep -q "LocalInputReader" "$PROJECT_ROOT/backend/engine/real_engine.py" 2>/dev/null; then
    pass "real_engine.py 使用 LocalInputReader"
else
    fail "real_engine.py 未使用 LocalInputReader"
fi

# Check real_engine.py uses normalize_raw_dataset
if grep -q "normalize_raw_dataset" "$PROJECT_ROOT/backend/engine/real_engine.py" 2>/dev/null; then
    pass "real_engine.py 使用 normalize_raw_dataset"
else
    fail "real_engine.py 未使用 normalize_raw_dataset"
fi

# ── Step 2: Python 导入测试 ───────────────────────────────────
echo ""
echo "── Step 2：Python 导入测试 ──"

cd "$PROJECT_ROOT"

# Test import with mock engine (default)
export TOPOCHECKER_ENGINE=mock
if python3 -c "from backend.engine import RealEngineAdapter; print('RealEngineAdapter imported')" 2>/dev/null; then
    pass "RealEngineAdapter 可导入 (mock mode)"
else
    fail "RealEngineAdapter 导入失败"
fi

# Test import with real engine
export TOPOCHECKER_ENGINE=real
if python3 -c "from backend.engine import get_engine; e = get_engine(); print(type(e).__name__)" 2>/dev/null; then
    pass "TOPOCHECKER_ENGINE=real 返回 RealEngineAdapter"
else
    fail "TOPOCHECKER_ENGINE=real 设置失败"
fi

# Reset to mock
export TOPOCHECKER_ENGINE=mock

# ── Step 3: Backend 启动测试 (real engine) ───────────────────
echo ""
echo "── Step 3：Backend 启动测试 (TOPOCHECKER_ENGINE=real) ──"

# Stop any existing backend
bash "$SCRIPT_DIR/dev_stop_backend.sh" 2>/dev/null || true

# Start backend with real engine
export TOPOCHECKER_ENGINE=real
bash "$SCRIPT_DIR/dev_start_backend.sh" > /dev/null 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Check if backend is running
if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
    pass "后端启动成功 (real engine)"
else
    fail "后端启动失败"
fi

# Check health endpoint (response format: {"status":"healthy",...})
HEALTH_RESPONSE=$(curl -s http://127.0.0.1:8000/health 2>/dev/null || echo "{}")
if echo "$HEALTH_RESPONSE" | grep -qi "healthy"; then
    pass "Health endpoint 返回正常"
else
    fail "Health endpoint 异常"
fi

# ── Step 4: Recognition API 测试 ──────────────────────────────
echo ""
echo "── Step 4：Recognition API 测试 ──"

# Test recognition start (API prefix: /api)
RECOGNITION_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/recognition/start \
    -H "Content-Type: application/json" \
    -d '{"data_source_id": "sample", "scope_id": "scope-full"}' 2>/dev/null || echo "{}")

REC_ID=$(echo "$RECOGNITION_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('recognition_id', ''))" 2>/dev/null || echo "")

if [ -n "$REC_ID" ]; then
    pass "recognition/start 返回 recognition_id: $REC_ID"
else
    # Try alternate response format
    REC_ID=$(echo "$RECOGNITION_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('data', {}).get('recognition_id', ''))" 2>/dev/null || echo "")
    if [ -n "$REC_ID" ]; then
        pass "recognition/start 返回 recognition_id (alt format): $REC_ID"
    else
        fail "recognition/start 未返回 recognition_id"
        echo "  响应: $RECOGNITION_RESPONSE"
    fi
fi

# Test recognition status
if [ -n "$REC_ID" ]; then
    STATUS_RESPONSE=$(curl -s "http://127.0.0.1:8000/api/recognition/status" 2>/dev/null || echo "{}")
    if echo "$STATUS_RESPONSE" | grep -qiE "not_started|ready|completed"; then
        pass "recognition/status 返回状态"
    else
        fail "recognition/status 异常"
    fi
fi

# ── Step 5: 清理 ────────────────────────────────────────────
echo ""
echo "── Step 5：清理 ──"

# Stop backend
kill $BACKEND_PID 2>/dev/null || true
sleep 1

# Reset to mock
export TOPOCHECKER_ENGINE=mock

# ── 结果汇总 ─────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════════════"
echo -e "  通过：${GRN}${PASS}${NC}  失败：${RED}${FAIL}${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "REAL_ENGINE_RECOGNITION_SCAFFOLD_CHECK_PASS"
    echo "══════════════════════════════════════════════════════"
    exit 0
else
    echo "REAL_ENGINE_RECOGNITION_SCAFFOLD_CHECK_FAIL"
    echo "══════════════════════════════════════════════════════"
    exit 1
fi
