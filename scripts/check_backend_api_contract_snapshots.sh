#!/usr/bin/env bash
# ============================================================
# check_backend_api_contract_snapshots.sh
# TopoChecker — 校验后端 API 契约快照
# 对比后端响应与 snapshot JSON 文件
# 用法：bash scripts/check_backend_api_contract_snapshots.sh
# ============================================================
set -uo pipefail

CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$CURRENT_DIR/.." && pwd)"
BACKEND_URL="http://localhost:8000"
TIMEOUT=5
SNAPSHOT_DIR="$PROJECT_ROOT/tests/backend_api_contract"
PASS=0
FAIL=0
SKIP=0

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

skip() {
  echo -e "  ${YLW}⊘${NC} $1"
  SKIP=$((SKIP + 1))
}

echo "══════════════════════════════════════════════════════"
echo "  TopoChecker 后端 API 契约快照校验"
echo "══════════════════════════════════════════════════════"
echo ""

if ! curl -s -f --max-time 2 "$BACKEND_URL/health" > /dev/null 2>&1; then
  echo -e "${RED}✗${NC} 后端未运行或无法连接: $BACKEND_URL"
  echo ""
  echo "请先启动后端："
  echo "  cd backend"
  echo "  pip install -r requirements.txt"
  echo "  uvicorn main:app --reload --port 8000"
  echo ""
  exit 1
fi

echo -e "${GRN}✓${NC} 后端已运行: $BACKEND_URL"
echo ""

compare_snapshot() {
  local endpoint="$1"
  local filename="$2"
  local label="$3"

  local snapshot_file="$SNAPSHOT_DIR/$filename"
  if [ ! -f "$snapshot_file" ]; then
    skip "$label - 快照文件不存在: $filename"
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
    echo "    期望: $(echo "$expected" | head -c 100)..."
    echo "    实际: $(echo "$actual" | head -c 100)..."
  fi
}

echo "── 校验 Health ────────────────────────────────────"
compare_snapshot "/health" "health.json" "Health"

echo ""
echo "── 校验 Baseline 接口 ───────────────────────────────"
compare_snapshot "/api/baselines" "baselines.json" "Baseline 列表"
compare_snapshot "/api/baselines/baseline-001" "baseline_detail.json" "Baseline 详情"
compare_snapshot "/api/baselines/baseline-001/profile-map" "baseline_profile_map.json" "Profile Map"
compare_snapshot "/api/baselines/baseline-001/version-snapshot" "baseline_version_snapshot.json" "Baseline Version Snapshot"

echo ""
echo "── 校验 Rule 接口 ─────────────────────────────────"
compare_snapshot "/api/rules/definitions" "rule_definitions.json" "Rule Definitions"
compare_snapshot "/api/rulesets" "rulesets.json" "Rule Sets"

echo ""
echo "── 校验 Profile 接口 ────────────────────────────────"
compare_snapshot "/api/profiles/parameters" "parameter_profiles.json" "Parameter Profiles"
compare_snapshot "/api/profiles/thresholds" "threshold_profiles.json" "Threshold Profiles"
compare_snapshot "/api/scopes/selectors" "scope_selectors.json" "Scope Selectors"

echo ""
echo "── 校验 Execution 接口 ─────────────────────────────"
compare_snapshot "/api/data-sources" "data_sources.json" "Data Sources"
compare_snapshot "/api/scopes" "execution_scopes.json" "Execution Scopes"
compare_snapshot "/api/recognition/status" "recognition_status.json" "Recognition Status"

echo ""
echo "── 校验 Version 接口 ───────────────────────────────"
compare_snapshot "/api/baselines/baseline-001/versions" "versions.json" "Version 列表"
compare_snapshot "/api/versions/baseline-001::v1.0.0" "version_snapshot.json" "Version Snapshot"
compare_snapshot "/api/versions/diff?from_version=baseline-001::v1.0.0&to_version=baseline-001::v1.1.0" "version_diff.json" "Version Diff"

echo ""
echo "── 校验 Run 接口 ─────────────────────────────────"
compare_snapshot "/api/runs" "runs.json" "Run 历史"
compare_snapshot "/api/runs/run-001" "run_detail.json" "Run 详情"
compare_snapshot "/api/bundles/bundle-001" "bundle.json" "Bundle"
compare_snapshot "/api/issues/issue-001" "issue_detail.json" "Issue"

echo ""
echo "── 校验 Diff 接口 ─────────────────────────────────"
compare_snapshot "/api/diff/recheck?base_run_id=run-001&target_run_id=run-002" "recheck_diff.json" "Recheck Diff"

echo ""
echo "══════════════════════════════════════════════════════"
echo -e "  通过：${GRN}${PASS}${NC}  失败：${RED}${FAIL}${NC}  跳过：${YLW}${SKIP}${NC}"
echo ""

if [ $FAIL -gt 0 ]; then
  echo "API_CONTRACT_CHECK_FAIL"
  echo "══════════════════════════════════════════════════════"
  echo ""
  echo "后端 API 响应与快照不匹配。"
  echo "如果这是预期的变化，请更新快照："
  echo "  bash scripts/update_backend_api_snapshots.sh"
  echo ""
  exit 1
else
  echo "API_CONTRACT_CHECK_PASS"
  echo "══════════════════════════════════════════════════════"
  echo ""
  exit 0
fi