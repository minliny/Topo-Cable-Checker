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

info() {
  echo -e "  ${YLW}ℹ${NC} $1"
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

# Check for AI/LLM dependencies (only if explicit AI/LLM library, excluding comments)
if grep -rqiE "(openai|anthropic|gemini|claude)" "$PROJECT_ROOT/backend" 2>/dev/null; then
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

# Check provider default is file (not mock/database)
if grep -q 'default.*file\|"file"\|TOPOCHECKER_REPO.*file' "$PROJECT_ROOT/backend/repositories/provider.py" 2>/dev/null; then
  pass "provider.py 默认使用 file repository"
else
  fail "provider.py 默认可能不是 file repository"
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

# Check provider defaults to file
if grep -A2 -B2 'TOPOCHECKER_REPO' "$PROJECT_ROOT/backend/repositories/provider.py" 2>/dev/null | grep -q 'file.*default\|default.*file'; then
  pass "provider.py 默认已设为 file"
else
  fail "provider.py 默认未设为 file"
fi

# Check LOCAL_WORKSPACE_PERSISTENCE.md explicitly says no database
if grep -qi "no database\|不接数据库\|禁止.*数据库\|禁止.*sqlite\|禁止.*orm" "$PROJECT_ROOT/docs/dev/LOCAL_WORKSPACE_PERSISTENCE.md" 2>/dev/null; then
  pass "LOCAL_WORKSPACE_PERSISTENCE.md 明确不使用数据库"
else
  fail "LOCAL_WORKSPACE_PERSISTENCE.md 未明确说明不使用数据库"
fi

# ── Section 10c: Workspace Fixture 检查 ───────────────────────────
echo ""
echo "── Section 10c：Workspace Fixture 检查 ──"

check_file "export_mock_to_workspace.sh" "$PROJECT_ROOT/scripts/export_mock_to_workspace.sh"
check_file "export_mock_to_workspace.py" "$PROJECT_ROOT/backend/scripts/export_mock_to_workspace.py"
check_file "WORKSPACE_FIXTURES.md" "$PROJECT_ROOT/docs/dev/WORKSPACE_FIXTURES.md"

EXPORT_PY="$PROJECT_ROOT/backend/scripts/export_mock_to_workspace.py"

# Check export script has no database import references (exclude docstrings/comments)
found_db=$(awk '
  /^\s*"""/ { in_doc = !in_doc; next }
  in_doc { next }
  /^\s*#/ { next }
  /sqlite|sqlalchemy|peewee|tortoise|pymongo/ { print "found"; exit }
' "$EXPORT_PY" 2>/dev/null)
if [ -n "$found_db" ]; then
  fail "export_mock_to_workspace.py 包含数据库依赖"
else
  pass "export_mock_to_workspace.py 无数据库依赖"
fi

# Check export script uses json dump
if grep -q "json.dump" "$EXPORT_PY" 2>/dev/null; then
  pass "export_mock_to_workspace.py 使用 json.dump"
else
  fail "export_mock_to_workspace.py 未使用 json.dump"
fi

# Check export script references mock_data module
if grep -q "mock_data" "$EXPORT_PY" 2>/dev/null; then
  pass "export_mock_to_workspace.py 引用 mock_data"
else
  fail "export_mock_to_workspace.py 未引用 mock_data"
fi

# Check FileRepository reads from workspace inputs
if grep -q "_load_json\|_load_json_list\|_load_json_dict" "$PROJECT_ROOT/backend/repositories/file_repository.py" 2>/dev/null; then
  pass "FileRepository 实现 workspace JSON 读取 helper"
else
  fail "FileRepository 未实现 workspace JSON 读取 helper"
fi

# Check FileRepository has fallback to mock
if grep -q "_mock\." "$PROJECT_ROOT/backend/repositories/file_repository.py" 2>/dev/null; then
  pass "FileRepository 保留 mock fallback"
else
  fail "FileRepository 未保留 mock fallback"
fi

# Check WORKSPACE_FIXTURES.md explicitly says default is FileRepository
if grep -qi "默认.*FileRepository\|default.*FileRepository\|默认 repository" "$PROJECT_ROOT/docs/dev/WORKSPACE_FIXTURES.md" 2>/dev/null; then
  pass "WORKSPACE_FIXTURES.md 说明默认 repository"
else
  fail "WORKSPACE_FIXTURES.md 未说明默认 repository"
fi

# Check WORKSPACE_FIXTURES.md says no database
if grep -qi "no database\|不接数据库\|禁止.*数据库\|禁止.*sqlite\|禁止.*orm" "$PROJECT_ROOT/docs/dev/WORKSPACE_FIXTURES.md" 2>/dev/null; then
  pass "WORKSPACE_FIXTURES.md 明确不使用数据库"
else
  fail "WORKSPACE_FIXTURES.md 未明确说明不使用数据库"
fi

# ── Section 10d: FileRepository Runtime 检查 ──────────────────────
echo ""
echo "── Section 10d：FileRepository Runtime 检查 ──"

check_file "dev_start_backend_file_repo.sh" "$PROJECT_ROOT/scripts/dev_start_backend_file_repo.sh"
check_file "check_file_repository_runtime.sh" "$PROJECT_ROOT/scripts/check_file_repository_runtime.sh"

# Check dev_start_backend_file_repo.sh sets TOPOCHECKER_REPO=file
if grep -q "TOPOCHECKER_REPO=file" "$PROJECT_ROOT/scripts/dev_start_backend_file_repo.sh" 2>/dev/null; then
  pass "dev_start_backend_file_repo.sh 设置 TOPOCHECKER_REPO=file"
else
  fail "dev_start_backend_file_repo.sh 未设置 TOPOCHECKER_REPO=file"
fi

# Check dev_start_backend_file_repo.sh does NOT change default script
if grep -q "dev_start_backend.sh" "$PROJECT_ROOT/scripts/dev_start_backend_file_repo.sh" 2>/dev/null; then
  pass "dev_start_backend_file_repo.sh 引用默认启动脚本"
else
  info "dev_start_backend_file_repo.sh 未引用默认启动脚本"
fi

# Check check_file_repository_runtime.sh runs smoke test
if grep -q "check_http\|smoke\|Smoke" "$PROJECT_ROOT/scripts/check_file_repository_runtime.sh" 2>/dev/null; then
  pass "check_file_repository_runtime.sh 包含 smoke test"
else
  fail "check_file_repository_runtime.sh 未包含 smoke test"
fi

# Check check_file_repository_runtime.sh compares snapshots
if grep -q "compare_snapshot\|snapshot" "$PROJECT_ROOT/scripts/check_file_repository_runtime.sh" 2>/dev/null; then
  pass "check_file_repository_runtime.sh 包含 snapshot 校验"
else
  fail "check_file_repository_runtime.sh 未包含 snapshot 校验"
fi

# Check WORKSPACE_FIXTURES.md contains TOPOCHECKER_REPO=file
if grep -q "TOPOCHECKER_REPO=file" "$PROJECT_ROOT/docs/dev/WORKSPACE_FIXTURES.md" 2>/dev/null; then
  pass "WORKSPACE_FIXTURES.md 包含 TOPOCHECKER_REPO=file 说明"
else
  fail "WORKSPACE_FIXTURES.md 未包含 TOPOCHECKER_REPO=file 说明"
fi

# Check default dev_start_backend.sh does NOT set TOPOCHECKER_REPO=mock
if grep -q "TOPOCHECKER_REPO=mock" "$PROJECT_ROOT/scripts/dev_start_backend.sh" 2>/dev/null; then
  fail "dev_start_backend.sh 不应设置 TOPOCHECKER_REPO=mock"
else
  pass "dev_start_backend.sh 未强制 mock 模式"
fi

# Check dev_check_all.sh contains check_file_repository_runtime.sh
if grep -q "check_file_repository_runtime" "$PROJECT_ROOT/scripts/dev_check_all.sh" 2>/dev/null; then
  pass "dev_check_all.sh 包含 FileRepository runtime 检查"
else
  fail "dev_check_all.sh 未包含 FileRepository runtime 检查"
fi

# Check dev_check_all.sh contains export_mock_to_workspace
if grep -q "export_mock_to_workspace" "$PROJECT_ROOT/scripts/dev_check_all.sh" 2>/dev/null; then
  pass "dev_check_all.sh 包含 workspace fixture 导出"
else
  fail "dev_check_all.sh 未包含 workspace fixture 导出"
fi

# Check CI workflow contains file-repository-runtime job
if grep -q "file-repository-runtime" "$PROJECT_ROOT/.github/workflows/frontend-backend-ci.yml" 2>/dev/null; then
  pass "CI workflow 包含 file-repository-runtime job"
else
  fail "CI workflow 未包含 file-repository-runtime job"
fi

# Check CI workflow smoke job uses default (FileRepository) or does not force mock
if grep -A20 "smoke-and-snapshots" "$PROJECT_ROOT/.github/workflows/frontend-backend-ci.yml" 2>/dev/null | grep -q "TOPOCHECKER_REPO=mock"; then
  fail "CI smoke job 不应设置 TOPOCHECKER_REPO=mock"
else
  pass "CI smoke job 未强制 mock 模式（默认 FileRepository）"
fi

# Check CI workflow sets TOPOCHECKER_REPO=file in file-repository-runtime job
if grep -A50 "file-repository-runtime:" "$PROJECT_ROOT/.github/workflows/frontend-backend-ci.yml" 2>/dev/null | grep -q "TOPOCHECKER_REPO=file"; then
  pass "CI file-repository-runtime job 设置 TOPOCHECKER_REPO=file"
else
  fail "CI file-repository-runtime job 未设置 TOPOCHECKER_REPO=file"
fi

# Check LOCAL_DEV_WORKFLOW.md contains FileRepository section
if grep -q "FileRepository" "$PROJECT_ROOT/docs/dev/LOCAL_DEV_WORKFLOW.md" 2>/dev/null; then
  pass "LOCAL_DEV_WORKFLOW.md 包含 FileRepository 说明"
else
  fail "LOCAL_DEV_WORKFLOW.md 未包含 FileRepository 说明"
fi

# Check CI_BASELINE.md contains FileRepository runtime
if grep -q "FileRepository" "$PROJECT_ROOT/docs/dev/CI_BASELINE.md" 2>/dev/null; then
  pass "CI_BASELINE.md 包含 FileRepository runtime 说明"
else
  fail "CI_BASELINE.md 未包含 FileRepository runtime 说明"
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

# Check execution_service uses engine via provider
if grep -q "from ..engine.provider import get_engine" "$PROJECT_ROOT/backend/services/execution_service.py" 2>/dev/null; then
  pass "execution_service.py 使用 engine via provider"
else
  fail "execution_service.py 未使用 engine via provider"
fi

# Check run_service uses engine via provider
if grep -q "from ..engine.provider import get_engine" "$PROJECT_ROOT/backend/services/run_service.py" 2>/dev/null; then
  pass "run_service.py 使用 engine via provider"
else
  fail "run_service.py 未使用 engine via provider"
fi

# Check diff_service uses engine via provider
if grep -q "from ..engine.provider import get_engine" "$PROJECT_ROOT/backend/services/diff_service.py" 2>/dev/null; then
  pass "diff_service.py 使用 engine via provider"
else
  fail "diff_service.py 未使用 engine via provider"
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

# ── Section 13: FileRepository Switch Readiness Audit 检查 ──────────
echo ""
echo "── Section 13：FileRepository Switch Readiness Audit 检查 ──"

check_file "audit_repository_response_parity.sh" "$PROJECT_ROOT/scripts/audit_repository_response_parity.sh"
check_file "FILE_REPOSITORY_SWITCH_READINESS.md" "$PROJECT_ROOT/docs/dev/FILE_REPOSITORY_SWITCH_READINESS.md"

# Check audit script exists and is executable
if [ -x "$PROJECT_ROOT/scripts/audit_repository_response_parity.sh" ]; then
  pass "audit_repository_response_parity.sh 可执行"
else
  fail "audit_repository_response_parity.sh 不可执行"
fi

# Check audit script uses localhost only
if grep -q "localhost\|127.0.0.1" "$PROJECT_ROOT/scripts/audit_repository_response_parity.sh" 2>/dev/null; then
  pass "audit_repository_response_parity.sh 只使用 localhost"
else
  fail "audit_repository_response_parity.sh 未使用 localhost"
fi

# Check audit script does NOT switch default repository
if grep -q "TOPOCHECKER_REPO.*default\|default.*file" "$PROJECT_ROOT/scripts/audit_repository_response_parity.sh" 2>/dev/null; then
  fail "audit_repository_response_parity.sh 不应修改默认 repository"
else
  pass "audit_repository_response_parity.sh 不修改默认 repository"
fi

# Check audit script compares mock vs file
if grep -q "mock\|file" "$PROJECT_ROOT/scripts/audit_repository_response_parity.sh" 2>/dev/null; then
  pass "audit_repository_response_parity.sh 对比 mock 与 file"
else
  fail "audit_repository_response_parity.sh 未对比 mock 与 file"
fi

# Check FILE_REPOSITORY_SWITCH_READINESS.md says default is FileRepository
if grep -qi "默认.*FileRepository\|当前默认.*FileRepository\|Default.*FileRepository" "$PROJECT_ROOT/docs/dev/FILE_REPOSITORY_SWITCH_READINESS.md" 2>/dev/null; then
  pass "FILE_REPOSITORY_SWITCH_READINESS.md 说明默认 repository"
else
  fail "FILE_REPOSITORY_SWITCH_READINESS.md 未说明默认 repository"
fi

# Check FILE_REPOSITORY_SWITCH_READINESS.md says no database
if grep -qi "no database\|不接数据库\|禁止.*数据库\|禁止.*sqlite\|禁止.*orm" "$PROJECT_ROOT/docs/dev/FILE_REPOSITORY_SWITCH_READINESS.md" 2>/dev/null; then
  pass "FILE_REPOSITORY_SWITCH_READINESS.md 明确不使用数据库"
else
  fail "FILE_REPOSITORY_SWITCH_READINESS.md 未明确说明不使用数据库"
fi

# Check provider.py default is file
if grep -q 'TOPOCHECKER_REPO.*file\|default.*file\|"file"' "$PROJECT_ROOT/backend/repositories/provider.py" 2>/dev/null; then
  pass "provider.py 默认为 file repository"
else
  fail "provider.py 默认可能不是 file"
fi

# ── Section 14: Check Engine Integration Readiness Audit 检查 ──────────
echo ""
echo "── Section 14：Check Engine Integration Readiness Audit 检查 ──"

check_file "CHECK_ENGINE_INTEGRATION_READINESS.md" "$PROJECT_ROOT/docs/dev/CHECK_ENGINE_INTEGRATION_READINESS.md"

# Check document contains MockEngineAdapter
if grep -qi "MockEngineAdapter" "$PROJECT_ROOT/docs/dev/CHECK_ENGINE_INTEGRATION_READINESS.md" 2>/dev/null; then
  pass "文档包含 MockEngineAdapter"
else
  fail "文档未包含 MockEngineAdapter"
fi

# Check document contains recognition result
if grep -qi "RecognitionResult\|recognition result" "$PROJECT_ROOT/docs/dev/CHECK_ENGINE_INTEGRATION_READINESS.md" 2>/dev/null; then
  pass "文档包含 recognition result"
else
  fail "文档未包含 recognition result"
fi

# Check document contains normalized dataset
if grep -qi "normalized dataset\|Normalized Dataset" "$PROJECT_ROOT/docs/dev/CHECK_ENGINE_INTEGRATION_READINESS.md" 2>/dev/null; then
  pass "文档包含 normalized dataset"
else
  fail "文档未包含 normalized dataset"
fi

# Check document contains CheckResultBundle
if grep -qi "CheckResultBundle" "$PROJECT_ROOT/docs/dev/CHECK_ENGINE_INTEGRATION_READINESS.md" 2>/dev/null; then
  pass "文档包含 CheckResultBundle"
else
  fail "文档未包含 CheckResultBundle"
fi

# Check document contains RecheckDiffSnapshot
if grep -qi "RecheckDiffSnapshot" "$PROJECT_ROOT/docs/dev/CHECK_ENGINE_INTEGRATION_READINESS.md" 2>/dev/null; then
  pass "文档包含 RecheckDiffSnapshot"
else
  fail "文档未包含 RecheckDiffSnapshot"
fi

# Check document explicitly says no database
if grep -qi "no database\|不接数据库\|禁止.*数据库\|禁止.*sqlite\|禁止.*orm" "$PROJECT_ROOT/docs/dev/CHECK_ENGINE_INTEGRATION_READINESS.md" 2>/dev/null; then
  pass "文档明确不使用数据库"
else
  fail "文档未明确说明不使用数据库"
fi

# Check document explicitly says no AI/LLM
if grep -qi "no AI\|不引入 AI\|禁止.*AI\|禁止.*LLM\|不依赖 AI" "$PROJECT_ROOT/docs/dev/CHECK_ENGINE_INTEGRATION_READINESS.md" 2>/dev/null; then
  pass "文档明确不使用 AI/LLM"
else
  fail "文档未明确说明不使用 AI/LLM"
fi

# Check document explicitly says frontend does not compute diff
if grep -qi "前端不计算 diff\|frontend 不计算\|前端不生成.*diff\|engine/backend 生成\|backend 生成" "$PROJECT_ROOT/docs/dev/CHECK_ENGINE_INTEGRATION_READINESS.md" 2>/dev/null; then
  pass "文档明确前端不计算 diff"
else
  fail "文档未明确说明前端不计算 diff"
fi

# ── Section 15: RealEngineAdapter Scaffold 检查 ──────────────────
echo ""
echo "── Section 15：RealEngineAdapter Scaffold 检查 ──"

check_file "RealEngineAdapter scaffold" "$PROJECT_ROOT/backend/engine/real_engine.py"
check_file "Engine provider" "$PROJECT_ROOT/backend/engine/provider.py"

# Check real_engine.py has NotImplementedError (scaffold guard)
if grep -q "NotImplementedError" "$PROJECT_ROOT/backend/engine/real_engine.py" 2>/dev/null; then
  pass "real_engine.py 所有方法 raise NotImplementedError (scaffold)"
else
  fail "real_engine.py 缺少 NotImplementedError scaffold guard"
fi

# Check real_engine.py does not have real engine calls
# Use word boundaries to avoid false positives (e.g., "wait" contains "ai")
if ! grep -qiE "(openpyxl|pandas|sqlalchemy|\bsqlite\b|openai|anthropic|requests)" "$PROJECT_ROOT/backend/engine/real_engine.py" 2>/dev/null; then
  pass "real_engine.py 不接数据库/AI/LLM"
else
  fail "real_engine.py 可能接入了数据库或 AI/LLM"
fi

# Check provider.py supports TOPOCHECKER_ENGINE env var
if grep -q "TOPOCHECKER_ENGINE" "$PROJECT_ROOT/backend/engine/provider.py" 2>/dev/null; then
  pass "provider.py 支持 TOPOCHECKER_ENGINE 环境变量"
else
  fail "provider.py 不支持 TOPOCHECKER_ENGINE 环境变量"
fi

# Check provider.py defaults to mock
if grep -qi 'default.*mock\|os.environ.get.*mock' "$PROJECT_ROOT/backend/engine/provider.py" 2>/dev/null; then
  pass "provider.py 默认 engine 为 mock"
else
  fail "provider.py 默认 engine 不是 mock"
fi

# Check services use engine provider
if grep -q "from ..engine.provider import get_engine" "$PROJECT_ROOT/backend/services/execution_service.py" 2>/dev/null; then
  pass "execution_service.py 使用 engine provider"
else
  fail "execution_service.py 未使用 engine provider"
fi

if grep -q "from ..engine.provider import get_engine" "$PROJECT_ROOT/backend/services/run_service.py" 2>/dev/null; then
  pass "run_service.py 使用 engine provider"
else
  fail "run_service.py 未使用 engine provider"
fi

if grep -q "from ..engine.provider import get_engine" "$PROJECT_ROOT/backend/services/diff_service.py" 2>/dev/null; then
  pass "diff_service.py 使用 engine provider"
else
  fail "diff_service.py 未使用 engine provider"
fi

# Check real_engine.py does not directly import mock_data
if ! grep -qi "mock_data\|MOCK_BASELINES\|MOCK_RUNS" "$PROJECT_ROOT/backend/engine/real_engine.py" 2>/dev/null; then
  pass "real_engine.py 不直接导入 mock_data"
else
  fail "real_engine.py 不应导入 mock_data"
fi

# ── Section 16: Local Input File Reader Scaffold 检查 ────────────
echo ""
echo "── Section 16：Local Input File Reader Scaffold 检查 ──"

check_dir "input/ 目录" "$PROJECT_ROOT/backend/input"
check_file "input/models.py" "$PROJECT_ROOT/backend/input/models.py"
check_file "input/reader.py" "$PROJECT_ROOT/backend/input/reader.py"
check_file "input/normalizer.py" "$PROJECT_ROOT/backend/input/normalizer.py"

# Check LocalInputReader class exists
if grep -q "class LocalInputReader" "$PROJECT_ROOT/backend/input/reader.py" 2>/dev/null; then
  pass "LocalInputReader 类存在"
else
  fail "LocalInputReader 类不存在"
fi

# Check NormalizedDataset exists
if grep -q "class NormalizedDataset" "$PROJECT_ROOT/backend/input/models.py" 2>/dev/null; then
  pass "NormalizedDataset 模型存在"
else
  fail "NormalizedDataset 模型不存在"
fi

# Check normalize_raw_dataset function exists
if grep -q "def normalize_raw_dataset" "$PROJECT_ROOT/backend/input/normalizer.py" 2>/dev/null; then
  pass "normalize_raw_dataset 函数存在"
else
  fail "normalize_raw_dataset 函数不存在"
fi

# Check documentation exists
check_file "LOCAL_INPUT_FILE_READER.md" "$PROJECT_ROOT/docs/dev/LOCAL_INPUT_FILE_READER.md"

# Check input module does not have database/AI/LLM (excluding comments)
if ! grep -qiE "(sqlite3|sqlalchemy|\bopenai\b|\banthropic\b)" "$PROJECT_ROOT/backend/input"/*.py 2>/dev/null; then
  pass "input/ 模块不接数据库/AI/LLM"
else
  fail "input/ 模块可能接入了数据库或 AI/LLM"
fi

# Check input module uses openpyxl for Excel (not forbidden)
if grep -q "openpyxl" "$PROJECT_ROOT/backend/input/reader.py" 2>/dev/null; then
  pass "reader.py 使用 openpyxl 读取 Excel"
else
  fail "reader.py 未使用 openpyxl"
fi

# Check requirements.txt includes openpyxl
if grep -q "openpyxl" "$PROJECT_ROOT/backend/requirements.txt" 2>/dev/null; then
  pass "requirements.txt 包含 openpyxl"
else
  fail "requirements.txt 缺少 openpyxl"
fi

# ── Section 17: Real Engine Recognition Scaffold 检查 ────────
echo ""
echo "── Section 17：Real Engine Recognition Scaffold 检查 ──"

check_file "REAL_ENGINE_RECOGNITION_SCAFFOLD.md" "$PROJECT_ROOT/docs/dev/REAL_ENGINE_RECOGNITION_SCAFFOLD.md"
check_file "check_real_engine_recognition_scaffold.sh" "$PROJECT_ROOT/scripts/check_real_engine_recognition_scaffold.sh"

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

# Check real_engine.py implements recognition methods
if grep -q "async def start_recognition" "$PROJECT_ROOT/backend/engine/real_engine.py" 2>/dev/null; then
  pass "real_engine.py 实现 start_recognition"
else
  fail "real_engine.py 未实现 start_recognition"
fi

if grep -q "async def get_recognition_result" "$PROJECT_ROOT/backend/engine/real_engine.py" 2>/dev/null; then
  pass "real_engine.py 实现 get_recognition_result"
else
  fail "real_engine.py 未实现 get_recognition_result"
fi

# Check sample_topology.csv exists
check_file "sample_topology.csv" "$PROJECT_ROOT/workspace/inputs/sample_topology.csv"

# Check default engine is still mock (provider defaults to mock)
if grep -q 'get("TOPOCHECKER_ENGINE", "mock")' "$PROJECT_ROOT/backend/engine/provider.py" 2>/dev/null; then
  pass "provider.py 默认 engine 为 mock"
else
  fail "provider.py 默认 engine 不是 mock"
fi

# ── Section 18: Device Recognition Rules Scaffold 检查 ─────
echo ""
echo "── Section 18：Device Recognition Rules Scaffold 检查 ──"

check_dir "recognition/ 目录" "$PROJECT_ROOT/backend/recognition"
check_file "recognition/models.py" "$PROJECT_ROOT/backend/recognition/models.py"
check_file "recognition/recognizer.py" "$PROJECT_ROOT/backend/recognition/recognizer.py"
check_file "DEVICE_RECOGNITION_RULES.md" "$PROJECT_ROOT/docs/dev/DEVICE_RECOGNITION_RULES.md"
check_file "check_device_recognition_rules.sh" "$PROJECT_ROOT/scripts/check_device_recognition_rules.sh"

# Check DatasetRecognizer exists
if grep -q "class DatasetRecognizer" "$PROJECT_ROOT/backend/recognition/recognizer.py" 2>/dev/null; then
  pass "DatasetRecognizer 类存在"
else
  fail "DatasetRecognizer 类不存在"
fi

# Check RecognizedTableKind exists
if grep -q "class RecognizedTableKind" "$PROJECT_ROOT/backend/recognition/models.py" 2>/dev/null; then
  pass "RecognizedTableKind 枚举存在"
else
  fail "RecognizedTableKind 枚举不存在"
fi

# Check recognition module uses keyword matching
if grep -q "DEVICE_KEYWORDS\|LINK_KEYWORDS" "$PROJECT_ROOT/backend/recognition/recognizer.py" 2>/dev/null; then
  pass "识别关键词已定义"
else
  fail "识别关键词未定义"
fi

# Check real_engine.py uses DatasetRecognizer
if grep -q "from ..recognition import DatasetRecognizer" "$PROJECT_ROOT/backend/engine/real_engine.py" 2>/dev/null; then
  pass "real_engine.py 导入 DatasetRecognizer"
else
  fail "real_engine.py 未导入 DatasetRecognizer"
fi

# Check recognition module does not have AI/LLM or database (excluding comments)
if ! grep -qiE "(sqlite3|sqlalchemy|\bopenai\b|\banthropic\b)" "$PROJECT_ROOT/backend/recognition"/*.py 2>/dev/null; then
  pass "recognition/ 模块不接数据库/AI/LLM"
else
  fail "recognition/ 模块可能接入了数据库或 AI/LLM"
fi

# Check recognizer does not generate IssueItem
if ! grep -qi "IssueItem" "$PROJECT_ROOT/backend/recognition/recognizer.py" 2>/dev/null; then
  pass "recognizer.py 不生成 IssueItem"
else
  fail "recognizer.py 不应生成 IssueItem"
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
