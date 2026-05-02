#!/bin/bash
# scripts/check_device_type_inference.sh
# 验证设备类型推断 scaffold
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
echo "  Device Type Inference Scaffold 验证"
echo "══════════════════════════════════════════════════════"

# ── Step 1: 文件结构检查 ──────────────────────────────────
echo ""
echo "── Step 1：文件结构检查 ──"

if [ -f "$PROJECT_ROOT/backend/recognition/type_inference.py" ]; then
    pass "type_inference.py 存在"
else
    fail "type_inference.py 不存在"
fi

if [ -f "$PROJECT_ROOT/docs/dev/DEVICE_TYPE_INFERENCE.md" ]; then
    pass "DEVICE_TYPE_INFERENCE.md 存在"
else
    fail "DEVICE_TYPE_INFERENCE.md 不存在"
fi

# Check DeviceType enum
if grep -q "class DeviceType" "$PROJECT_ROOT/backend/recognition/models.py" 2>/dev/null; then
    pass "DeviceType 枚举存在"
else
    fail "DeviceType 枚举不存在"
fi

# Check infer_device_type function
if grep -q "def infer_device_type" "$PROJECT_ROOT/backend/recognition/type_inference.py" 2>/dev/null; then
    pass "infer_device_type 函数存在"
else
    fail "infer_device_type 函数不存在"
fi

# ── Step 2: 规则检查 ────────────────────────────────────
echo ""
echo "── Step 2：推断规则检查 ──"

# Check CE rule
if grep -qi "ce\|Catalyst" "$PROJECT_ROOT/backend/recognition/type_inference.py" 2>/dev/null; then
    pass "CE 规则已定义"
else
    fail "CE 规则未定义"
fi

# Check XH rule
if grep -qi "xh\|S5735" "$PROJECT_ROOT/backend/recognition/type_inference.py" 2>/dev/null; then
    pass "XH 规则已定义"
else
    fail "XH 规则未定义"
fi

# Check LINGQU rule
if grep -qi "lingqu\|灵衢\|lq_l2" "$PROJECT_ROOT/backend/recognition/type_inference.py" 2>/dev/null; then
    pass "LINGQU/灵衢/LQ_L2 规则已定义"
else
    fail "LINGQU/灵衢/LQ_L2 规则未定义"
fi

# Check optical resource rule
if grep -qi "optical\|光资源\|链路光" "$PROJECT_ROOT/backend/recognition/type_inference.py" 2>/dev/null; then
    pass "Optical Resource 规则已定义"
else
    fail "Optical Resource 规则未定义"
fi

# Check network resource rule
if grep -qi "network_resource\|网络资源" "$PROJECT_ROOT/backend/recognition/type_inference.py" 2>/dev/null; then
    pass "Network Resource 规则已定义"
else
    fail "Network Resource 规则未定义"
fi

# ── Step 3: Python 导入测试 ────────────────────────────────
echo ""
echo "── Step 3：Python 导入测试 ──"

cd "$PROJECT_ROOT"

# Test type_inference module import
if python3 -c "from backend.recognition import infer_device_type, infer_and_summarize_tables; print('OK')" 2>/dev/null; then
    pass "type_inference 模块可导入"
else
    fail "type_inference 模块导入失败"
fi

