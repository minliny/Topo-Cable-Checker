#!/usr/bin/env bash
# ============================================================
# check_backend_api_skeleton.sh
# TopoChecker — 后端 API Skeleton 静态护栏
# 检查 backend/ 目录下的 API skeleton 实现
# 用法：bash scripts/check_backend_api_skeleton.sh
# ============================================================
set -euo pipefail

CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$CURRENT_DIR/.." && pwd)"
PASS=0
FAIL=0

RED='\033[0;31m'
GRN='\033[0;32m'
YLW='\033[0;33m'
NC='\033[0m'

pass() {
  echo -e "  ${GRN}✓${NC} $1"
  PASS=$((PASS + 1))
}

fail() {
  echo -e "  ${RED}✗${NC} $1"
  FAIL=$((FAIL + 1))
}

echo "══════════════════════════════════════════════════════"
echo "  TopoChecker 后端 API Skeleton 护栏"
echo "══════════════════════════════════════════════════════"

# ── Section 1: Backend 目录结构检查 ───────────────────────────────
echo ""
echo "── Section 1：Backend 目录结构检查 ──"

if [ -d "$PROJECT_ROOT/backend" ]; then
  pass "backend/ 目录存在"
else
  fail "backend/ 目录不存在"
  echo ""
  echo "FRONTEND_BACKEND_API_SKELETON_CHECK_FAIL"
  exit 1
fi

check_file() {
  local label="$1" file="$2"
  if [ -f "$file" ]; then
    pass "$label 存在: $file"
  else
    fail "$label 不存在: $file"
  fi
}

check_dir() {
  local label="$1" dir="$2"
  if [ -d "$dir" ]; then
    pass "$label 存在: $dir"
  else
    fail "$label 不存在: $dir"
  fi
}

check_file "main.py" "$PROJECT_ROOT/backend/main.py"
check_file "requirements.txt" "$PROJECT_ROOT/backend/requirements.txt"
check_file "models/__init__.py" "$PROJECT_ROOT/backend/models/__init__.py"
check_file "data/mock_data.py" "$PROJECT_ROOT/backend/data/mock_data.py"
check_file "routers/__init__.py" "$PROJECT_ROOT/backend/routers/__init__.py"

# ── Section 2: 核心路由文件检查 ──────────────────────────────────
echo ""
echo "── Section 2：核心路由文件检查 ──"

check_file "baselines.py" "$PROJECT_ROOT/backend/routers/baselines.py"
check_file "rules.py" "$PROJECT_ROOT/backend/routers/rules.py"
check_file "versions.py" "$PROJECT_ROOT/backend/routers/versions.py"
check_file "execution.py" "$PROJECT_ROOT/backend/routers/execution.py"
check_file "runs.py" "$PROJECT_ROOT/backend/routers/runs.py"
check_file "diff.py" "$PROJECT_ROOT/backend/routers/diff.py"
check_file "profiles.py" "$PROJECT_ROOT/backend/routers/profiles.py"

# ── Section 3: 文档检查 ─────────────────────────────────────────
echo ""
echo "── Section 3：文档检查 ──"

check_file "BACKEND_API_SKELETON.md" "$PROJECT_ROOT/docs/api/BACKEND_API_SKELETON.md"

# ── Section 4: Mock 数据检查 ─────────────────────────────────────
echo ""
echo "── Section 4：Mock 数据检查 ──"

if grep -q "MOCK_BASELINES" "$PROJECT_ROOT/backend/data/mock_data.py" 2>/dev/null; then
  pass "mock_data.py 包含 MOCK_BASELINES"
else
  fail "mock_data.py 缺少 MOCK_BASELINES"
fi

if grep -q "MOCK_RUNS" "$PROJECT_ROOT/backend/data/mock_data.py" 2>/dev/null; then
  pass "mock_data.py 包含 MOCK_RUNS"
else
  fail "mock_data.py 缺少 MOCK_RUNS"
fi

if grep -q "MOCK_RECHECK_DIFF_SNAPSHOTS\|RecheckDiffSnapshot" "$PROJECT_ROOT/backend/data/mock_data.py" 2>/dev/null; then
  pass "mock_data.py 包含 RecheckDiffSnapshot"
else
  fail "mock_data.py 缺少 RecheckDiffSnapshot"
fi

