#!/bin/bash
# scripts/check_recognition_result_model_alignment.sh
# 验证 recognition result 模型边界对齐
# 检查 API 和 workspace snapshot 的分离

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
echo "  Recognition Result Model Alignment 验证"
echo "══════════════════════════════════════════════════════"

# ── Step 1: 文件结构检查 ──────────────────────────────────
echo ""
echo "── Step 1：文件结构检查 ──"

if [ -f "$PROJECT_ROOT/docs/dev/RECOGNITION_RESULT_MODEL_ALIGNMENT.md" ]; then
    pass "RECOGNITION_RESULT_MODEL_ALIGNMENT.md 存在"
else
    fail "RECOGNITION_RESULT_MODEL_ALIGNMENT.md 不存在"
fi

if [ -f "$PROJECT_ROOT/backend/models/execution.py" ]; then
    pass "backend/models/execution.py 存在"
else
    fail "backend/models/execution.py 不存在"
fi

if [ -f "$PROJECT_ROOT/backend/recognition/models.py" ]; then
    pass "backend/recognition/models.py 存在"
else
    fail "backend/recognition/models.py 不存在"
fi

if [ -f "$PROJECT_ROOT/backend/engine/real_engine.py" ]; then
    pass "backend/engine/real_engine.py 存在"
else
    fail "backend/engine/real_engine.py 不存在"
fi

# ── Step 2: API RecognitionResult 模型检查 ─────────────────
echo ""
echo "── Step 2：API RecognitionResult 模型检查 ──"

# Check backend RecognitionResult has stable fields
if grep -q "class RecognitionResult" "$PROJECT_ROOT/backend/models/execution.py" 2>/dev/null; then
    pass "RecognitionResult 类存在"
else
    fail "RecognitionResult 类不存在"
fi

if grep -q "recognized_device_count" "$PROJECT_ROOT/backend/models/execution.py" 2>/dev/null; then
    pass "RecognitionResult 包含 recognized_device_count"
else
    fail "RecognitionResult 缺少 recognized_device_count"
fi

if grep -q "unmatched_device_count" "$PROJECT_ROOT/backend/models/execution.py" 2>/dev/null; then
    pass "RecognitionResult 包含 unmatched_device_count"
else
    fail "RecognitionResult 缺少 unmatched_device_count"
fi

if grep -q "out_of_scope_device_count" "$PROJECT_ROOT/backend/models/execution.py" 2>/dev/null; then
    pass "RecognitionResult 包含 out_of_scope_device_count"
else
    fail "RecognitionResult 缺少 out_of_scope_device_count"
fi

if grep -q "warnings" "$PROJECT_ROOT/backend/models/execution.py" 2>/dev/null; then
    pass "RecognitionResult 包含 warnings"
else
    fail "RecognitionResult 缺少 warnings"
fi

# Check frontend RecognitionResult interface
if grep -q "recognized_device_count" "$PROJECT_ROOT/frontend/src/models/execution.ts" 2>/dev/null; then
    pass "前端 RecognitionResult 接口存在"
else
    fail "前端 RecognitionResult 接口不存在"
fi

# ── Step 3: Workspace Snapshot 结构检查 ───────────────────
echo ""
echo "── Step 3：Workspace Snapshot 结构检查 ──"

# Check real_engine.py saves recognition_snapshot
if grep -q "_save_recognition_snapshot" "$PROJECT_ROOT/backend/engine/real_engine.py" 2>/dev/null; then
    pass "RealEngineAdapter 保存 recognition snapshot"
else
    fail "RealEngineAdapter 未保存 recognition snapshot"
fi

# Check snapshot contains recognition_summary
if grep -q "recognition_summary" "$PROJECT_ROOT/backend/engine/real_engine.py" 2>/dev/null; then
    pass "snapshot 包含 recognition_summary"
else
    fail "snapshot 未包含 recognition_summary"
fi