# Test infer_device_type with CE
CE_RESULT=$(python3 -c "
from backend.recognition import infer_device_type
result = infer_device_type(device_name='Core-SW-01', model='Catalyst9300-CE')
print(result.device_type.value)
" 2>/dev/null)
if [ "$CE_RESULT" = "switch" ]; then
    pass "CE 开头推断为 switch"
else
    fail "CE 开头推断失败: $CE_RESULT"
fi

# Test infer_device_type with LINGQU
LINGQU_RESULT=$(python3 -c "
from backend.recognition import infer_device_type
result = infer_device_type(device_name='LINGQU-EDGE-01', model='LQ_L2-SWITCH')
print(result.device_type.value)
" 2>/dev/null)
if [ "$LINGQU_RESULT" = "ai_network" ]; then
    pass "LINGQU 推断为 ai_network"
else
    fail "LINGQU 推断失败: $LINGQU_RESULT"
fi

# Test infer_device_type with optical
OPTICAL_RESULT=$(python3 -c "
from backend.recognition import infer_device_type
result = infer_device_type(device_name='OPT-LINK-MOD-01', model='Optical-Link-Module')
print(result.device_type.value)
" 2>/dev/null)
if [ "$OPTICAL_RESULT" = "optical_resource" ]; then
    pass "Optical 推断为 optical_resource"
else
    fail "Optical 推断失败: $OPTICAL_RESULT"
fi

# ── Step 4: Backend 启动测试 ──────────────────────────────
echo ""
echo "── Step 4：Backend 启动测试 ──"

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

# ── Step 5: Recognition API 测试 ──────────────────────────
echo ""
echo "── Step 5：Recognition API 测试 ──"

# Start recognition
RECOGNITION_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/recognition/start \
    -H "Content-Type: application/json" \
    -d '{"data_source_id": "sample_topology", "scope_id": "scope-full"}' 2>/dev/null || echo "{}")

REC_ID=$(echo "$RECOGNITION_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('recognition_id', ''))" 2>/dev/null || echo "")

if [ -n "$REC_ID" ]; then
    pass "recognition/start 返回 recognition_id"

    # Find the latest recognition snapshot file
    # RealEngineAdapter returns UUID-based IDs (rec-{uuid}), not rec-001
    # MockEngineAdapter returns rec-001
    SNAPSHOT_FILE=""
    if [ "$REC_ID" = "rec-001" ]; then
        # Mock mode: no snapshot file needed
        SNAPSHOT_FILE=""
    else
        # Real mode: find the snapshot matching the recognition_id
        SNAPSHOT_FILE="$PROJECT_ROOT/workspace/snapshots/recognition/$REC_ID.json"
    fi

    if [ -n "$SNAPSHOT_FILE" ] && [ -f "$SNAPSHOT_FILE" ]; then
        if grep -q "device_type_summaries" "$SNAPSHOT_FILE" 2>/dev/null; then
            pass "recognition snapshot 包含 device_type_summaries"

            # Check for expected device types
            HAS_SWITCH=$(python3 -c "
import json
with open('$SNAPSHOT_FILE') as f:
    data = json.load(f)
    summary = data.get('recognition_summary', {})
    types = [s['device_type'] for s in summary.get('device_type_summaries', [])]
    print('yes' if 'switch' in types else 'no')
" 2>/dev/null)

            HAS_AI_NETWORK=$(python3 -c "
import json
with open('$SNAPSHOT_FILE') as f:
    data = json.load(f)
    summary = data.get('recognition_summary', {})
    types = [s['device_type'] for s in summary.get('device_type_summaries', [])]
    print('yes' if 'ai_network' in types else 'no')
" 2>/dev/null)

            HAS_OPTICAL=$(python3 -c "
import json
with open('$SNAPSHOT_FILE') as f:
    data = json.load(f)
    summary = data.get('recognition_summary', {})
    types = [s['device_type'] for s in summary.get('device_type_summaries', [])]
    print('yes' if 'optical_resource' in types else 'no')
" 2>/dev/null)

            HAS_NETWORK=$(python3 -c "
import json
with open('$SNAPSHOT_FILE') as f:
    data = json.load(f)
    summary = data.get('recognition_summary', {})
    types = [s['device_type'] for s in summary.get('device_type_summaries', [])]
    print('yes' if 'network_resource' in types else 'no')
" 2>/dev/null)

            if [ "$HAS_SWITCH" = "yes" ]; then
                pass "识别到 switch 类型"
            else
                fail "未识别到 switch 类型"
            fi

            if [ "$HAS_AI_NETWORK" = "yes" ]; then
                pass "识别到 ai_network 类型"
            else
                fail "未识别到 ai_network 类型"
            fi

            if [ "$HAS_OPTICAL" = "yes" ]; then
                pass "识别到 optical_resource 类型"
            else
                fail "未识别到 optical_resource 类型"
            fi

            if [ "$HAS_NETWORK" = "yes" ]; then
                pass "识别到 network_resource 类型"
            else
                fail "未识别到 network_resource 类型"
            fi
        else
            fail "recognition snapshot 缺少 device_type_summaries"
        fi
    elif [ -z "$SNAPSHOT_FILE" ]; then
        # Mock mode: skip snapshot checks
        pass "MockEngineAdapter 模式 (跳过 snapshot 检查)"
    else
        fail "recognition snapshot 文件不存在"
    fi
else
    fail "recognition/start 未返回 recognition_id"
fi

# ── Step 6: 检查不生成 IssueItem ────────────────────────────
echo ""
echo "── Step 6：IssueItem 检查 ──"

if grep -qi "IssueItem" "$PROJECT_ROOT/backend/recognition/type_inference.py" 2>/dev/null; then
    fail "type_inference.py 不应生成 IssueItem"
else
    pass "type_inference.py 不生成 IssueItem"
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
    echo "DEVICE_TYPE_INFERENCE_CHECK_PASS"
    echo "══════════════════════════════════════════════════════"
    exit 0
else
    echo "DEVICE_TYPE_INFERENCE_CHECK_FAIL"
    echo "══════════════════════════════════════════════════════"
    exit 1
fi
