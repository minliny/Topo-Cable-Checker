#!/usr/bin/env bash
# ============================================================
# dev_check_all.sh
# TopoChecker — 本地开发全量检查
# 执行所有护栏检查和 smoke test
# 用法：bash scripts/dev_check_all.sh
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOST="127.0.0.1"
PORT="8000"

RED='\033[0;31m'
GRN='\033[0;32m'
YLW='\033[0;33m'
NC='\033[0m'

TOTAL_PASS=0
TOTAL_FAIL=0

run_check() {
    local name="$1"
    local cmd="$2"

    echo ""
    echo "══════════════════════════════════════════════════════"
    echo "  $name"
    echo "══════════════════════════════════════════════════════"

    if eval "$cmd"; then
        echo ""
        echo -e "${GRN}✓ PASS${NC}"
        return 0
    else
        echo ""
        echo -e "${RED}✗ FAIL${NC}"
        return 1
    fi
}

echo "══════════════════════════════════════════════════════"
echo "  TopoChecker 本地开发全量检查"
echo "══════════════════════════════════════════════════════"
echo ""

# Check if backend is running
echo "── 检查后端状态 ──────────────────────────────"
if curl -s -f --max-time 1 "http://$HOST:$PORT/health" > /dev/null 2>&1; then
    echo -e "${GRN}✓${NC} 后端已运行"
    BACKEND_RUNNING=1
else
    echo -e "${YLW}⚠${NC} 后端未运行"
    echo ""
    echo "提示：先启动后端以运行完整检查："
    echo "  bash scripts/dev_start_backend.sh"
    echo ""
    BACKEND_RUNNING=0
fi
echo ""

# Frontend checks
echo "══════════════════════════════════════════════════════"
echo "  阶段 1：前端护栏检查"
echo "══════════════════════════════════════════════════════"

run_check "Frontend Prototype Freeze" "bash '$PROJECT_ROOT/scripts/check_frontend_prototype_freeze.sh'" || ((TOTAL_FAIL++))
run_check "Frontend Componentization" "bash '$PROJECT_ROOT/scripts/check_frontend_componentization_phase1.sh'" || ((TOTAL_FAIL++))
run_check "Frontend Typecheck Baseline" "bash '$PROJECT_ROOT/scripts/check_frontend_typecheck_baseline.sh'" || ((TOTAL_FAIL++))

echo ""
echo "══════════════════════════════════════════════════════"
echo "  阶段 2：前端 npm typecheck"
echo "══════════════════════════════════════════════════════"

(cd "$PROJECT_ROOT/frontend" && npm run typecheck) || ((TOTAL_FAIL++))

# Backend skeleton checks
echo ""
echo "══════════════════════════════════════════════════════"
echo "  阶段 3：后端 API Skeleton 检查"
echo "══════════════════════════════════════════════════════"

run_check "Backend API Skeleton" "bash '$PROJECT_ROOT/scripts/check_backend_api_skeleton.sh'" || ((TOTAL_FAIL++))

# Backend runtime checks (only if backend is running)
if [ $BACKEND_RUNNING -eq 1 ]; then
    echo ""
    echo "══════════════════════════════════════════════════════"
    echo "  阶段 4：后端 Runtime 检查（后端已运行）"
    echo "══════════════════════════════════════════════════════"

    run_check "Smoke Test" "bash '$PROJECT_ROOT/scripts/smoke_frontend_backend_local.sh'" || ((TOTAL_FAIL++))
    run_check "API Contract Snapshots" "bash '$PROJECT_ROOT/scripts/check_backend_api_contract_snapshots.sh'" || ((TOTAL_FAIL++))
else
    echo ""
    echo "══════════════════════════════════════════════════════"
    echo "  阶段 4：后端 Runtime 检查（跳过）"
    echo "══════════════════════════════════════════════════════"
    echo -e "${YLW}⚠${NC} 后端未运行，跳过后端 runtime 检查"
    echo ""
    echo "启动后端后重新运行此脚本："
    echo "  bash scripts/dev_start_backend.sh"
    echo "  bash scripts/dev_check_all.sh"
fi

# Summary
echo ""
echo "══════════════════════════════════════════════════════"
echo "  检查完成"
echo "══════════════════════════════════════════════════════"

if [ $TOTAL_FAIL -eq 0 ]; then
    echo -e "${GRN}✓ 所有检查通过${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}✗ $TOTAL_FAIL 项检查失败${NC}"
    echo ""
    exit 1
fi