if grep -q "MOCK_VERSION_DIFF_SNAPSHOTS\|VersionDiffSnapshot" "$PROJECT_ROOT/backend/data/mock_data.py" 2>/dev/null; then
  pass "mock_data.py 包含 VersionDiffSnapshot"
else
  fail "mock_data.py 缺少 VersionDiffSnapshot"
fi

# ── Section 5: 禁止内容检查 ─────────────────────────────────────
echo ""
echo "── Section 5：禁止内容检查 ──"

# Check for database connection configuration
if grep -rqi "sqlite\|postgres\|mysql\|mongodb\|sqlalchemy.*create_engine\|psycopg" "$PROJECT_ROOT/backend" 2>/dev/null; then
  fail "backend 包含数据库连接配置（禁止使用真实数据库）"
else
  pass "backend 无数据库连接配置"
fi

# Check for production URLs (exclude localhost)
if grep -rE "^[^#]*(production|api\.|cloud\.|aws\.|azure\.|gcp\.|https?://[^l]" "$PROJECT_ROOT/backend" 2>/dev/null | grep -vi "localhost\|127.0.0.1" > /dev/null; then
  fail "backend 包含生产 URL"
else
  pass "backend 无生产 URL"
fi

# Check for AI/LLM dependencies (only if explicit AI/LLM library)
if grep -rqi "openai\|anthropic\|llm\|gemini\|claude" "$PROJECT_ROOT/backend" 2>/dev/null; then
  fail "backend 包含 AI/LLM 依赖（禁止使用 AI/LLM）"
else
  pass "backend 无 AI/LLM 依赖"
fi

# Check for real check engine
if grep -rqi "check_engine\|rule_executor\|run_checks\|execute_check" "$PROJECT_ROOT/backend" 2>/dev/null | grep -v "#"; then
  fail "backend 包含检查引擎调用（禁止接入真实引擎）"
else
  pass "backend 无检查引擎调用"
fi

# Check main.py is using FastAPI
if grep -qi "FastAPI\|uvicorn" "$PROJECT_ROOT/backend/main.py" 2>/dev/null; then
  pass "main.py 使用 FastAPI"
else
  fail "main.py 未使用 FastAPI"
fi

# ── Section 6: API 契约兼容性检查 ────────────────────────────────
echo ""
echo "── Section 6：API 契约兼容性检查 ──"

# Check recognition confirm endpoint exists
if grep -q "recognition/confirm" "$PROJECT_ROOT/backend/routers/execution.py" 2>/dev/null; then
  pass "保留 recognition confirm 流程"
else
  fail "缺少 recognition confirm 流程"
fi

# Check diff endpoint returns RecheckDiffSnapshot
if grep -q "recheck.*diff\|diff.*recheck\|RecheckDiffSnapshot" "$PROJECT_ROOT/backend/routers/diff.py" 2>/dev/null; then
  pass "diff 路由返回 RecheckDiffSnapshot"
else
  fail "diff 路由未返回 RecheckDiffSnapshot"
fi

# ── Section 7: Smoke Test 检查 ──────────────────────────────────────────
echo ""
echo "── Section 7：Smoke Test 检查 ──"

check_file "smoke_frontend_backend_local.sh" "$PROJECT_ROOT/scripts/smoke_frontend_backend_local.sh"
check_file "LOCAL_INTEGRATION_SMOKE_TEST.md" "$PROJECT_ROOT/docs/api/LOCAL_INTEGRATION_SMOKE_TEST.md"

# Check smoke script has no production URLs
if [ -f "$PROJECT_ROOT/scripts/smoke_frontend_backend_local.sh" ]; then
  if grep -E "^[^#]*https?://" "$PROJECT_ROOT/scripts/smoke_frontend_backend_local.sh" 2>/dev/null | grep -vi "localhost\|127\.0\.0\.1\|example\|placeholder" > /dev/null; then
    fail "smoke 脚本包含生产 URL"
  else
    pass "smoke 脚本无生产 URL"
  fi
fi

# Check smoke script only uses localhost
if [ -f "$PROJECT_ROOT/scripts/smoke_frontend_backend_local.sh" ]; then
  if grep -q "localhost\|127\.0\.0\.1" "$PROJECT_ROOT/scripts/smoke_frontend_backend_local.sh" 2>/dev/null; then
    pass "smoke 脚本只使用 localhost"
  else
    fail "smoke 脚本未使用 localhost/127.0.0.1"
  fi