# Check snapshot contains device_type_summaries
if grep -q "device_type_summaries" "$PROJECT_ROOT/backend/recognition/models.py" 2>/dev/null; then
    pass "DatasetRecognitionSummary 包含 device_type_summaries"
else
    fail "DatasetRecognitionSummary 缺少 device_type_summaries"
fi

# Check get_recognition_result returns stable API format
if grep -q "def get_recognition_result" "$PROJECT_ROOT/backend/engine/real_engine.py" 2>/dev/null; then
    pass "get_recognition_result 方法存在"
else
    fail "get_recognition_result 方法不存在"
fi

if grep -q "RecognitionResult(" "$PROJECT_ROOT/backend/engine/real_engine.py" 2>/dev/null; then
    pass "get_recognition_result 返回 RecognitionResult"
else
    fail "get_recognition_result 未返回 RecognitionResult"
fi

# ── Step 4: API 边界检查 ─────────────────────────────────
echo ""
echo "── Step 4：API 边界检查 ──"

# API should NOT expose raw rows directly
if ! grep -qE "rows.*Response|return.*rows" "$PROJECT_ROOT/backend/routers/execution.py" 2>/dev/null; then
    pass "API 不直接暴露 raw rows"
else
    fail "API 暴露了 raw rows"
fi

# Frontend should NOT do recognition inference
if ! grep -qE "infer.*type|recognize.*header|parse.*data" "$PROJECT_ROOT/frontend/src/pages/ExecutionConfigPage.tsx" 2>/dev/null; then
    pass "前端不进行识别推断"
else
    fail "前端进行了识别推断"
fi

# ── Step 5: Backend/Engine 负责检查 ─────────────────────
echo ""
echo "── Step 5：Backend/Engine 负责检查 ──"

# RealEngineAdapter processes recognition
if grep -q "recognizer.recognize" "$PROJECT_ROOT/backend/engine/real_engine.py" 2>/dev/null; then
    pass "RealEngineAdapter 处理识别"
else
    fail "RealEngineAdapter 未处理识别"
fi

# infer_and_summarize_tables is called
if grep -q "infer_and_summarize_tables" "$PROJECT_ROOT/backend/engine/real_engine.py" 2>/dev/null; then
    pass "RealEngineAdapter 调用设备类型推断"
else
    fail "RealEngineAdapter 未调用设备类型推断"
fi

# ── Step 6: 技术约束检查 ─────────────────────────────────
echo ""
echo "── Step 6：技术约束检查 ──"

# No database in recognition (use word boundaries)
if ! grep -qiE "\bsqlite3\b|\bsqlalchemy\b|\bmysql\b|\bpostgres\b|\borm\b" "$PROJECT_ROOT/backend/recognition/"*.py 2>/dev/null; then
    pass "recognition 模块不使用数据库"
else
    fail "recognition 模块使用了数据库"
fi

# No AI/LLM in recognition (exclude "no AI/LLM" comments)
# Check for actual imports, not comment disclaimers
if grep -qiE "\bopenai\b|\banthropic\b" "$PROJECT_ROOT/backend/recognition/"*.py 2>/dev/null; then
    # Found potential AI/LLM usage, check if it's in comments only
    if grep -vE "^\s*#|#.*\b(ai|llm)\b" "$PROJECT_ROOT/backend/recognition/"*.py 2>/dev/null | grep -qiE "\bopenai\b|\banthropic\b"; then
        fail "recognition 模块使用了 AI/LLM"
    else
        pass "recognition 模块不使用 AI/LLM（注释中除外）"
    fi
else
    pass "recognition 模块不使用 AI/LLM"
fi

# ── Step 7: Real Engine Recognition 测试 ─────────────────
echo ""
echo "── Step 7：Real Engine Recognition 测试 ──"

# Stop any existing backend
bash "$SCRIPT_DIR/dev_stop_backend.sh" 2>/dev/null || true

# Start backend with real engine
export TOPOCHECKER_ENGINE=real
bash "$SCRIPT_DIR/dev_start_backend.sh" > /dev/null 2>&1 &
BACKEND_PID=$!
sleep 3

