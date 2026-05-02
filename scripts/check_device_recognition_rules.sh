#!/bin/bash
# scripts/check_device_recognition_rules.sh
# 验证设备识别规则 scaffold
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
echo "  Device Recognition Rules Scaffold 验证"
echo "══════════════════════════════════════════════════════"

# ── Step 1: 文件结构检查 ──────────────────────────────────
echo ""
echo "── Step 1：文件结构检查 ──"

if [ -d "$PROJECT_ROOT/backend/recognition" ]; then
    pass "backend/recognition/ 目录存在"
else
    fail "backend/recognition/ 目录不存在"
fi

if [ -f "$PROJECT_ROOT/backend/recognition/models.py" ]; then
    pass "recognition/models.py 存在"
else
    fail "recognition/models.py 不存在"
fi

if [ -f "$PROJECT_ROOT/backend/recognition/recognizer.py" ]; then
    pass "recognition/recognizer.py 存在"
else
    fail "recognition/recognizer.py 不存在"
fi

# Check DatasetRecognizer class
if grep -q "class DatasetRecognizer" "$PROJECT_ROOT/backend/recognition/recognizer.py" 2>/dev/null; then
    pass "DatasetRecognizer 类存在"
else
    fail "DatasetRecognizer 类不存在"
fi

# Check RecognizedTableKind enum
if grep -q "class RecognizedTableKind" "$PROJECT_ROOT/backend/recognition/models.py" 2>/dev/null; then
    pass "RecognizedTableKind 枚举存在"
else
    fail "RecognizedTableKind 枚举不存在"
fi

# Check DatasetRecognitionSummary
if grep -q "class DatasetRecognitionSummary" "$PROJECT_ROOT/backend/recognition/models.py" 2>/dev/null; then
    pass "DatasetRecognitionSummary 模型存在"
else
    fail "DatasetRecognitionSummary 模型不存在"
fi

# ── Step 2: 关键词检查 ────────────────────────────────────
echo ""
echo "── Step 2：识别关键词检查 ──"

# Check device keywords
if grep -q "device_name\|DEVICE_KEYWORDS" "$PROJECT_ROOT/backend/recognition/recognizer.py" 2>/dev/null; then
    pass "设备表关键词已定义"
else
    fail "设备表关键词未定义"
fi

# Check link keywords
if grep -q "link_name\|LINK_KEYWORDS" "$PROJECT_ROOT/backend/recognition/recognizer.py" 2>/dev/null; then
    pass "链路表关键词已定义"
else
    fail "链路表关键词未定义"
fi

# ── Step 3: RealEngineAdapter 集成检查 ──────────────────
echo ""
echo "── Step 3：RealEngineAdapter 集成检查 ──"

if grep -q "from ..recognition import DatasetRecognizer" "$PROJECT_ROOT/backend/engine/real_engine.py" 2>/dev/null; then
    pass "RealEngineAdapter 导入 DatasetRecognizer"
else
    fail "RealEngineAdapter 未导入 DatasetRecognizer"
fi

if grep -q "self.recognizer = DatasetRecognizer" "$PROJECT_ROOT/backend/engine/real_engine.py" 2>/dev/null; then
    pass "RealEngineAdapter 实例化 DatasetRecognizer"
else
    fail "RealEngineAdapter 未实例化 DatasetRecognizer"
fi

if grep -q "self.recognizer.recognize" "$PROJECT_ROOT/backend/engine/real_engine.py" 2>/dev/null; then
    pass "RealEngineAdapter 调用 recognizer.recognize"
else
    fail "RealEngineAdapter 未调用 recognizer.recognize"
fi

# ── Step 4: Python 导入测试 ────────────────────────────────
echo ""
echo "── Step 4：Python 导入测试 ──"

cd "$PROJECT_ROOT"

# Test recognition module import
if python3 -c "from backend.recognition import DatasetRecognizer, DatasetRecognitionSummary; print('OK')" 2>/dev/null; then
    pass "recognition 模块可导入"
else
    fail "recognition 模块导入失败"
fi

# Test RealEngineAdapter with recognition
if python3 -c "
import os
os.environ['TOPOCHECKER_ENGINE'] = 'real'
from backend.engine import RealEngineAdapter
adapter = RealEngineAdapter()
print(type(adapter.recognizer).__name__)
" 2>/dev/null | grep -q "DatasetRecognizer"; then
    pass "RealEngineAdapter 集成 DatasetRecognizer 成功"
else
    fail "RealEngineAdapter 集成 DatasetRecognizer 失败"
fi

# ── Step 5: Backend 启动测试 ──────────────────────────────
echo ""
echo "── Step 5：Backend 启动测试 ──"

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
fi

# ── Step 6: Recognition API 测试 ──────────────────────────
echo ""
echo "── Step 6：Recognition API 测试 ──"

# Start recognition
RECOGNITION_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/recognition/start \
    -H "Content-Type: application/json" \
    -d '{"data_source_id": "sample_topology", "scope_id": "scope-full"}' 2>/dev/null || echo "{}")

REC_ID=$(echo "$RECOGNITION_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('recognition_id', ''))" 2>/dev/null || echo "")

if [ -n "$REC_ID" ]; then
    pass "recognition/start 返回 recognition_id"

    # Check recognition snapshot contains summary
    SNAPSHOT_FILE="$PROJECT_ROOT/workspace/snapshots/recognition/$REC_ID.json"
    if [ -f "$SNAPSHOT_FILE" ]; then
        if grep -q "recognition_summary" "$SNAPSHOT_FILE" 2>/dev/null; then
            pass "recognition snapshot 包含 recognition_summary"

            # Check if device tables recognized
            DEVICE_COUNT=$(python3 -c "
import json
with open('$SNAPSHOT_FILE') as f:
    data = json.load(f)
    summary = data.get('recognition_summary', {})
    print(summary.get('total_device_count', 0))
" 2>/dev/null || echo "0")

            if [ "$DEVICE_COUNT" -gt 0 ]; then
                pass "识别到 $DEVICE_COUNT 个设备"
            else
                fail "未识别到设备"
            fi
        else
            fail "recognition snapshot 缺少 recognition_summary"
        fi
    else
        fail "recognition snapshot 文件不存在"
    fi
else
    fail "recognition/start 未返回 recognition_id"
fi

# ── Step 7: 清理 ────────────────────────────────────────────
echo ""
echo "── Step 7：清理 ──"

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
    echo "DEVICE_RECOGNITION_RULES_CHECK_PASS"
    echo "══════════════════════════════════════════════════════"
    exit 0
else
    echo "DEVICE_RECOGNITION_RULES_CHECK_FAIL"
    echo "══════════════════════════════════════════════════════"
    exit 1
fi
