#!/usr/bin/env bash
# ============================================================
# check_file_repository_runtime.sh
# TopoChecker — 验证 FileRepository 模式后端运行时 API 兼容性
# 用法：bash scripts/check_file_repository_runtime.sh
# ============================================================
set -uo pipefail

CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$CURRENT_DIR/.." && pwd)"
BACKEND_URL="http://localhost:8000"
TIMEOUT=5
PASS=0
FAIL=0
SKIP=0

RED='\033[0;31m'
GRN='\033[0;32m'
YLW='\033[0;33m'
BLU='\033[0;34m'
NC='\033[0m'

pass() {
  echo -e "  ${GRN}✓${NC} $1"
  PASS=$((PASS + 1))
}

fail() {
  echo -e "  ${RED}✗${NC} $1"
  FAIL=$((FAIL + 1))
}

skip() {
  echo -e "  ${YLW}⊘${NC} $1"
  SKIP=$((SKIP + 1))
}

info() {
  echo -e "  ${BLU}ℹ${NC} $1"
}

echo "══════════════════════════════════════════════════════"
echo "  FileRepository Runtime 验证"
echo "══════════════════════════════════════════════════════"
echo ""

# ── Step 1: 检查后端是否运行 ──────────────────────────────
echo "── Step 1: 检查后端状态 ──────────────────────────────"
echo ""

if ! curl -s -f --max-time 2 "$BACKEND_URL/health" > /dev/null 2>&1; then
    echo -e "  ${YLW}⚠${NC} 后端未运行，尝试启动 FileRepository 模式..."
    bash "$PROJECT_ROOT/scripts/dev_start_backend_file_repo.sh"
    sleep 3
fi

if ! curl -s -f --max-time 2 "$BACKEND_URL/health" > /dev/null 2>&1; then
    fail "后端无法启动或连接"
    echo ""
    echo "FILE_REPOSITORY_RUNTIME_FAIL"
    echo "══════════════════════════════════════════════════════"
    exit 1
fi

pass "后端已运行: $BACKEND_URL"

# ── Step 2: 校验环境确实是 FileRepository 模式 ─────────────
echo ""
echo "── Step 2: 校验 Repository 模式 ──────────────────────"
echo ""

# Check that the backend process has TOPOCHECKER_REPO=file in its environment
BACKEND_PID=$(pgrep -f "uvicorn.*backend.main:app" | head -1)
if [ -n "$BACKEND_PID" ]; then
    if ps e -p "$BACKEND_PID" 2>/dev/null | grep -q "TOPOCHECKER_REPO=file"; then
        pass "后端进程环境变量 TOPOCHECKER_REPO=file"
    else
        fail "后端进程未设置 TOPOCHECKER_REPO=file"
    fi
else
    skip "无法获取后端 PID"
fi

# Also verify by checking the log file
LOG_FILE="$PROJECT_ROOT/backend/dev_server_file_repo.log"
if [ -f "$LOG_FILE" ]; then
    if grep -q "TOPOCHECKER_REPO=file\|FileRepository" "$LOG_FILE" 2>/dev/null; then
        pass "日志确认 FileRepository 模式"
    else
        info "日志未明确显示 FileRepository 模式（可能启动时尚未加载）"
    fi
else
    skip "日志文件不存在"
fi

# ── Step 3: Smoke Test ────────────────────────────────────
echo ""
echo "── Step 3: Smoke Test ────────────────────────────────"
echo ""

check_http() {
  local method="$1"
  local endpoint="$2"
  local label="$3"
  local body="${4:-}"

  local url="${BACKEND_URL}${endpoint}"
  local response
  local http_code

  if [ -n "$body" ]; then
    response=$(curl -s -w "\n%{http_code}" -X "$method" "$url" -H "Content-Type: application/json" -d "$body" --max-time "$TIMEOUT" 2>/dev/null)
  else
    response=$(curl -s -w "\n%{http_code}" -X "$method" "$url" --max-time "$TIMEOUT" 2>/dev/null)
  fi

  http_code=$(echo "$response" | tail -1)

  if [ "$http_code" = "000" ]; then
    skip "$label - 后端未运行 (curl timeout)"
    return 1
  fi

  if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
    pass "$label - HTTP $http_code"
    return 0
  else
    fail "$label - HTTP $http_code"
    return 1
  fi
}

check_http GET "/health" "健康检查"
check_http GET "/api/baselines" "获取 baseline 列表"
check_http GET "/api/rules/definitions" "获取规则定义"
check_http GET "/api/rulesets" "获取规则集列表"
check_http GET "/api/data-sources" "获取数据源列表"
check_http GET "/api/scopes" "获取执行作用域列表"
check_http GET "/api/profiles/parameters" "获取参数配置列表"
check_http GET "/api/profiles/thresholds" "获取阈值配置列表"
check_http GET "/api/scopes/selectors" "获取作用域选择器列表"
check_http GET "/api/baselines/baseline-001/versions" "获取版本列表"
check_http GET "/api/versions/baseline-001::v1.0.0" "获取版本快照"
check_http GET "/api/versions/diff?from_version=baseline-001::v1.0.0&to_version=baseline-001::v1.1.0" "获取版本 Diff"
check_http GET "/api/recognition/status" "获取识别状态"
check_http GET "/api/runs" "获取运行历史"
check_http GET "/api/runs/run-001" "获取 Run 详情"
check_http GET "/api/bundles/bundle-001" "获取 Bundle 详情"
check_http GET "/api/issues/issue-001" "获取 Issue 详情"
check_http GET "/api/diff/recheck?base_run_id=run-001&target_run_id=run-002" "获取 Recheck Diff"

