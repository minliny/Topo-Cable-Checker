#!/usr/bin/env bash
# ============================================================
# dev_check_all.sh
# TopoChecker — 开发环境全量检查
# 用法：bash scripts/dev_check_all.sh
# ============================================================
set -uo pipefail

CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$CURRENT_DIR/.." && pwd)"

RED='\033[0;31m'
GRN='\033[0;32m'
YLW='\033[0;33m'
BLU='\033[0;34m'
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

run_check() {
  local label="$1"
  local cmd="$2"

  echo ""
  echo "── $label ─────────────────────────────────────────────"
  echo ""

  if eval "$cmd"; then
    pass "$label"
  else
    fail "$label"
  fi
}

echo "══════════════════════════════════════════════════════"
echo "  TopoChecker 开发环境全量检查"
echo "══════════════════════════════════════════════════════"
echo ""

# ── 前端检查 ──────────────────────────────────────────────
echo ""
echo "═══ 前端检查 ═══"
echo ""

run_check "前端原型冻结检查" "bash $PROJECT_ROOT/scripts/check_frontend_prototype_freeze.sh"
run_check "前端组件化检查" "bash $PROJECT_ROOT/scripts/check_frontend_componentization_phase1.sh"
run_check "前端 Typecheck 基线" "bash $PROJECT_ROOT/scripts/check_frontend_typecheck_baseline.sh"

# ── 后端骨架检查 ──────────────────────────────────────────
echo ""
echo "═══ 后端骨架检查 ═══"
echo ""

run_check "后端 API 骨架检查" "bash $PROJECT_ROOT/scripts/check_backend_api_skeleton.sh"

# ── 导出 workspace fixtures ───────────────────────────────
echo ""
echo "═══ Workspace Fixtures 导出 ═══"
echo ""

run_check "导出 mock 到 workspace" "bash $PROJECT_ROOT/scripts/export_mock_to_workspace.sh"

# ── 默认 FileRepository 模式运行时检查 ────────────────────
echo ""
echo "═══ 默认 FileRepository 模式运行时检查 ═══"
echo ""

# 确保后端已停止
bash $PROJECT_ROOT/scripts/dev_stop_backend.sh 2>/dev/null || true

# 启动默认后端（FileRepository 模式）
echo ""
echo "启动后端（默认 FileRepository 模式）..."
bash $PROJECT_ROOT/scripts/dev_start_backend.sh
sleep 3

run_check "Smoke Test (FileRepository)" "bash $PROJECT_ROOT/scripts/smoke_frontend_backend_local.sh"
run_check "API Contract Snapshots (FileRepository)" "bash $PROJECT_ROOT/scripts/check_backend_api_contract_snapshots.sh"

# 停止后端
bash $PROJECT_ROOT/scripts/dev_stop_backend.sh

# ── MockRepository 回退模式运行时检查 ─────────────────────
echo ""
echo "═══ MockRepository 回退模式运行时检查 ═══"
echo ""

# 启动 MockRepository 模式后端
export TOPOCHECKER_REPO=mock
echo ""
echo "启动后端（MockRepository 回退模式）..."
bash $PROJECT_ROOT/scripts/dev_start_backend.sh
sleep 3

run_check "Smoke Test (Mock)" "bash $PROJECT_ROOT/scripts/smoke_frontend_backend_local.sh"
run_check "API Contract Snapshots (Mock)" "bash $PROJECT_ROOT/scripts/check_backend_api_contract_snapshots.sh"

# 停止后端
bash $PROJECT_ROOT/scripts/dev_stop_backend.sh
unset TOPOCHECKER_REPO

# ── FileRepository 模式运行时检查 ─────────────────────────
echo ""
echo "═══ FileRepository 模式运行时检查 ═══"
echo ""

# 启动 FileRepository 模式后端
echo ""
echo "启动后端（FileRepository 模式）..."
bash $PROJECT_ROOT/scripts/dev_start_backend_file_repo.sh
sleep 3

run_check "FileRepository Runtime 验证" "bash $PROJECT_ROOT/scripts/check_file_repository_runtime.sh"

# 停止后端（无论检查结果如何）
bash $PROJECT_ROOT/scripts/dev_stop_backend.sh

# ── 汇总 ──────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════════════"
echo -e "  通过：${GRN}${PASS}${NC}  失败：${RED}${FAIL}${NC}"
echo ""

if [ $FAIL -gt 0 ]; then
    echo -e "  ${RED}DEV_CHECK_ALL_FAIL${NC}"
    echo "══════════════════════════════════════════════════════"
    echo ""
    exit 1
else
    echo -e "  ${GRN}DEV_CHECK_ALL_PASS${NC}"
    echo "══════════════════════════════════════════════════════"
    echo ""
    exit 0
fi
