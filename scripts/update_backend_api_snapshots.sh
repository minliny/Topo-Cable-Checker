#!/usr/bin/env bash
# ============================================================
# update_backend_api_snapshots.sh
# TopoChecker — 更新后端 API 契约快照
# 从本地后端获取响应并写入 snapshot JSON 文件
# 只允许 localhost / 127.0.0.1
# 用法：bash scripts/update_backend_api_snapshots.sh
# ============================================================
set -uo pipefail

CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$CURRENT_DIR/.." && pwd)"
BACKEND_URL="http://localhost:8000"
TIMEOUT=5
SNAPSHOT_DIR="$PROJECT_ROOT/tests/backend_api_contract"

RED='\033[0;31m'
GRN='\033[0;32m'
YLW='\033[0;33m'
NC='\033[0m'

echo "══════════════════════════════════════════════════════"
echo "  TopoChecker 后端 API 契约快照更新"
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

fetch_and_save() {
  local endpoint="$1"
  local filename="$2"
  local response
  local http_code

  echo -n "请求 $endpoint ... "
  response=$(curl -s -w "\n%{http_code}" "$BACKEND_URL$endpoint" --max-time "$TIMEOUT" 2>/dev/null)
  http_code=$(echo "$response" | tail -1)
  local body=$(echo "$response" | sed '$d')

  if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
    echo "$body" > "$SNAPSHOT_DIR/$filename"
    echo -e "${GRN}✓${NC} 保存到 $filename"
  else
    echo -e "${RED}✗${NC} HTTP $http_code"
  fi
}

mkdir -p "$SNAPSHOT_DIR"

echo "── 更新 Health ────────────────────────────────────"
fetch_and_save "/health" "health.json"

echo ""
echo "── 更新 Baseline 接口 ───────────────────────────────"
fetch_and_save "/api/baselines" "baselines.json"
fetch_and_save "/api/baselines/baseline-001" "baseline_detail.json"
fetch_and_save "/api/baselines/baseline-001/profile-map" "baseline_profile_map.json"
fetch_and_save "/api/baselines/baseline-001/version-snapshot" "baseline_version_snapshot.json"

echo ""
echo "── 更新 Rule 接口 ─────────────────────────────────"
fetch_and_save "/api/rules/definitions" "rule_definitions.json"
fetch_and_save "/api/rulesets" "rulesets.json"

echo ""
echo "── 更新 Profile 接口 ────────────────────────────────"
fetch_and_save "/api/profiles/parameters" "parameter_profiles.json"
fetch_and_save "/api/profiles/thresholds" "threshold_profiles.json"
fetch_and_save "/api/scopes/selectors" "scope_selectors.json"

echo ""
echo "── 更新 Execution 接口 ─────────────────────────────"
fetch_and_save "/api/data-sources" "data_sources.json"
fetch_and_save "/api/scopes" "execution_scopes.json"
fetch_and_save "/api/recognition/status" "recognition_status.json"

echo ""
echo "── 更新 Version 接口 ───────────────────────────────"
fetch_and_save "/api/baselines/baseline-001/versions" "versions.json"
fetch_and_save "/api/versions/baseline-001::v1.0.0" "version_snapshot.json"
fetch_and_save "/api/versions/diff?from_version=baseline-001::v1.0.0&to_version=baseline-001::v1.1.0" "version_diff.json"

echo ""
echo "── 更新 Run 接口 ──────────────────────────────────"
fetch_and_save "/api/runs" "runs.json"
fetch_and_save "/api/runs/run-001" "run_detail.json"
fetch_and_save "/api/bundles/bundle-001" "bundle.json"
fetch_and_save "/api/issues/issue-001" "issue_detail.json"

echo ""
echo "── 更新 Diff 接口 ─────────────────────────────────"
fetch_and_save "/api/diff/recheck?base_run_id=run-001&target_run_id=run-002" "recheck_diff.json"

echo ""
echo "══════════════════════════════════════════════════════"
echo "  快照更新完成"
echo "══════════════════════════════════════════════════════"
echo ""
echo "使用以下命令验证快照："
echo "  bash scripts/check_backend_api_contract_snapshots.sh"
echo ""