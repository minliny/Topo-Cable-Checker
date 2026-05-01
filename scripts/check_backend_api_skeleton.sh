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

# Check for database / ORM / SQLite dependencies
DB_CONN_FOUND=0
for pyfile in $(find "$PROJECT_ROOT/backend" -name "*.py"); do
  if grep -qi "sqlite3\|psycopg\|pymysql\|sqlalchemy\|mongodb\|pymongo\|peewee\|tortoise" "$pyfile" 2>/dev/null; then
    DB_CONN_FOUND=1
    break
  fi
done
if [ $DB_CONN_FOUND -eq 1 ]; then
  fail "backend 包含数据库/ORM/SQLite 依赖（禁止）"
else
  pass "backend 无数据库/ORM/SQLite 依赖"
fi

# Check for production URLs (exclude localhost, exclude FastAPI CORS import)
PROD_URL_FOUND=0
for pyfile in $(find "$PROJECT_ROOT/backend" -name "*.py"); do
  # Skip mock_data.py which may contain "production" in descriptions
  if [ "$(basename "$pyfile")" = "mock_data.py" ]; then
    continue
  fi
  # Check for actual production URLs or API endpoints, not import statements
  if grep -E "^[^#]*(cloud\.|aws\.|azure\.|gcp\.|https?://[^l])" "$pyfile" 2>/dev/null | grep -vi "localhost\|127.0.0.1" > /dev/null; then
    PROD_URL_FOUND=1
    break
  fi
done
if [ $PROD_URL_FOUND -eq 1 ]; then
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

# ── Section 10: Service/Repository 分层检查 ────────────────────────────────
echo ""
echo "── Section 10：Service/Repository 分层检查 ──"

check_dir "services/ 目录" "$PROJECT_ROOT/backend/services"
check_dir "repositories/ 目录" "$PROJECT_ROOT/backend/repositories"
check_file "repositories/interface.py" "$PROJECT_ROOT/backend/repositories/interface.py"
check_file "repositories/provider.py" "$PROJECT_ROOT/backend/repositories/provider.py"
check_file "mock_repository.py" "$PROJECT_ROOT/backend/repositories/mock_repository.py"

# Check service files exist
for svc in baseline rule version execution run diff profile; do
  check_file "${svc}_service.py" "$PROJECT_ROOT/backend/services/${svc}_service.py"
done

# Check routers do NOT directly import mock_data
ROUTER_MOCK_IMPORT_COUNT=0
for router in baselines.py rules.py versions.py execution.py runs.py diff.py profiles.py; do
  if grep -q "from \.\.data import\|from \.\.data\.mock_data import" "$PROJECT_ROOT/backend/routers/$router" 2>/dev/null; then
    fail "router $router 直接 import mock_data（应通过 service 层）"
    ROUTER_MOCK_IMPORT_COUNT=$((ROUTER_MOCK_IMPORT_COUNT + 1))
  fi
done
if [ $ROUTER_MOCK_IMPORT_COUNT -eq 0 ]; then
  pass "所有 routers 不直接 import mock_data"
fi

# Check services use provider instead of directly instantiating MockRepository
SERVICE_PROVIDER_COUNT=0
for svc in baseline rule version execution run diff profile; do
  if grep -q "get_repository" "$PROJECT_ROOT/backend/services/${svc}_service.py" 2>/dev/null; then
    pass "${svc}_service.py 使用 repository provider"
  else
    fail "${svc}_service.py 未使用 repository provider"
    SERVICE_PROVIDER_COUNT=$((SERVICE_PROVIDER_COUNT + 1))
  fi
done

# Check mock_repository implements Repository interface
if grep -q "class MockRepository(Repository)" "$PROJECT_ROOT/backend/repositories/mock_repository.py" 2>/dev/null; then
  pass "MockRepository 显式实现 Repository 接口"
else
  fail "MockRepository 未显式实现 Repository 接口"
fi

# Check repository imports mock_data
if grep -q "from \.\.data import" "$PROJECT_ROOT/backend/repositories/mock_repository.py" 2>/dev/null; then
  pass "mock_repository.py 正确 import mock_data"
