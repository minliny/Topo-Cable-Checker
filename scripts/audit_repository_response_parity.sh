#!/usr/bin/env bash
# ============================================================
# audit_repository_response_parity.sh
# TopoChecker — MockRepository vs FileRepository 响应对比审计
# 用法：bash scripts/audit_repository_response_parity.sh
# ============================================================
set -uo pipefail

CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$CURRENT_DIR/.." && pwd)"
BACKEND_URL="http://localhost:8000"
TIMEOUT=5
AUDIT_DIR="$PROJECT_ROOT/.audit_parity"

RED='\033[0;31m'
GRN='\033[0;32m'
YLW='\033[0;33m'
BLU='\033[0;34m'
NC='\033[0m'

MATCH=0
MISMATCH=0
SKIP=0

match() {
  echo -e "  ${GRN}✓ 匹配${NC} $1"
  MATCH=$((MATCH + 1))
}

mismatch() {
  echo -e "  ${RED}✗ 差异${NC} $1"
  MISMATCH=$((MISMATCH + 1))
}

skip() {
  echo -e "  ${YLW}⊘ 跳过${NC} $1"
  SKIP=$((SKIP + 1))
}

# ── Cleanup and setup ──────────────────────────────────────
rm -rf "$AUDIT_DIR"
mkdir -p "$AUDIT_DIR/mock"
mkdir -p "$AUDIT_DIR/file"

echo "══════════════════════════════════════════════════════"
echo "  MockRepository vs FileRepository 响应对比审计"
echo "══════════════════════════════════════════════════════"
echo ""

# ── Step 1: Export workspace fixtures ──────────────────────
echo "── Step 1: 导出 workspace fixtures ───────────────────"
echo ""
bash "$PROJECT_ROOT/scripts/export_mock_to_workspace.sh" > /dev/null 2>&1

# ── Step 2: Start MockRepository backend ───────────────────
echo ""
echo "── Step 2: 启动 MockRepository 模式后端 ──────────────"
echo ""

bash "$PROJECT_ROOT/scripts/dev_stop_backend.sh" 2>/dev/null || true
sleep 1

bash "$PROJECT_ROOT/scripts/dev_start_backend.sh" > /dev/null 2>&1
sleep 3

if ! curl -s -f --max-time 2 "$BACKEND_URL/health" > /dev/null 2>&1; then
    echo -e "  ${RED}✗${NC} MockRepository 后端启动失败"
    exit 1
fi
echo -e "  ${GRN}✓${NC} MockRepository 后端已启动"

# ── Step 3: Collect MockRepository responses ───────────────
echo ""
echo "── Step 3: 收集 MockRepository 响应 ──────────────────"
echo ""

fetch_and_save() {
    local endpoint="$1"
    local filename="$2"
    local outdir="$3"

    local response
    response=$(curl -s --max-time "$TIMEOUT" "$BACKEND_URL$endpoint" 2>/dev/null)
    echo "$response" > "$outdir/$filename"
}