fi

# Check smoke script is executable
if [ -x "$PROJECT_ROOT/scripts/smoke_frontend_backend_local.sh" ] 2>/dev/null; then
  pass "smoke 脚本可执行"
else
  fail "smoke 脚本不可执行"
fi

# ── Section 8: API Contract Snapshots 检查 ────────────────────────────────
echo ""
echo "── Section 8：API Contract Snapshots 检查 ──"

check_dir "snapshot 目录" "$PROJECT_ROOT/tests/backend_api_contract"
check_file "update snapshots 脚本" "$PROJECT_ROOT/scripts/update_backend_api_snapshots.sh"
check_file "check snapshots 脚本" "$PROJECT_ROOT/scripts/check_backend_api_contract_snapshots.sh"
check_file "snapshots 文档" "$PROJECT_ROOT/docs/api/BACKEND_API_CONTRACT_SNAPSHOTS.md"

# Check key snapshot files exist
check_file "health.json" "$PROJECT_ROOT/tests/backend_api_contract/health.json"
check_file "baselines.json" "$PROJECT_ROOT/tests/backend_api_contract/baselines.json"
check_file "recheck_diff.json" "$PROJECT_ROOT/tests/backend_api_contract/recheck_diff.json"
check_file "version_diff.json" "$PROJECT_ROOT/tests/backend_api_contract/version_diff.json"

# Check update script has no production URLs
if [ -f "$PROJECT_ROOT/scripts/update_backend_api_snapshots.sh" ]; then
  if grep -E "^[^#]*(production|api\.example|https://[^l])" "$PROJECT_ROOT/scripts/update_backend_api_snapshots.sh" 2>/dev/null | grep -vi "localhost\|127\.0\.0\.1\|example\|placeholder" > /dev/null; then
    fail "update 脚本包含生产 URL"
  else
    pass "update 脚本无生产 URL"
  fi
fi

# Check update script only uses localhost
if [ -f "$PROJECT_ROOT/scripts/update_backend_api_snapshots.sh" ]; then
  if grep -q "localhost\|127\.0\.0\.1" "$PROJECT_ROOT/scripts/update_backend_api_snapshots.sh" 2>/dev/null; then
    pass "update 脚本只使用 localhost"
  else
    fail "update 脚本未使用 localhost/127.0.0.1"
  fi
fi

# Check update script is executable
if [ -x "$PROJECT_ROOT/scripts/update_backend_api_snapshots.sh" ] 2>/dev/null; then
  pass "update 脚本可执行"
else
  fail "update 脚本不可执行"
fi

# Check check script is executable
if [ -x "$PROJECT_ROOT/scripts/check_backend_api_contract_snapshots.sh" ] 2>/dev/null; then
  pass "check 脚本可执行"
else
  fail "check 脚本不可执行"
fi

# Check snapshot README exists
check_file "snapshots README" "$PROJECT_ROOT/tests/backend_api_contract/README.md"

# ── Section 9: Dev Orchestration Scripts 检查 ──────────────────────────────
echo ""
echo "── Section 9：Dev Orchestration Scripts 检查 ──"

check_file "dev_start_backend.sh" "$PROJECT_ROOT/scripts/dev_start_backend.sh"
check_file "dev_stop_backend.sh" "$PROJECT_ROOT/scripts/dev_stop_backend.sh"
check_file "dev_check_all.sh" "$PROJECT_ROOT/scripts/dev_check_all.sh"
check_file "LOCAL_DEV_WORKFLOW.md" "$PROJECT_ROOT/docs/dev/LOCAL_DEV_WORKFLOW.md"

# Check dev scripts are executable
if [ -x "$PROJECT_ROOT/scripts/dev_start_backend.sh" ] 2>/dev/null; then
  pass "dev_start_backend.sh 可执行"
else
  fail "dev_start_backend.sh 不可执行"
fi

if [ -x "$PROJECT_ROOT/scripts/dev_stop_backend.sh" ] 2>/dev/null; then
  pass "dev_stop_backend.sh 可执行"
else
  fail "dev_stop_backend.sh 不可执行"
fi

if [ -x "$PROJECT_ROOT/scripts/dev_check_all.sh" ] 2>/dev/null; then
  pass "dev_check_all.sh 可执行"
else
  fail "dev_check_all.sh 不可执行"