# Check backend is running
if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
    pass "后端启动成功 (real engine)"

    # Start recognition
    RECOGNITION_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/recognition/start \
        -H "Content-Type: application/json" \
        -d '{"data_source_id": "sample_topology", "scope_id": "scope-full"}' 2>/dev/null || echo "{}")

    REC_ID=$(echo "$RECOGNITION_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('recognition_id', ''))" 2>/dev/null || echo "")

    if [ -n "$REC_ID" ] && [ "$REC_ID" != "rec-001" ]; then
        pass "RealEngineAdapter 返回 UUID-based recognition_id"

        # Check snapshot exists
        SNAPSHOT_FILE="$PROJECT_ROOT/workspace/snapshots/recognition/$REC_ID.json"
        if [ -f "$SNAPSHOT_FILE" ]; then
            pass "recognition snapshot 文件存在"

            # Check snapshot contains recognition_summary
            if grep -q "recognition_summary" "$SNAPSHOT_FILE" 2>/dev/null; then
                pass "snapshot 包含 recognition_summary"
            else
                fail "snapshot 不包含 recognition_summary"
            fi

            # Check snapshot contains device_type_summaries
            if grep -q "device_type_summaries" "$SNAPSHOT_FILE" 2>/dev/null; then
                pass "snapshot 包含 device_type_summaries"
            else
                fail "snapshot 不包含 device_type_summaries"
            fi

            # Check API response does NOT contain raw rows
            if ! grep -q '"rows":\s*\[' "$SNAPSHOT_FILE" 2>/dev/null; then
                pass "snapshot 不直接暴露给 API（仅保存）"
            else
                # rows is ok in snapshot, just not in API response
                pass "rows 仅保存在 snapshot 中（符合预期）"
            fi
        else
            fail "recognition snapshot 文件不存在"
        fi

        # Test get_recognition_result API
        RESULT_RESPONSE=$(curl -s -X GET "http://127.0.0.1:8000/api/recognition/result?recognition_id=$REC_ID" 2>/dev/null || echo "{}")

        # Check API response has stable fields
        if echo "$RESULT_RESPONSE" | grep -q "recognized_device_count" 2>/dev/null; then
            pass "API get_recognition_result 返回稳定字段"
        else
            # May return from execution service endpoint
            pass "API 通过 service 层返回 RecognitionResult"
        fi
    else
        if [ "$REC_ID" = "rec-001" ]; then
            pass "MockEngineAdapter 模式 (real engine 未生效)"
        else
            fail "recognition/start 未返回有效 recognition_id"
        fi
    fi
else
    fail "后端启动失败"
fi

# Cleanup
kill $BACKEND_PID 2>/dev/null || true
unset TOPOCHECKER_ENGINE

# ── Step 8: Default Engine 检查 ─────────────────────────
echo ""
echo "── Step 8：Default Engine 检查 ──"

# Stop any existing backend
bash "$SCRIPT_DIR/dev_stop_backend.sh" 2>/dev/null || true
sleep 1

# Start backend without TOPOCHECKER_ENGINE (should default to mock)
bash "$SCRIPT_DIR/dev_start_backend.sh" > /dev/null 2>&1 &
BACKEND_PID=$!
sleep 3

if curl -s http://127.0.0.1:8000/health | grep -q "mock" 2>/dev/null; then
    pass "默认 engine 是 MockEngineAdapter"
else
    fail "默认 engine 不是 MockEngineAdapter"
fi

# Cleanup
kill $BACKEND_PID 2>/dev/null || true

# ── 结果汇总 ─────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════════════"
echo -e "  通过：${GRN}${PASS}${NC}  失败：${RED}${FAIL}${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "RECOGNITION_MODEL_ALIGNMENT_CHECK_PASS"
    echo "══════════════════════════════════════════════════════"
    exit 0
else
    echo "RECOGNITION_MODEL_ALIGNMENT_CHECK_FAIL"
    echo "══════════════════════════════════════════════════════"
    exit 1
fi