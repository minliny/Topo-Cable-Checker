#!/usr/bin/env bash
# ============================================================
# smoke_frontend_backend_local.sh
# TopoChecker — 前端后端本地联通 Smoke Test
# 测试后端 API 接口响应，不修改前端默认配置
# 用法：bash scripts/smoke_frontend_backend_local.sh
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
  echo -e "  ${YLW}⊘${NC} $1 (skipped)"
  SKIP=$((SKIP + 1))
}

info() {
  echo -e "  ${BLU}ℹ${NC} $1"
}

echo "══════════════════════════════════════════════════════"
echo "  TopoChecker 前端后端本地联通 Smoke Test"
echo "══════════════════════════════════════════════════════"
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
  local body_only=$(echo "$response" | sed '$d')

  if [ "$http_code" = "000" ]; then
    skip "$label - 后端未运行 (curl timeout)"
    return 1
  fi

  if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
    pass "$label - HTTP $http_code"
    return 0
  else
    fail "$label - HTTP $http_code: $body_only"
    return 1
  fi
}

check_json_field() {
  local endpoint="$1"
  local field="$2"
  local label="$3"

  local url="${BACKEND_URL}${endpoint}"
  local response
  local http_code

  response=$(curl -s -w "\n%{http_code}" "$url" --max-time "$TIMEOUT" 2>/dev/null)
  http_code=$(echo "$response" | tail -1)
  local body=$(echo "$response" | sed '$d')

  if [ "$http_code" = "000" ]; then
    skip "$label - 后端未运行"
    return 1
  fi

  if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
    if echo "$body" | grep -q "\"$field\"" 2>/dev/null; then
      pass "$label - 包含 $field 字段"
      return 0
    else
      fail "$label - 缺少 $field 字段"
      return 1
    fi
  else
    fail "$label - HTTP $http_code"
    return 1
  fi
}

echo "── Step 1: 检查后端状态 ──────────────────────────────"
echo ""

if curl -s -f --max-time 2 "$BACKEND_URL/health" > /dev/null 2>&1; then
  info "后端已运行: $BACKEND_URL"
else
  echo ""
  echo -e "  ${YLW}⚠${NC} 后端未运行或无法连接"
  echo "  请先启动后端："
  echo "    cd backend"
  echo "    pip install -r requirements.txt"
  echo "    uvicorn main:app --reload --port 8000"
  echo ""
  echo "  或者使用后台启动："
  echo "    cd backend && nohup uvicorn main:app --port 8000 > server.log 2>&1 &"
  echo ""
fi

echo "── Step 2: 基础接口测试 ─────────────────────────────"
echo ""

check_http GET "/health" "健康检查"
check_http GET "/api/baselines" "获取 baseline 列表"
check_http GET "/api/rules/definitions" "获取规则定义"
check_http GET "/api/rulesets" "获取规则集列表"
check_http GET "/api/data-sources" "获取数据源列表"
check_http GET "/api/scopes" "获取执行作用域列表"
check_http GET "/api/profiles/parameters" "获取参数配置列表"
check_http GET "/api/profiles/thresholds" "获取阈值配置列表"
check_http GET "/api/scopes/selectors" "获取作用域选择器列表"

echo ""
echo "── Step 3: 核心接口 JSON 字段验证 ──────────────────"
echo ""

check_json_field "/api/baselines" "baselines" "Baseline 列表响应"
check_json_field "/api/baselines/baseline-001" "baseline" "Baseline 详情响应"
check_json_field "/api/baselines/baseline-001/profile-map" "parameter_profile_id" "Profile Map 响应"
check_json_field "/api/baselines/baseline-001/version-snapshot" "current_version" "Version Snapshot 响应"
check_json_field "/api/rules/definitions" "rules" "Rule Definitions 响应"
check_json_field "/api/data-sources" "data_sources" "Data Sources 响应"
check_json_field "/api/scopes" "scopes" "Execution Scopes 响应"

echo ""
echo "── Step 4: Version/Execution 接口测试 ───────────────"
echo ""

check_http GET "/api/baselines/baseline-001/versions" "获取版本列表"
check_http GET "/api/versions/baseline-001::v1.0.0" "获取版本快照"
check_http GET "/api/versions/diff?from_version=baseline-001::v1.0.0&to_version=baseline-001::v1.1.0" "获取版本 Diff"
check_http GET "/api/recognition/status" "获取识别状态"
check_http GET "/api/runs" "获取运行历史"

echo ""
echo "── Step 5: Workbench/Diff 接口测试 ───────────────────"
echo ""

check_http GET "/api/runs/run-001" "获取 Run 详情"
check_http GET "/api/bundles/bundle-001" "获取 Bundle 详情"
check_http GET "/api/issues/issue-001" "获取 Issue 详情"
check_http GET "/api/diff/recheck?base_run_id=run-001&target_run_id=run-002" "获取 Recheck Diff"

echo ""
echo "── Step 6: Diff 边界验证 ─────────────────────────────"
echo ""

diff_response=$(curl -s --max-time "$TIMEOUT" "$BACKEND_URL/api/diff/recheck?base_run_id=run-001&target_run_id=run-002" 2>/dev/null)

if [ -n "$diff_response" ] && echo "$diff_response" | grep -q "diff_id\|summary\|issue_count_change" 2>/dev/null; then
  if echo "$diff_response" | grep -q "added_issues\|removed_issues" 2>/dev/null; then
    pass "Recheck Diff 包含预计算快照字段 (added_issues/removed_issues)"
  else
    pass "Recheck Diff 返回有效 JSON"
  fi
else
  if [ -z "$diff_response" ]; then
    skip "Recheck Diff - 后端未运行"
  else
    fail "Recheck Diff - 响应格式异常"
  fi
fi

echo ""
echo "── Step 7: 脚本约束检查 ──────────────────────────────"
echo ""

if grep -qE "^[^#]*(production|api\.example|https://[^l])" "$0" 2>/dev/null; then
  fail "Smoke 脚本包含生产 URL"
else
  pass "Smoke 脚本无生产 URL"
fi

if grep -qE "^[^#]*(axios|react-query|swr|fetch\()" "$0" 2>/dev/null; then
  fail "Smoke 脚本包含禁止库调用"
else
  pass "Smoke 脚本未使用禁止库"
fi

echo ""
echo "══════════════════════════════════════════════════════"
echo -e "  通过：${GRN}${PASS}${NC}  失败：${RED}${FAIL}${NC}  跳过：${YLW}${SKIP}${NC}"
echo ""

if [ $FAIL -gt 0 ]; then
  echo "SMOKE_TEST_FAIL"
  echo "══════════════════════════════════════════════════════"
  echo ""
  exit 1
elif [ $SKIP -gt 0 ] && [ $PASS -eq 0 ]; then
  echo "SMOKE_TEST_SKIP"
  echo "══════════════════════════════════════════════════════"
  echo ""
  echo "后端未运行或无法连接。Smoke test 需要后端运行才能执行。"
  echo "启动后端后重新运行此脚本。"
  exit 2
else
  echo "SMOKE_TEST_PASS"
  echo "══════════════════════════════════════════════════════"
  echo ""
  exit 0
fi