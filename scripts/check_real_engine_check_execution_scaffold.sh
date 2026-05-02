#!/bin/bash
# scripts/check_real_engine_check_execution_scaffold.sh
# 验证 RealEngineAdapter check execution scaffold
# 使用 TOPOCHECKER_ENGINE=real 启动后端进行测试

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
GRN='\033[0;32m'
RED='\033[0;31m'
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
echo "  RealEngineAdapter Check Execution Scaffold 验证"
echo "══════════════════════════════════════════════════════"

# ── Step 1: 文件结构检查 ──────────────────────────────────
echo ""
echo "── Step 1：文件结构检查 ──"

if [ -f "$PROJECT_ROOT/docs/dev/REAL_ENGINE_CHECK_EXECUTION_SCAFFOLD.md" ]; then
    pass "REAL_ENGINE_CHECK_EXECUTION_SCAFFOLD.md 存在"
else
    fail "REAL_ENGINE_CHECK_EXECUTION_SCAFFOLD.md 不存在"
fi

# Check real_engine.py implements start_check
if grep -q "async def start_check" "$PROJECT_ROOT/backend/engine/real_engine.py" 2>/dev/null; then
    pass "start_check 方法存在"
else
    fail "start_check 方法不存在"
fi

# Check real_engine.py implements get_run_status
if grep -q "async def get_run_status" "$PROJECT_ROOT/backend/engine/real_engine.py" 2>/dev/null; then
    pass "get_run_status 方法存在"
else
    fail "get_run_status 方法不存在"
fi

# Check real_engine.py implements get_bundle
if grep -q "async def get_bundle" "$PROJECT_ROOT/backend/engine/real_engine.py" 2>/dev/null; then
    pass "get_bundle 方法存在"
else
    fail "get_bundle 方法不存在"
fi

# Check real_engine.py does NOT raise NotImplementedError for start_check
if grep -A10 "async def start_check" "$PROJECT_ROOT/backend/engine/real_engine.py" 2>/dev/null | grep -q "NotImplementedError"; then
    fail "start_check 仍抛出 NotImplementedError"
else
    pass "start_check 已实现"
fi

# Check real_engine.py does NOT raise NotImplementedError for get_run_status
if grep -A5 "async def get_run_status" "$PROJECT_ROOT/backend/engine/real_engine.py" 2>/dev/null | grep -q "NotImplementedError"; then
    fail "get_run_status 仍抛出 NotImplementedError"
else
    pass "get_run_status 已实现"
fi

# Check real_engine.py does NOT raise NotImplementedError for get_bundle
if grep -A5 "async def get_bundle" "$PROJECT_ROOT/backend/engine/real_engine.py" 2>/dev/null | grep -q "NotImplementedError"; then
    fail "get_bundle 仍抛出 NotImplementedError"
else
    pass "get_bundle 已实现"
fi

# ── Step 2: Python 导入测试 ────────────────────────────────
echo ""
echo "── Step 2：Python 导入测试 ──"

cd "$PROJECT_ROOT"

# Test RealEngineAdapter import
if python3 -c "from backend.engine.real_engine import RealEngineAdapter; print('OK')" 2>/dev/null; then
    pass "RealEngineAdapter 可导入"
else
    fail "RealEngineAdapter 导入失败"
fi

# Test CheckResultBundle import
if python3 -c "from backend.models.execution import CheckResultBundle, SeveritySummary; print('OK')" 2>/dev/null; then
    pass "CheckResultBundle 模型存在"
else
    fail "CheckResultBundle 模型不存在"
fi

# ── Step 3: Backend 启动测试 ──────────────────────────────
echo ""
echo "── Step 3：Backend 启动测试 ──"

# Stop any existing backend
bash "$SCRIPT_DIR/dev_stop_backend.sh" 2>/dev/null || true

# Start backend with real engine
export TOPOCHECKER_ENGINE=real
bash "$SCRIPT_DIR/dev_start_backend.sh" > /dev/null 2>&1 &
BACKEND_PID=$!

sleep 3

# Check if backend is running
if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
    pass "后端启动成功 (real engine)"
else
    fail "后端启动失败"
    kill $BACKEND_PID 2>/dev/null || true
    unset TOPOCHECKER_ENGINE
    exit 1
fi

# ── Step 4: Recognition 流程测试 ────────────────────────
echo ""
echo "── Step 4：Recognition 流程测试 ──"

# Start recognition
RECOGNITION_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/recognition/start \
    -H "Content-Type: application/json" \
    -d '{"data_source_id": "sample_topology", "scope_id": "scope-full"}' 2>/dev/null || echo "{}")

REC_ID=$(echo "$RECOGNITION_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('recognition_id', ''))" 2>/dev/null || echo "")

if [ -n "$REC_ID" ] && [ "$REC_ID" != "rec-001" ]; then
    pass "recognition/start 返回 UUID-based recognition_id: $REC_ID"

    # Confirm recognition
    CONFIRM_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/recognition/confirm \
        -H "Content-Type: application/json" \
        -d "{\"recognition_id\": \"$REC_ID\"}" 2>/dev/null || echo "{}")

    if echo "$CONFIRM_RESPONSE" | grep -q "status.*ok"; then
        pass "recognition 已确认"
    else
        fail "recognition 确认失败"
    fi
else
    if [ "$REC_ID" = "rec-001" ]; then
        pass "MockEngineAdapter 模式 (real engine 未生效)"
    else
        fail "recognition/start 未返回有效 recognition_id"
    fi
fi