fetch_and_save "/health" "health.json" "$AUDIT_DIR/mock"
fetch_and_save "/api/baselines" "baselines.json" "$AUDIT_DIR/mock"
fetch_and_save "/api/baselines/baseline-001" "baseline_detail.json" "$AUDIT_DIR/mock"
fetch_and_save "/api/rules/definitions" "rule_definitions.json" "$AUDIT_DIR/mock"
fetch_and_save "/api/rulesets" "rulesets.json" "$AUDIT_DIR/mock"
fetch_and_save "/api/profiles/parameters" "parameter_profiles.json" "$AUDIT_DIR/mock"
fetch_and_save "/api/profiles/thresholds" "threshold_profiles.json" "$AUDIT_DIR/mock"
fetch_and_save "/api/scopes/selectors" "scope_selectors.json" "$AUDIT_DIR/mock"
fetch_and_save "/api/data-sources" "data_sources.json" "$AUDIT_DIR/mock"
fetch_and_save "/api/scopes" "execution_scopes.json" "$AUDIT_DIR/mock"
fetch_and_save "/api/recognition/status" "recognition_status.json" "$AUDIT_DIR/mock"
fetch_and_save "/api/baselines/baseline-001/versions" "versions.json" "$AUDIT_DIR/mock"
fetch_and_save "/api/versions/baseline-001::v1.0.0" "version_snapshot.json" "$AUDIT_DIR/mock"
fetch_and_save "/api/versions/diff?from_version=baseline-001::v1.0.0&to_version=baseline-001::v1.1.0" "version_diff.json" "$AUDIT_DIR/mock"
fetch_and_save "/api/runs" "runs.json" "$AUDIT_DIR/mock"
fetch_and_save "/api/runs/run-001" "run_detail.json" "$AUDIT_DIR/mock"
fetch_and_save "/api/bundles/bundle-001" "bundle.json" "$AUDIT_DIR/mock"
fetch_and_save "/api/issues/issue-001" "issue_detail.json" "$AUDIT_DIR/mock"
fetch_and_save "/api/diff/recheck?base_run_id=run-001&target_run_id=run-002" "recheck_diff.json" "$AUDIT_DIR/mock"

echo -e "  ${GRN}✓${NC} 已收集 20 个 MockRepository 响应"

# ── Step 4: Stop Mock, start FileRepository ────────────────
echo ""
echo "── Step 4: 切换为 FileRepository 模式后端 ────────────"
echo ""

bash "$PROJECT_ROOT/scripts/dev_stop_backend.sh" > /dev/null 2>&1
sleep 1

bash "$PROJECT_ROOT/scripts/dev_start_backend_file_repo.sh" > /dev/null 2>&1
sleep 3

if ! curl -s -f --max-time 2 "$BACKEND_URL/health" > /dev/null 2>&1; then
    echo -e "  ${RED}✗${NC} FileRepository 后端启动失败"
    bash "$PROJECT_ROOT/scripts/dev_stop_backend.sh" 2>/dev/null || true
    exit 1
fi
echo -e "  ${GRN}✓${NC} FileRepository 后端已启动"

# ── Step 5: Collect FileRepository responses ───────────────
echo ""
echo "── Step 5: 收集 FileRepository 响应 ──────────────────"
echo ""

fetch_and_save "/health" "health.json" "$AUDIT_DIR/file"
fetch_and_save "/api/baselines" "baselines.json" "$AUDIT_DIR/file"
fetch_and_save "/api/baselines/baseline-001" "baseline_detail.json" "$AUDIT_DIR/file"
fetch_and_save "/api/rules/definitions" "rule_definitions.json" "$AUDIT_DIR/file"
fetch_and_save "/api/rulesets" "rulesets.json" "$AUDIT_DIR/file"
fetch_and_save "/api/profiles/parameters" "parameter_profiles.json" "$AUDIT_DIR/file"
fetch_and_save "/api/profiles/thresholds" "threshold_profiles.json" "$AUDIT_DIR/file"
fetch_and_save "/api/scopes/selectors" "scope_selectors.json" "$AUDIT_DIR/file"
fetch_and_save "/api/data-sources" "data_sources.json" "$AUDIT_DIR/file"
fetch_and_save "/api/scopes" "execution_scopes.json" "$AUDIT_DIR/file"
fetch_and_save "/api/recognition/status" "recognition_status.json" "$AUDIT_DIR/file"
fetch_and_save "/api/baselines/baseline-001/versions" "versions.json" "$AUDIT_DIR/file"
fetch_and_save "/api/versions/baseline-001::v1.0.0" "version_snapshot.json" "$AUDIT_DIR/file"
fetch_and_save "/api/versions/diff?from_version=baseline-001::v1.0.0&to_version=baseline-001::v1.1.0" "version_diff.json" "$AUDIT_DIR/file"
fetch_and_save "/api/runs" "runs.json" "$AUDIT_DIR/file"
fetch_and_save "/api/runs/run-001" "run_detail.json" "$AUDIT_DIR/file"
fetch_and_save "/api/bundles/bundle-001" "bundle.json" "$AUDIT_DIR/file"
fetch_and_save "/api/issues/issue-001" "issue_detail.json" "$AUDIT_DIR/file"
fetch_and_save "/api/diff/recheck?base_run_id=run-001&target_run_id=run-002" "recheck_diff.json" "$AUDIT_DIR/file"