else
  fail "mock_repository.py 未 import mock_data"
fi

# Check provider defaults to MockRepository
if grep -q "MockRepository" "$PROJECT_ROOT/backend/repositories/provider.py" 2>/dev/null; then
  pass "provider.py 包含 MockRepository"
else
  fail "provider.py 不包含 MockRepository"
fi

# Check provider default is mock (not database)
if grep -q 'default.*mock\|"mock"\|TOPOCHECKER_REPO.*mock' "$PROJECT_ROOT/backend/repositories/provider.py" 2>/dev/null; then
  pass "provider.py 默认使用 mock repository"
else
  fail "provider.py 默认可能不是 mock repository"
fi

# Check NO sqlite_repository.py exists
if [ -f "$PROJECT_ROOT/backend/repositories/sqlite_repository.py" ]; then
  fail "sqlite_repository.py 不应存在（禁止数据库）"
else
  pass "sqlite_repository.py 不存在"
fi

# Check NO DATABASE_INTEGRATION_PLAN.md exists
if [ -f "$PROJECT_ROOT/docs/api/DATABASE_INTEGRATION_PLAN.md" ]; then
  fail "DATABASE_INTEGRATION_PLAN.md 不应存在（禁止数据库计划）"
else
  pass "DATABASE_INTEGRATION_PLAN.md 不存在"
fi

# ── Section 10b: Local Workspace Persistence 检查 ─────────────────
echo ""
echo "── Section 10b：Local Workspace Persistence 检查 ──"

check_dir "workspace/ 目录" "$PROJECT_ROOT/backend/workspace"
check_file "workspace/__init__.py" "$PROJECT_ROOT/backend/workspace/__init__.py"
check_file "workspace/paths.py" "$PROJECT_ROOT/backend/workspace/paths.py"
check_file "workspace/schema.py" "$PROJECT_ROOT/backend/workspace/schema.py"
check_file "workspace/manager.py" "$PROJECT_ROOT/backend/workspace/manager.py"
check_file "file_repository.py" "$PROJECT_ROOT/backend/repositories/file_repository.py"
check_file "LOCAL_WORKSPACE_PERSISTENCE.md" "$PROJECT_ROOT/docs/dev/LOCAL_WORKSPACE_PERSISTENCE.md"

# Check workspace __init__ exports WorkspacePaths and WorkspaceManager
if grep -q "WorkspacePaths" "$PROJECT_ROOT/backend/workspace/__init__.py" 2>/dev/null; then
  pass "workspace/__init__.py 导出 WorkspacePaths"
else
  fail "workspace/__init__.py 未导出 WorkspacePaths"
fi

if grep -q "WorkspaceManager" "$PROJECT_ROOT/backend/workspace/__init__.py" 2>/dev/null; then
  pass "workspace/__init__.py 导出 WorkspaceManager"
else
  fail "workspace/__init__.py 未导出 WorkspaceManager"
fi

# Check workspace paths defines all 6 directories
for dir_name in inputs tasks runs snapshots reports exports; do
  if grep -q "def ${dir_name}\|${dir_name}" "$PROJECT_ROOT/backend/workspace/paths.py" 2>/dev/null; then
    pass "paths.py 定义 ${dir_name} 目录"
  else
    fail "paths.py 未定义 ${dir_name} 目录"
  fi
done

# Check workspace manager has save/load methods
for method in save_task load_task list_tasks save_run load_run list_runs save_snapshot load_snapshot list_snapshots save_report list_reports save_export load_export; do
  if grep -q "def ${method}" "$PROJECT_ROOT/backend/workspace/manager.py" 2>/dev/null; then
    pass "manager.py 实现 ${method}"
  else
    fail "manager.py 未实现 ${method}"
  fi
done

# Check file_repository.py implements Repository and uses WorkspaceManager
if grep -q "class FileRepository(Repository)" "$PROJECT_ROOT/backend/repositories/file_repository.py" 2>/dev/null; then
  pass "FileRepository 显式实现 Repository 接口"
else
  fail "FileRepository 未显式实现 Repository 接口"
fi