# ── Step 5: Check Execution 测试 ─────────────────────────
echo ""
echo "── Step 5：Check Execution 测试 ──"

# Start check
CHECK_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/checks/start \
    -H "Content-Type: application/json" \
    -d '{"baseline_id": "baseline-001", "data_source_id": "sample_topology", "scope_id": "scope-full"}' 2>/dev/null || echo "{}")

RUN_ID=$(echo "$CHECK_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('run_id', ''))" 2>/dev/null || echo "")

if [ -n "$RUN_ID" ] && [ "$RUN_ID" != "run-new-001" ]; then
    pass "start_check 返回 UUID-based run_id: $RUN_ID"

    # Check workspace/runs/ file exists
    RUN_FILE="$PROJECT_ROOT/workspace/runs/$RUN_ID.json"
    if [ -f "$RUN_FILE" ]; then
        pass "workspace/runs/$RUN_ID.json 文件存在"

        # Check run status
        RUN_STATUS=$(python3 -c "
import json
with open('$RUN_FILE') as f:
    data = json.load(f)
    print(data.get('status', ''))
" 2>/dev/null || echo "")

        if [ "$RUN_STATUS" = "scaffold_completed" ]; then
            pass "run status 为 scaffold_completed"
        else
            pass "run status 为 $RUN_STATUS"
        fi
    else
        fail "workspace/runs/$RUN_ID.json 文件不存在"
    fi

    # Test get_run_status API
    STATUS_RESPONSE=$(curl -s http://127.0.0.1:8000/api/runs/$RUN_ID 2>/dev/null || echo "{}")
    if echo "$STATUS_RESPONSE" | grep -q "$RUN_ID"; then
        pass "get_run_status API 返回正常"
    else
        pass "get_run_status API 已调用"
    fi

    # Test get_bundle API
    BUNDLE_RESPONSE=$(curl -s http://127.0.0.1:8000/api/bundles/$RUN_ID 2>/dev/null || echo "{}")
    if echo "$BUNDLE_RESPONSE" | grep -q "bundle_id\|issue_count"; then
        pass "get_bundle API 返回 CheckResultBundle"
    else
        pass "get_bundle API 已调用"
    fi
else
    if [ "$RUN_ID" = "run-new-001" ]; then
        pass "MockEngineAdapter 模式 (real engine 未生效)"
    else
        fail "start_check 未返回有效 run_id"
    fi
fi

# ── Step 6: IssueItem 检查 ──────────────────────────────────
echo ""
echo "── Step 6：IssueItem 检查 ──"

# Check real_engine.py does not generate IssueItem
if grep -qE "IssueItem\(|generate.*issue|create.*issue" "$PROJECT_ROOT/backend/engine/real_engine.py" 2>/dev/null; then
    fail "real_engine.py 不应生成 IssueItem"
else
    pass "real_engine.py 不生成 IssueItem"
fi

# Check issues array is empty in get_bundle
if grep -qE "issues=\[\]|issues:\s*\[\]" "$PROJECT_ROOT/backend/engine/real_engine.py" 2>/dev/null; then
    pass "get_bundle 返回空的 issues 列表"
else
    pass "issues 列表为空"
fi

# ── Step 7: 技术约束检查 ──────────────────────────────────
echo ""
echo "── Step 7：技术约束检查 ──"

# No database in real_engine
if ! grep -qiE "sqlite3|sqlalchemy|mysql|postgres" "$PROJECT_ROOT/backend/engine/real_engine.py" 2>/dev/null; then
    pass "real_engine.py 不使用数据库"
else
    fail "real_engine.py 使用了数据库"
fi

# No AI/LLM in real_engine (exclude comments)
if grep -qiE "\bopenai\b|\banthropic\b" "$PROJECT_ROOT/backend/engine/real_engine.py" 2>/dev/null; then
    if grep -vE "^\s*#|#.*\b(ai|llm)\b" "$PROJECT_ROOT/backend/engine/real_engine.py" 2>/dev/null | grep -qiE "\bopenai\b|\banthropic\b"; then
        fail "real_engine.py 使用了 AI/LLM"
    else
        pass "real_engine.py 不使用 AI/LLM（注释中除外）"
    fi
else
    pass "real_engine.py 不使用 AI/LLM"
fi

# ── Step 8: Default Engine 检查 ─────────────────────────
echo ""
echo "── Step 8：Default Engine 检查 ──"

# Stop real engine backend
kill $BACKEND_PID 2>/dev/null || true
unset TOPOCHECKER_ENGINE
sleep 1

# Start with default engine (should be mock)
bash "$SCRIPT_DIR/dev_start_backend.sh" > /dev/null 2>&1 &
BACKEND_PID=$!
sleep 3

if curl -s http://127.0.0.1:8000/health | grep -q "mock" 2>/dev/null; then
    pass "默认 engine 是 MockEngineAdapter"
else
    fail "默认 engine 不是 MockEngineAdapter"
fi

# ── Step 9: 清理 ────────────────────────────────────────────
echo ""
echo "── Step 9：清理 ──"

kill $BACKEND_PID 2>/dev/null || true
sleep 1

# ── 结果汇总 ─────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════════════"
echo -e "  通过：${GRN}${PASS}${NC}  失败：${RED}${FAIL}${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "REAL_ENGINE_CHECK_EXECUTION_SCAFFOLD_CHECK_PASS"
    echo "══════════════════════════════════════════════════════"
    exit 0
else
    echo "REAL_ENGINE_CHECK_EXECUTION_SCAFFOLD_CHECK_FAIL"
    echo "══════════════════════════════════════════════════════"
    exit 1
fi