echo -e "  ${GRN}✓${NC} 已收集 20 个 FileRepository 响应"

# ── Step 6: Compare responses ──────────────────────────────
echo ""
echo "── Step 6: 响应对比 ──────────────────────────────────"
echo ""

compare_response() {
    local filename="$1"
    local label="$2"

    local mock_file="$AUDIT_DIR/mock/$filename"
    local file_file="$AUDIT_DIR/file/$filename"

    if [ ! -f "$mock_file" ] || [ ! -f "$file_file" ]; then
        skip "$label - 文件缺失"
        return
    fi

    local mock_resp
    local file_resp
    mock_resp=$(cat "$mock_file")
    file_resp=$(cat "$file_file")

    if [ "$mock_resp" = "$file_resp" ]; then
        match "$label"
    else
        mismatch "$label"
        # Show diff summary
        local diff_out
        diff_out=$(diff -u "$mock_file" "$file_file" 2>/dev/null | head -20)
        if [ -n "$diff_out" ]; then
            echo "    差异摘要："
            echo "$diff_out" | sed 's/^/      /'
        fi
    fi
}

compare_response "health.json" "Health"
compare_response "baselines.json" "Baseline 列表"
compare_response "baseline_detail.json" "Baseline 详情"
compare_response "rule_definitions.json" "Rule Definitions"
compare_response "rulesets.json" "Rule Sets"
compare_response "parameter_profiles.json" "Parameter Profiles"
compare_response "threshold_profiles.json" "Threshold Profiles"
compare_response "scope_selectors.json" "Scope Selectors"
compare_response "data_sources.json" "Data Sources"
compare_response "execution_scopes.json" "Execution Scopes"
compare_response "recognition_status.json" "Recognition Status"
compare_response "versions.json" "Version 列表"
compare_response "version_snapshot.json" "Version Snapshot"
compare_response "version_diff.json" "Version Diff"
compare_response "runs.json" "Run 历史"
compare_response "run_detail.json" "Run 详情"
compare_response "bundle.json" "Bundle"
compare_response "issue_detail.json" "Issue Detail"
compare_response "recheck_diff.json" "Recheck Diff"

# ── Step 7: Cleanup ────────────────────────────────────────
echo ""
echo "── Step 7: 清理 ──────────────────────────────────────"
echo ""

bash "$PROJECT_ROOT/scripts/dev_stop_backend.sh" > /dev/null 2>&1
sleep 1

echo -e "  ${GRN}✓${NC} 后端已停止"
echo -e "  ${BLU}ℹ${NC} 审计文件保留在: $AUDIT_DIR"

# ── Summary ────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════════════"
echo -e "  匹配：${GRN}${MATCH}${NC}  差异：${RED}${MISMATCH}${NC}  跳过：${YLW}${SKIP}${NC}"
echo ""

if [ $MISMATCH -gt 0 ]; then
    echo -e "  ${RED}AUDIT_RESULT: 存在差异，暂不具备默认切换条件${NC}"
    echo "══════════════════════════════════════════════════════"
    echo ""
    exit 1
else
    echo -e "  ${GRN}AUDIT_RESULT: 响应完全一致，具备默认切换条件${NC}"
    echo "══════════════════════════════════════════════════════"
    echo ""
    exit 0
fi