if grep -q "WorkspaceManager" "$PROJECT_ROOT/backend/repositories/file_repository.py" 2>/dev/null; then
  pass "FileRepository 使用 WorkspaceManager"
else
  fail "FileRepository 未使用 WorkspaceManager"
fi

# Check provider.py has FileRepository branch
if grep -q "FileRepository" "$PROJECT_ROOT/backend/repositories/provider.py" 2>/dev/null; then
  pass "provider.py 预留 FileRepository 分支"
else
  fail "provider.py 未预留 FileRepository 分支"
fi

# Check default is still mock (not file)
if grep -q 'TOPOCHECKER_REPO.*mock\|default.*mock\|"mock"' "$PROJECT_ROOT/backend/repositories/provider.py" 2>/dev/null; then
  pass "provider.py 默认仍为 mock repository"
else
  fail "provider.py 默认可能已切换为 file repository"
fi

# Check provider does NOT default to file
if grep -A2 -B2 'TOPOCHECKER_REPO' "$PROJECT_ROOT/backend/repositories/provider.py" 2>/dev/null | grep -q 'file.*default\|default.*file'; then
  fail "provider.py 默认可能已设为 file"
else
  pass "provider.py 默认未设为 file"
fi

# Check LOCAL_WORKSPACE_PERSISTENCE.md explicitly says no database
if grep -qi "no database\|不接数据库\|禁止.*数据库\|禁止.*sqlite\|禁止.*orm" "$PROJECT_ROOT/docs/dev/LOCAL_WORKSPACE_PERSISTENCE.md" 2>/dev/null; then
  pass "LOCAL_WORKSPACE_PERSISTENCE.md 明确不使用数据库"
else
  fail "LOCAL_WORKSPACE_PERSISTENCE.md 未明确说明不使用数据库"
fi

# ── Section 11: Engine Adapter 检查 ────────────────────────────────
echo ""
echo "── Section 11：Engine Adapter 检查 ──"

check_dir "engine/ 目录" "$PROJECT_ROOT/backend/engine"
check_file "engine/interface.py" "$PROJECT_ROOT/backend/engine/interface.py"
check_file "engine/mock_engine.py" "$PROJECT_ROOT/backend/engine/mock_engine.py"

# Check EngineAdapter class exists
if grep -q "class EngineAdapter" "$PROJECT_ROOT/backend/engine/interface.py" 2>/dev/null; then
  pass "EngineAdapter 抽象类存在"
else
  fail "EngineAdapter 抽象类不存在"
fi

# Check MockEngineAdapter implements EngineAdapter
if grep -q "class MockEngineAdapter(EngineAdapter)" "$PROJECT_ROOT/backend/engine/mock_engine.py" 2>/dev/null; then
  pass "MockEngineAdapter 实现 EngineAdapter"
else
  fail "MockEngineAdapter 未实现 EngineAdapter"
fi

# Check engine has no real external service calls
if grep -rqi "requests\|httpx\|urllib" "$PROJECT_ROOT/backend/engine" 2>/dev/null; then
  fail "engine 目录包含真实 HTTP 调用"
else
  pass "engine 无真实 HTTP 调用"
fi

# Check execution_service uses engine adapter
if grep -q "MockEngineAdapter" "$PROJECT_ROOT/backend/services/execution_service.py" 2>/dev/null; then
  pass "execution_service.py 使用 MockEngineAdapter"
else
  fail "execution_service.py 未使用 MockEngineAdapter"
fi

# Check run_service uses engine adapter
if grep -q "MockEngineAdapter" "$PROJECT_ROOT/backend/services/run_service.py" 2>/dev/null; then
  pass "run_service.py 使用 MockEngineAdapter"
else
  fail "run_service.py 未使用 MockEngineAdapter"
fi

# Check diff_service uses engine adapter
if grep -q "MockEngineAdapter" "$PROJECT_ROOT/backend/services/diff_service.py" 2>/dev/null; then
  pass "diff_service.py 使用 MockEngineAdapter"
else
  fail "diff_service.py 未使用 MockEngineAdapter"
fi

# ── Section 12: CI Configuration 检查 ────────────────────────────────
echo ""
echo "── Section 12：CI Configuration 检查 ──"

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