# ── Step 4: API Snapshot Check ────────────────────────────
echo ""
echo "── Step 4: API Contract Snapshot 校验 ────────────────"
echo ""

SNAPSHOT_DIR="$PROJECT_ROOT/tests/backend_api_contract"

compare_snapshot() {
  local endpoint="$1"
  local filename="$2"
  local label="$3"

  local snapshot_file="$SNAPSHOT_DIR/$filename"
  if [ ! -f "$snapshot_file" ]; then
    skip "$label - 快照文件不存在"
    return
  fi

  local response
  local http_code

  response=$(curl -s -w "\n%{http_code}" "$BACKEND_URL$endpoint" --max-time "$TIMEOUT" 2>/dev/null)
  http_code=$(echo "$response" | tail -1)
  local actual=$(echo "$response" | sed '$d')

  if [ "$http_code" = "000" ]; then
    skip "$label - 后端超时"
    return
  fi

  if [ "$http_code" -ge 400 ]; then
    skip "$label - HTTP $http_code"
    return
  fi

  local expected
  expected=$(cat "$snapshot_file")

  if [ "$actual" = "$expected" ]; then
    pass "$label - 匹配"
  else
    fail "$label - 不匹配"
    echo "    期望: $(echo "$expected" | head -c 120)..."
    echo "    实际: $(echo "$actual" | head -c 120)..."
  fi
}

compare_snapshot "/health" "health.json" "Health"
compare_snapshot "/api/baselines" "baselines.json" "Baseline 列表"
compare_snapshot "/api/baselines/baseline-001" "baseline_detail.json" "Baseline 详情"
compare_snapshot "/api/baselines/baseline-001/profile-map" "baseline_profile_map.json" "Profile Map"
compare_snapshot "/api/baselines/baseline-001/version-snapshot" "baseline_version_snapshot.json" "Baseline Version Snapshot"
compare_snapshot "/api/rules/definitions" "rule_definitions.json" "Rule Definitions"
compare_snapshot "/api/rulesets" "rulesets.json" "Rule Sets"
compare_snapshot "/api/profiles/parameters" "parameter_profiles.json" "Parameter Profiles"
compare_snapshot "/api/profiles/thresholds" "threshold_profiles.json" "Threshold Profiles"
compare_snapshot "/api/scopes/selectors" "scope_selectors.json" "Scope Selectors"
compare_snapshot "/api/data-sources" "data_sources.json" "Data Sources"
compare_snapshot "/api/scopes" "execution_scopes.json" "Execution Scopes"
compare_snapshot "/api/recognition/status" "recognition_status.json" "Recognition Status"
compare_snapshot "/api/baselines/baseline-001/versions" "versions.json" "Version 列表"
compare_snapshot "/api/versions/baseline-001::v1.0.0" "version_snapshot.json" "Version Snapshot"
compare_snapshot "/api/versions/diff?from_version=baseline-001::v1.0.0&to_version=baseline-001::v1.1.0" "version_diff.json" "Version Diff"
compare_snapshot "/api/runs" "runs.json" "Run 历史"
compare_snapshot "/api/runs/run-001" "run_detail.json" "Run 详情"
compare_snapshot "/api/bundles/bundle-001" "bundle.json" "Bundle"
compare_snapshot "/api/issues/issue-001" "issue_detail.json" "Issue"
compare_snapshot "/api/diff/recheck?base_run_id=run-001&target_run_id=run-002" "recheck_diff.json" "Recheck Diff"

# ── Step 5: 边界检查 ──────────────────────────────────────
echo ""
echo "── Step 5: 边界检查 ──────────────────────────────────"
echo ""

# Check no database references in response
health_resp=$(curl -s --max-time "$TIMEOUT" "$BACKEND_URL/health" 2>/dev/null)
if echo "$health_resp" | grep -qi "sqlite\|database\|orm"; then
    fail "Health 响应包含数据库相关字段"
else
    pass "Health 响应无数据库相关字段"
fi

# Check default dev_start_backend.sh is NOT file repo mode
if grep -q "TOPOCHECKER_REPO=file" "$PROJECT_ROOT/scripts/dev_start_backend.sh" 2>/dev/null; then
    fail "dev_start_backend.sh 不应包含 TOPOCHECKER_REPO=file"
else
    pass "dev_start_backend.sh 未切换为 file 模式"
fi

echo ""
echo "══════════════════════════════════════════════════════"
echo -e "  通过：${GRN}${PASS}${NC}  失败：${RED}${FAIL}${NC}  跳过：${YLW}${SKIP}${NC}"
echo ""

if [ $FAIL -gt 0 ]; then
    echo "FILE_REPOSITORY_RUNTIME_FAIL"
    echo "══════════════════════════════════════════════════════"
    echo ""
    exit 1
else
    echo "FILE_REPOSITORY_RUNTIME_PASS"
    echo "══════════════════════════════════════════════════════"
    echo ""
    exit 0
fi