fi

# Check dev scripts only use localhost
for script in dev_start_backend.sh dev_stop_backend.sh dev_check_all.sh; do
  if [ -f "$PROJECT_ROOT/scripts/$script" ]; then
    if grep -E "^[^#]*(production|api\.|cloud\.|aws\.|azure\.|gcp\.)" "$PROJECT_ROOT/scripts/$script" 2>/dev/null | grep -vi "localhost\|127.0.0.1" > /dev/null; then
      fail "$script 包含生产 URL"
    else
      pass "$script 无生产 URL"
    fi
  fi
done

# Check dev scripts don't use AI/LLM (only explicit AI libraries)
for script in dev_start_backend.sh dev_stop_backend.sh dev_check_all.sh; do
  if [ -f "$PROJECT_ROOT/scripts/$script" ]; then
    if grep -qi "openai\|anthropic\|gemini\|claude" "$PROJECT_ROOT/scripts/$script" 2>/dev/null; then
      fail "$script 包含 AI/LLM 依赖"
    else
      pass "$script 无 AI/LLM 依赖"
    fi
  fi
done

# ── Section 10: CI Configuration 检查 ────────────────────────────────
echo ""
echo "── Section 10：CI Configuration 检查 ──"

check_file "CI workflow" "$PROJECT_ROOT/.github/workflows/frontend-backend-ci.yml"
check_file "CI 文档" "$PROJECT_ROOT/docs/dev/CI_BASELINE.md"

# Check CI workflow has frontend typecheck
if [ -f "$PROJECT_ROOT/.github/workflows/frontend-backend-ci.yml" ]; then
  if grep -q "npm run typecheck" "$PROJECT_ROOT/.github/workflows/frontend-backend-ci.yml" 2>/dev/null; then
    pass "CI workflow 包含 frontend typecheck"
  else
    fail "CI workflow 缺少 frontend typecheck"
  fi
fi

# Check CI workflow has backend smoke
if [ -f "$PROJECT_ROOT/.github/workflows/frontend-backend-ci.yml" ]; then
  if grep -q "smoke_frontend_backend_local.sh" "$PROJECT_ROOT/.github/workflows/frontend-backend-ci.yml" 2>/dev/null; then
    pass "CI workflow 包含 backend smoke test"
  else
    fail "CI workflow 缺少 backend smoke test"
  fi
fi

# Check CI workflow has snapshot check
if [ -f "$PROJECT_ROOT/.github/workflows/frontend-backend-ci.yml" ]; then
  if grep -q "check_backend_api_contract_snapshots.sh" "$PROJECT_ROOT/.github/workflows/frontend-backend-ci.yml" 2>/dev/null; then
    pass "CI workflow 包含 snapshot check"
  else
    fail "CI workflow 缺少 snapshot check"
  fi
fi

# Check CI workflow doesn't have production URLs
if [ -f "$PROJECT_ROOT/.github/workflows/frontend-backend-ci.yml" ]; then
  if grep -E "production|api\.|cloud\.|aws\.|azure\.|gcp\.|https?://[^l]" "$PROJECT_ROOT/.github/workflows/frontend-backend-ci.yml" 2>/dev/null | grep -vi "localhost\|127.0.0.1" | grep -qi "https://"; then
    fail "CI workflow 包含生产 URL"
  else
    pass "CI workflow 无生产 URL"
  fi
fi

# Check CI workflow doesn't use AI/LLM
if [ -f "$PROJECT_ROOT/.github/workflows/frontend-backend-ci.yml" ]; then
  if grep -qi "openai\|anthropic\|gemini\|claude" "$PROJECT_ROOT/.github/workflows/frontend-backend-ci.yml" 2>/dev/null; then
    fail "CI workflow 包含 AI/LLM 依赖"
  else
    pass "CI workflow 无 AI/LLM 依赖"
  fi
fi

# ── 结果汇总 ─────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════════════"
echo -e "  通过：${GRN}${PASS}${NC}  失败：${RED}${FAIL}${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
  echo "FRONTEND_BACKEND_API_SKELETON_CHECK_PASS"
  echo "══════════════════════════════════════════════════════"
  echo ""
  exit 0
else
  echo "FRONTEND_BACKEND_API_SKELETON_CHECK_FAIL"
  echo "══════════════════════════════════════════════════════"
  echo ""
  exit 1
fi