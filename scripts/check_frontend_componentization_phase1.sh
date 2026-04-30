#!/usr/bin/env bash
# ============================================================
# check_frontend_componentization_phase1.sh
# TopoChecker — 前端组件化 Phase 1 静态护栏
# 检查 frontend/ 目录下的 TypeScript/TSX 迁移成果
# 用法：bash scripts/check_frontend_componentization_phase1.sh
# ============================================================
set -euo pipefail

PROJECT_ROOT="."
FRONTEND_DIR="frontend"
PASS=0
FAIL=0
ERRORS=()

RED='\033[0;31m'; GRN='\033[0;32m'; YLW='\033[1;33m'; NC='\033[0m'

pass() { echo -e "  ${GRN}✓${NC} $1"; PASS=$((PASS+1)); }
fail() { echo -e "  ${RED}✗${NC} $1"; FAIL=$((FAIL+1)); ERRORS+=("$1"); }

check_file() {
  local label="$1" path="$2"
  if [ -f "$path" ]; then pass "$label 存在: $path";
  else fail "$label 不存在: $path"; fi
}

check_present_in() {
  local label="$1" pattern="$2" file="$3"
  if [ -f "$file" ] && grep -qE "$pattern" "$file" 2>/dev/null; then
    pass "$label ($file)";
  else
    fail "缺失: $label in $file ($pattern)";
  fi
}

check_absent_in_dir() {
  local label="$1" pattern="$2" dir="$3"
  local matches
  local EXCLUDE_DIRS="node_modules|dist|build|\.next|coverage|\.git"
  matches=$(find "$dir" -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.html" \) -exec grep -lF "$pattern" {} \; 2>/dev/null | grep -vE "/($EXCLUDE_DIRS)/" || true)
  if [ -z "$matches" ]; then
    pass "无禁止词: $label";
  else
    fail "禁止词 '$pattern' 出现于: $(echo "$matches" | tr '\n' ' ')";
  fi
}

echo ""
echo "══════════════════════════════════════════════════════"
echo "  TopoChecker 前端组件化 Phase 1 静态护栏"
echo "  目标目录：$FRONTEND_DIR/"
echo "══════════════════════════════════════════════════════"
echo ""

if [ ! -d "$FRONTEND_DIR" ]; then
  echo -e "${RED}[FATAL] frontend/ 目录不存在${NC}"
  exit 1
fi

# ── Section 1: TypeScript 模型文件 ────────────────────────────
echo "── Section 1：TypeScript 模型文件 ──"
check_file "profile.ts"    "$FRONTEND_DIR/src/models/profile.ts"
check_file "scope.ts"      "$FRONTEND_DIR/src/models/scope.ts"
check_file "baseline.ts"   "$FRONTEND_DIR/src/models/baseline.ts"
check_file "execution.ts"  "$FRONTEND_DIR/src/models/execution.ts"
check_file "diff.ts"       "$FRONTEND_DIR/src/models/diff.ts"
check_file "version.ts"    "$FRONTEND_DIR/src/models/version.ts"
echo ""

# ── Section 2: Mock 文件 ──────────────────────────────────────
echo "── Section 2：Mock 数据文件 ──"
check_file "profiles.mock.ts"  "$FRONTEND_DIR/src/mocks/profiles.mock.ts"
check_file "execution.mock.ts" "$FRONTEND_DIR/src/mocks/execution.mock.ts"
check_file "diff.mock.ts"      "$FRONTEND_DIR/src/mocks/diff.mock.ts"
check_file "version.mock.ts"   "$FRONTEND_DIR/src/mocks/version.mock.ts"
echo ""

# ── Section 3: 页面组件文件 ───────────────────────────────────
echo "── Section 3：页面组件文件 ──"
check_file "ExecutionConfigPage.tsx"    "$FRONTEND_DIR/src/pages/ExecutionConfigPage.tsx"
check_file "DiffComparePage.tsx"        "$FRONTEND_DIR/src/pages/DiffComparePage.tsx"
check_file "VersionManagementPage.tsx"  "$FRONTEND_DIR/src/pages/VersionManagementPage.tsx"
check_file "AnalysisWorkbenchPage.tsx"  "$FRONTEND_DIR/src/pages/AnalysisWorkbenchPage.tsx"
check_file "RunHistoryPage.tsx"         "$FRONTEND_DIR/src/pages/RunHistoryPage.tsx"
check_file "BaselineDetailPage.tsx"    "$FRONTEND_DIR/src/pages/BaselineDetailPage.tsx"
check_file "RuleEditorPage.tsx"        "$FRONTEND_DIR/src/pages/RuleEditorPage.tsx"
check_file "App.tsx"                   "$FRONTEND_DIR/App.tsx"
echo ""

# ── Section 4: 关键模型内容存在性 ────────────────────────────
echo "── Section 4：关键模型内容 ──"
check_present_in "RecheckDiffSnapshot 类型"    "RecheckDiffSnapshot"   "$FRONTEND_DIR/src/models/diff.ts"
check_present_in "WorkbenchDrilldownContext"   "WorkbenchDrilldownContext" "$FRONTEND_DIR/src/models/diff.ts"
check_present_in "VersionDiffSnapshot 类型"    "VersionDiffSnapshot"   "$FRONTEND_DIR/src/models/version.ts"
check_present_in "VersionChangeSummary 类型"   "VersionChangeSummary"  "$FRONTEND_DIR/src/models/version.ts"
check_present_in "RecognitionStatus 类型"      "RecognitionStatus"     "$FRONTEND_DIR/src/models/execution.ts"
check_present_in "IssueItem 类型"              "IssueItem"             "$FRONTEND_DIR/src/models/execution.ts"
echo ""

# ── Section 5: Mock 数据关键常量存在 ─────────────────────────
echo "── Section 5：Mock 关键常量 ──"
check_present_in "RECHECK_DIFF_SNAPSHOTS" "RECHECK_DIFF_SNAPSHOTS" "$FRONTEND_DIR/src/mocks/diff.mock.ts"
check_present_in "VERSION_DIFF_SNAPSHOTS" "VERSION_DIFF_SNAPSHOTS" "$FRONTEND_DIR/src/mocks/version.mock.ts"
check_present_in "VERSION_CHANGE_SUMMARIES" "VERSION_CHANGE_SUMMARIES" "$FRONTEND_DIR/src/mocks/version.mock.ts"
check_present_in "VERSION_SNAPSHOTS" "VERSION_SNAPSHOTS" "$FRONTEND_DIR/src/mocks/version.mock.ts"
check_present_in "RECOGNITION_RESULTS" "RECOGNITION_RESULTS" "$FRONTEND_DIR/src/mocks/execution.mock.ts"
echo ""

# ── Section 6: P0/P1/P2 关键边界检查 ──────────────────────────
echo "── Section 6：P0/P1/P2 关键边界 ──"
check_present_in "ExecutionConfig 使用 recognitionStatus" "recognitionStatus" "$FRONTEND_DIR/src/pages/ExecutionConfigPage.tsx"
check_present_in "ExecutionConfig 有 canCheck 禁用" "canCheck" "$FRONTEND_DIR/src/pages/ExecutionConfigPage.tsx"
check_present_in "ExecutionConfig 确认 baseline 确认" "confirmed" "$FRONTEND_DIR/src/pages/ExecutionConfigPage.tsx"
check_present_in "DiffCompare 使用 drilldown 上下文" "onDrilldownToWorkbench" "$FRONTEND_DIR/src/pages/DiffComparePage.tsx"
check_present_in "baseline.ts 有 rule_overrides 结构" "rule_overrides" "$FRONTEND_DIR/src/models/baseline.ts"
# Check VersionMgmt uses either VERSION_DIFF_SNAPSHOTS or getVersionDiff
if [ -f "$FRONTEND_DIR/src/pages/VersionManagementPage.tsx" ]; then
  if grep -qi "VERSION_DIFF_SNAPSHOTS\|getVersionDiff" "$FRONTEND_DIR/src/pages/VersionManagementPage.tsx" 2>/dev/null; then
    pass "VersionMgmt 使用 VERSION_DIFF_SNAPSHOTS 或 getVersionDiff";
  else
    fail "VersionMgmt 未使用 VERSION_DIFF_SNAPSHOTS 或 getVersionDiff";
  fi
fi
check_present_in "VersionMgmt 使用 VERSION_CHANGE_SUMMARIES" "VERSION_CHANGE_SUMMARIES" "$FRONTEND_DIR/src/pages/VersionManagementPage.tsx"
# Check VersionMgmt uses either VERSION_SNAPSHOTS or getVersionSnapshot
if [ -f "$FRONTEND_DIR/src/pages/VersionManagementPage.tsx" ]; then
  if grep -qi "VERSION_SNAPSHOTS\|getVersionSnapshot" "$FRONTEND_DIR/src/pages/VersionManagementPage.tsx" 2>/dev/null; then
    pass "VersionMgmt 使用 VERSION_SNAPSHOTS 或 getVersionSnapshot";
  else
    fail "VersionMgmt 未使用 VERSION_SNAPSHOTS 或 getVersionSnapshot";
  fi
fi
echo ""

# ── Section 6b: Workbench Phase 2 护栏 ──────────────────────
echo "── Section 6b：Workbench Phase 2 护栏 ──"
check_present_in "WorkbenchDrilldownContext (Workbench)" "WorkbenchDrilldownContext" "$FRONTEND_DIR/src/pages/AnalysisWorkbenchPage.tsx"
check_present_in "CheckResultBundle (Workbench)" "CheckResultBundle" "$FRONTEND_DIR/src/pages/AnalysisWorkbenchPage.tsx"
check_present_in "Workbench 中 issue_diff_item" "issue_diff_item" "$FRONTEND_DIR/src/pages/AnalysisWorkbenchPage.tsx"
check_present_in "Workbench 中 diff_type" "diff_type" "$FRONTEND_DIR/src/pages/AnalysisWorkbenchPage.tsx"
check_present_in "Workbench 中 from_run_id" "from_run_id" "$FRONTEND_DIR/src/pages/AnalysisWorkbenchPage.tsx"
check_present_in "Workbench 中 to_run_id" "to_run_id" "$FRONTEND_DIR/src/pages/AnalysisWorkbenchPage.tsx"
echo ""

# ── Section 6c: App.tsx Workbench 占位检查 ──────────────────
echo "── Section 6c：App.tsx Workbench 占位移除检查 ──"
if grep -q "TODO Phase 2.*workbench\|Phase 2 待迁移.*Workbench" "$FRONTEND_DIR/App.tsx" 2>/dev/null; then
  fail "App.tsx 仍包含 workbench TODO 占位文案";
else
  pass "App.tsx 无 workbench TODO 占位文案";
fi
echo ""

# ── Section 6d: RunHistoryPage Phase 2 护栏 ─────────────────
echo "── Section 6d：RunHistoryPage Phase 2 护栏 ──"
check_present_in "RunHistory 中 RunHistoryEntry" "RunHistoryEntry" "$FRONTEND_DIR/src/models/execution.ts"
check_present_in "RunHistoryPage 中 run_id" "run_id" "$FRONTEND_DIR/src/pages/RunHistoryPage.tsx"
check_present_in "RunHistoryPage 中 baseline_id" "baseline_id" "$FRONTEND_DIR/src/pages/RunHistoryPage.tsx"
check_present_in "RunHistoryPage 中 status" "status" "$FRONTEND_DIR/src/pages/RunHistoryPage.tsx"
check_present_in "RunHistoryPage 中 severity_summary" "severity_summary" "$FRONTEND_DIR/src/pages/RunHistoryPage.tsx"
check_present_in "RunHistoryPage 中 data_source_id" "data_source_id" "$FRONTEND_DIR/src/pages/RunHistoryPage.tsx"
check_present_in "RunHistoryPage 中 scope_id" "scope_id" "$FRONTEND_DIR/src/pages/RunHistoryPage.tsx"
check_present_in "RunHistoryPage 使用 CheckResultBundle" "CheckResultBundle" "$FRONTEND_DIR/src/pages/RunHistoryPage.tsx"
check_present_in "RunHistory 跳转到 Workbench" "onNavigateToWorkbench" "$FRONTEND_DIR/src/pages/RunHistoryPage.tsx"
check_present_in "App.tsx 已配置 history 页面入口" "'history'" "$FRONTEND_DIR/App.tsx"
echo ""

# ── Section 6e: BaselineDetailPage Phase 2 护栏 ──────────────
echo "── Section 6e：BaselineDetailPage Phase 2 护栏 ──"
check_present_in "BaselineDetailPage 存在" "BaselineDetailPage" "$FRONTEND_DIR/src/pages/BaselineDetailPage.tsx"
check_present_in "BaselineDetailPage 中 ParameterProfile" "ParameterProfile" "$FRONTEND_DIR/src/pages/BaselineDetailPage.tsx"
check_present_in "BaselineDetailPage 中 ThresholdProfile" "ThresholdProfile" "$FRONTEND_DIR/src/pages/BaselineDetailPage.tsx"
check_present_in "BaselineDetailPage 中 ScopeSelector" "ScopeSelector" "$FRONTEND_DIR/src/pages/BaselineDetailPage.tsx"
check_present_in "BaselineDetailPage 中 RuleSet" "RuleSet" "$FRONTEND_DIR/src/pages/BaselineDetailPage.tsx"
check_present_in "BaselineDetailPage 中 RuleDefinition" "RuleDefinition" "$FRONTEND_DIR/src/pages/BaselineDetailPage.tsx"
check_present_in "BaselineDetailPage 中 baseline_id" "baseline_id" "$FRONTEND_DIR/src/pages/BaselineDetailPage.tsx"
check_present_in "BaselineDetailPage 中 version" "version" "$FRONTEND_DIR/src/pages/BaselineDetailPage.tsx"
check_present_in "App.tsx 已配置 baseline 页面入口" "'baseline'" "$FRONTEND_DIR/App.tsx"
# No outbound editing buttons in BaselineDetail
if grep -qE "Edit Rule|Version History|发布此版本|执行检查" "$FRONTEND_DIR/src/pages/BaselineDetailPage.tsx" 2>/dev/null; then
  fail "BaselineDetailPage 包含越界入口按钮";
else
  pass "BaselineDetailPage 无越界入口按钮";
fi
echo ""

# ── Section 6f: RuleEditorPage Phase 2 护栏 ─────────────────
echo "── Section 6f：RuleEditorPage Phase 2 护栏 ──"
check_file "RuleEditorPage.tsx" "$FRONTEND_DIR/src/pages/RuleEditorPage.tsx"
check_present_in "RuleEditorPage 中 RuleSet" "RuleSet" "$FRONTEND_DIR/src/pages/RuleEditorPage.tsx"
check_present_in "RuleEditorPage 中 rule_overrides" "rule_overrides" "$FRONTEND_DIR/src/pages/RuleEditorPage.tsx"
check_present_in "RuleEditorPage 中 ParameterProfile" "ParameterProfile" "$FRONTEND_DIR/src/pages/RuleEditorPage.tsx"
check_present_in "RuleEditorPage 中 ThresholdProfile" "ThresholdProfile" "$FRONTEND_DIR/src/pages/RuleEditorPage.tsx"
check_present_in "RuleEditorPage 中 ScopeSelector" "ScopeSelector" "$FRONTEND_DIR/src/pages/RuleEditorPage.tsx"
check_present_in "RuleEditorPage 中 typed input" "TypedInput" "$FRONTEND_DIR/src/pages/RuleEditorPage.tsx"
check_present_in "App.tsx 已配置 rule-editor 页面入口" "'rule-editor'" "$FRONTEND_DIR/App.tsx"
# RuleEditor must NOT edit condition DSL
if grep -q "condition.*onChange\|condition.*onInput" "$FRONTEND_DIR/src/pages/RuleEditorPage.tsx" 2>/dev/null; then
  fail "RuleEditorPage 允许编辑 condition（禁止）";
else
  pass "RuleEditorPage condition 只读";
fi
# No version publishing / rollback / execution triggers
if grep -qE "Publish Version|Rollback|执行检查|Execute Check" "$FRONTEND_DIR/src/pages/RuleEditorPage.tsx" 2>/dev/null; then
  fail "RuleEditorPage 包含越界入口";
else
  pass "RuleEditorPage 无越界入口";
fi
echo ""

# ── Section 6g: UI 样式文件 Phase 3 ───────────────────────
echo "── Section 6g：UI 样式文件检查 ──"
check_file "design-tokens.css" "$FRONTEND_DIR/src/styles/design-tokens.css"
check_file "app.css" "$FRONTEND_DIR/src/styles/app.css"
check_present_in "App.tsx 引入 design-tokens.css" "design-tokens.css" "$FRONTEND_DIR/App.tsx"
check_present_in "App.tsx 引入 app.css" "app.css" "$FRONTEND_DIR/App.tsx"
echo ""

# ── Section 6h: 响应式 UI Polish Phase 3.1 ───────────────────
echo "── Section 6h：响应式 UI Polish 检查 ──"
# Breakpoint tokens - design tokens only has breakpoint references (not media queries)
check_present_in "design-tokens 包含断点参考注释" "sm:" "$FRONTEND_DIR/src/styles/design-tokens.css"
# Media queries in app.css
check_present_in "app.css 包含 tablet breakpoint" "@media \(max-width: 1024px\)" "$FRONTEND_DIR/src/styles/app.css"
check_present_in "app.css 包含 mobile breakpoint" "@media \(max-width: 768px\)" "$FRONTEND_DIR/src/styles/app.css"
# Table overflow handling
check_present_in "app.css 包含 overflow-x" "overflow-x" "$FRONTEND_DIR/src/styles/app.css"
check_present_in "app.css 包含 table-container" "table-container" "$FRONTEND_DIR/src/styles/app.css"
# Empty state
check_present_in "app.css 包含 empty-state" "empty-state" "$FRONTEND_DIR/src/styles/app.css"
check_present_in "app.css 包含 empty-icon" "empty-icon" "$FRONTEND_DIR/src/styles/app.css"
check_present_in "app.css 包含 empty-title" "empty-title" "$FRONTEND_DIR/src/styles/app.css"
# Detail panel
check_present_in "app.css 包含 detail-pane" "detail-pane" "$FRONTEND_DIR/src/styles/app.css"
check_present_in "app.css 包含 detail-header" "detail-header" "$FRONTEND_DIR/src/styles/app.css"
check_present_in "app.css 包含 detail-tabs" "detail-tabs" "$FRONTEND_DIR/src/styles/app.css"
check_present_in "app.css 包含 tab-btn" "tab-btn" "$FRONTEND_DIR/src/styles/app.css"
# Responsive grid
check_present_in "app.css 包含 media query 响应式" "work-area" "$FRONTEND_DIR/src/styles/app.css"
check_present_in "app.css 包含 history-content" "history-content" "$FRONTEND_DIR/src/styles/app.css"
echo ""

# ── Section 6i: 视觉一致性检查 Phase 3.2 ─────────────────────
echo "── Section 6i：视觉一致性检查 ──"
# All 7 pages use page-header class
check_present_in "VersionManagementPage page-header"    "page-header" "$FRONTEND_DIR/src/pages/VersionManagementPage.tsx"
check_present_in "DiffComparePage page-header"          "page-header" "$FRONTEND_DIR/src/pages/DiffComparePage.tsx"
check_present_in "ExecutionConfigPage page-header"     "page-header" "$FRONTEND_DIR/src/pages/ExecutionConfigPage.tsx"
check_present_in "AnalysisWorkbenchPage page-header"   "page-header" "$FRONTEND_DIR/src/pages/AnalysisWorkbenchPage.tsx"
check_present_in "RunHistoryPage page-header"           "page-header" "$FRONTEND_DIR/src/pages/RunHistoryPage.tsx"
check_present_in "BaselineDetailPage page-header"      "page-header" "$FRONTEND_DIR/src/pages/BaselineDetailPage.tsx"
check_present_in "RuleEditorPage page-header"          "page-header" "$FRONTEND_DIR/src/pages/RuleEditorPage.tsx"
# No <h1> page titles — use page-title class instead
if grep -q "<h1>" "$FRONTEND_DIR/src/pages/"*.tsx 2>/dev/null; then
  fail "页面使用 <h1> 而非 page-title class";
else
  pass "所有页面使用 page-title div 而非 <h1>";
fi
# All 7 pages use unified btn classes (btn btn-primary etc)
check_present_in "ExecutionConfigPage btn-primary"     "btn btn-primary" "$FRONTEND_DIR/src/pages/ExecutionConfigPage.tsx"
check_present_in "DiffComparePage btn-primary"        "btn btn-primary" "$FRONTEND_DIR/src/pages/DiffComparePage.tsx"
# app.css has detail-panel / empty-state / table-container
check_present_in "app.css detail-panel"              "detail-panel"  "$FRONTEND_DIR/src/styles/app.css"
check_present_in "app.css empty-state"               "empty-state"   "$FRONTEND_DIR/src/styles/app.css"
check_present_in "app.css table-container"            "table-container" "$FRONTEND_DIR/src/styles/app.css"
check_present_in "app.css drilldown-banner"          "drilldown-banner" "$FRONTEND_DIR/src/styles/app.css"
check_present_in "app.css version-row"               "version-row"  "$FRONTEND_DIR/src/styles/app.css"
check_present_in "app.css change-badges"             "change-badges" "$FRONTEND_DIR/src/styles/app.css"
check_present_in "app.css diff-run-selector"         "diff-run-selector" "$FRONTEND_DIR/src/styles/app.css"
check_present_in "app.css diff-detail-panel"         "diff-detail-panel" "$FRONTEND_DIR/src/styles/app.css"
check_present_in "app.css panel-header"              "panel-header"  "$FRONTEND_DIR/src/styles/app.css"
echo ""

# ── Section 7: 禁止词扫描（全 frontend/ 目录）────────────────
echo "── Section 7：禁止词扫描 ──"
for pat in "idsA" "idsB" "newIssues" "removedIssues" "ra.diff_summary" \
           "addedRules" "removedRules" "oldRuleIds" "newRuleIds"; do
  check_absent_in_dir "$pat" "$pat" "$FRONTEND_DIR"
done
# Version diff UI computation patterns
check_absent_in_dir "new Set(old" "new Set(old" "$FRONTEND_DIR"
check_absent_in_dir "new Set(new" "new Set(new" "$FRONTEND_DIR"
echo ""

# ── Section 8: any 类型审计 ─────────────────────────────────
echo "── Section 8：any 类型审计 ──"
if [ -d "$FRONTEND_DIR/src/models" ]; then
  any_count=$(grep -r ": any" "$FRONTEND_DIR/src/models/" 2>/dev/null | grep -v "//.*: any" | wc -l | tr -d ' ' || true)
  if [ "$any_count" -eq 0 ]; then
    pass "models/ 中无裸 ': any' 类型";
  else
    fail "models/ 中发现 $any_count 处 ': any' 类型（禁止滥用 any）";
  fi
fi
echo ""

# ── Section 9: 工程基线文件（Phase 2 新增）─────────────────────
echo "── Section 9：工程基线文件 ──"
check_file "package.json"  "$FRONTEND_DIR/package.json"
check_file "tsconfig.json" "$FRONTEND_DIR/tsconfig.json"
if [ -f "$FRONTEND_DIR/package.json" ] && grep -qF '"typecheck"' "$FRONTEND_DIR/package.json" 2>/dev/null; then
  pass "package.json 包含 typecheck script";
else
  fail "package.json 缺少 typecheck script";
fi
if [ -f "$FRONTEND_DIR/tsconfig.json" ] && grep -qF '"strict": true' "$FRONTEND_DIR/tsconfig.json" 2>/dev/null; then
  pass "tsconfig.json strict: true";
else
  fail "tsconfig.json 缺少 strict: true";
fi
if [ -f "$FRONTEND_DIR/tsconfig.json" ] && grep -qF '"noImplicitAny": true' "$FRONTEND_DIR/tsconfig.json" 2>/dev/null; then
  pass "tsconfig.json noImplicitAny: true";
else
  fail "tsconfig.json 缺少 noImplicitAny: true";
fi
echo ""

# ── Section 10: 7 个页面访问性检查 ────────────────────────
echo "── Section 10：7 个页面访问性检查 ──"
check_present_in "App.tsx 包含 execution 页面入口" "'execution'" "$FRONTEND_DIR/App.tsx"
check_present_in "App.tsx 包含 diff 页面入口" "'diff'" "$FRONTEND_DIR/App.tsx"
check_present_in "App.tsx 包含 version 页面入口" "'version'" "$FRONTEND_DIR/App.tsx"
check_present_in "App.tsx 包含 workbench 页面入口" "'workbench'" "$FRONTEND_DIR/App.tsx"
check_present_in "App.tsx 包含 history 页面入口" "'history'" "$FRONTEND_DIR/App.tsx"
check_present_in "App.tsx 包含 baseline 页面入口" "'baseline'" "$FRONTEND_DIR/App.tsx"
check_present_in "App.tsx 包含 rule-editor 页面入口" "'rule-editor'" "$FRONTEND_DIR/App.tsx"
echo ""

# ── Section 11: API Contract 准备层检查（Phase4 新增）─────────────────
echo "── Section 11：API Contract 准备层检查 ──"
check_file "api/contracts.ts" "$FRONTEND_DIR/src/api/contracts.ts"
check_file "api/client.ts" "$FRONTEND_DIR/src/api/client.ts"
check_file "api/mockClient.ts" "$FRONTEND_DIR/src/api/mockClient.ts"
check_file "api/README.md" "$FRONTEND_DIR/src/api/README.md"
# Check client.ts has no real fetch/URLs/libs
if [ -f "$FRONTEND_DIR/src/api/client.ts" ]; then
  if grep -qi "fetch\|axios\|react-query\|swr\|https?://" "$FRONTEND_DIR/src/api/client.ts" 2>/dev/null; then
    fail "client.ts 包含禁止内容（fetch/axios/react-query/swr/URL）";
  else
    pass "client.ts 无禁止内容（fetch/axios/react-query/swr/URL）";
  fi
fi
# Check mockClient doesn't use forbidden libs
if [ -f "$FRONTEND_DIR/src/api/mockClient.ts" ]; then
  if grep -qi "axios\|react-query\|swr" "$FRONTEND_DIR/src/api/mockClient.ts" 2>/dev/null; then
    fail "mockClient.ts 包含禁止库（axios/react-query/swr）";
  else
    pass "mockClient.ts 无禁止库（axios/react-query/swr）";
  fi
fi
# Check contracts has key endpoint types
check_present_in "contracts.ts 有 GetBaselineListResponse" "GetBaselineListResponse" "$FRONTEND_DIR/src/api/contracts.ts"
check_present_in "client.ts 有 ApiClient interface" "ApiClient" "$FRONTEND_DIR/src/api/client.ts"
echo ""

# ── Section 12: API Adapter/Service 层检查（Phase4.1 新增）──────────────────
echo "── Section 12：API Adapter/Service 层检查 ──"
check_file "api/services.ts" "$FRONTEND_DIR/src/api/services.ts"
check_file "api/index.ts" "$FRONTEND_DIR/src/api/index.ts"
# Check VersionManagementPage doesn't import VERSION_SNAPSHOTS/VERSION_DIFF_SNAPSHOTS directly from version.mock
if [ -f "$FRONTEND_DIR/src/pages/VersionManagementPage.tsx" ]; then
  # Check for import statements only
  if grep -i "^import" "$FRONTEND_DIR/src/pages/VersionManagementPage.tsx" | grep -qi "VERSION_SNAPSHOTS\|VERSION_DIFF_SNAPSHOTS" 2>/dev/null; then
    fail "VersionManagementPage 直接导入 VERSION_SNAPSHOTS/VERSION_DIFF_SNAPSHOTS";
  elif grep -qi "import.*VERSION_CHANGE_SUMMARIES" "$FRONTEND_DIR/src/pages/VersionManagementPage.tsx" 2>/dev/null; then
    pass "VersionManagementPage 仅导入 VERSION_CHANGE_SUMMARIES";
  else
    pass "VersionManagementPage 不直接导入 version.mock 中的快照/diff";
  fi
fi
# Check DiffComparePage doesn't import directly from diff.mock
if [ -f "$FRONTEND_DIR/src/pages/DiffComparePage.tsx" ]; then
  if grep -qi "from.*diff\.mock" "$FRONTEND_DIR/src/pages/DiffComparePage.tsx" 2>/dev/null; then
    fail "DiffComparePage 直接导入 diff.mock";
  else
    pass "DiffComparePage 不直接导入 diff.mock";
  fi
fi
# Check no pages use forbidden libs
for page_file in "$FRONTEND_DIR/src/pages"/*.tsx; do
  if [ -f "$page_file" ]; then
    if grep -qi "fetch\|axios\|react-query\|swr" "$page_file" 2>/dev/null; then
      filename=$(basename "$page_file")
      fail "$filename 包含禁止内容（fetch/axios/react-query/swr）";
    else
      filename=$(basename "$page_file")
      pass "$filename 无禁止内容（fetch/axios/react-query/swr）";
    fi
  fi
done
echo ""

# ── Section 12b: API Adapter/Service 层 Phase4.2 扩展检查 ─────────────────
echo "── Section 12b：Phase4.2 剩余页面迁移检查 ──"
# Check remaining 5 pages don't directly import from mocks
for page in "ExecutionConfigPage" "AnalysisWorkbenchPage" "RunHistoryPage" "BaselineDetailPage" "RuleEditorPage"; do
  page_file="$FRONTEND_DIR/src/pages/${page}.tsx"
  if [ -f "$page_file" ]; then
    if grep -qi "from.*mocks" "$page_file" 2>/dev/null; then
      fail "${page} 直接导入 mocks";
    else
      pass "${page} 不直接导入 mocks";
    fi
  fi
done
# Check services.ts covers all domains
check_present_in "services.ts 覆盖 baseline" "getBaselineProfileMapEntry|getBaselineVersionSnapshot" "$FRONTEND_DIR/src/api/services.ts"
check_present_in "services.ts 覆盖 execution" "getDataSourceList|getScopeList|getRecognitionStatus|startRecognition" "$FRONTEND_DIR/src/api/services.ts"
check_present_in "services.ts 覆盖 workbench" "getCheckResultBundle|getIssueDetail" "$FRONTEND_DIR/src/api/services.ts"
check_present_in "services.ts 覆盖 history" "getRunHistory|getRunDetail" "$FRONTEND_DIR/src/api/services.ts"
check_present_in "services.ts 覆盖 rule" "getRuleDefinitions|getRuleSetList|updateRuleOverride" "$FRONTEND_DIR/src/api/services.ts"
check_present_in "services.ts 覆盖 profile/scope" "getParameterProfileList|getThresholdProfileList|getScopeSelectorList" "$FRONTEND_DIR/src/api/services.ts"

# ── Section 12c: API Client Switching Scaffold Phase4.3 检查 ──────────────
echo "── Section 12c：Phase4.3 Client Switching Scaffold 检查 ──"
check_file "realClient.ts 存在" "$FRONTEND_DIR/src/api/realClient.ts"
check_file "provider.ts 存在" "$FRONTEND_DIR/src/api/provider.ts"

# Check services.ts imports from provider, not directly from mockClient
if [ -f "$FRONTEND_DIR/src/api/services.ts" ]; then
  if grep -qi "from.*provider" "$FRONTEND_DIR/src/api/services.ts" 2>/dev/null; then
    pass "services.ts 从 provider 导入 apiClient";
  else
    fail "services.ts 未从 provider 导入 apiClient";
  fi
  if grep -qi "from.*mockClient" "$FRONTEND_DIR/src/api/services.ts" 2>/dev/null; then
    fail "services.ts 直接导入 mockClient（应通过 provider）";
  else
    pass "services.ts 不直接导入 mockClient";
  fi
fi

# Check provider.ts default is mock (uses config.ts with isMockMode)
if [ -f "$FRONTEND_DIR/src/api/provider.ts" ]; then
  if grep -qi "isMockMode\|config" "$FRONTEND_DIR/src/api/provider.ts" 2>/dev/null; then
    pass "provider.ts 使用 config.ts (默认 mock)";
  else
    fail "provider.ts 未使用 config.ts";
  fi
fi
echo ""

# ── Section 12d: API Contract Documentation Phase4.4 检查 ──────────────
echo "── Section 12d：Phase4.4 API Contract Documentation 检查 ──"
check_file "FRONTEND_BACKEND_API_CONTRACT.md 存在" "$PROJECT_ROOT/docs/api/FRONTEND_BACKEND_API_CONTRACT.md"
check_file "docs/api/README.md 存在" "$PROJECT_ROOT/docs/api/README.md"

# Check contract document contains key terms
if [ -f "$PROJECT_ROOT/docs/api/FRONTEND_BACKEND_API_CONTRACT.md" ]; then
  check_present_in "契约文档包含 RecheckDiffSnapshot" "RecheckDiffSnapshot" "$PROJECT_ROOT/docs/api/FRONTEND_BACKEND_API_CONTRACT.md"
  check_present_in "契约文档包含 VersionDiffSnapshot" "VersionDiffSnapshot" "$PROJECT_ROOT/docs/api/FRONTEND_BACKEND_API_CONTRACT.md"
  check_present_in "契约文档包含 recognition confirm" "confirmRecognition|ConfirmRecognition|recognition.*confirm" "$PROJECT_ROOT/docs/api/FRONTEND_BACKEND_API_CONTRACT.md"
  check_present_in "契约文档包含 CheckResultBundle" "CheckResultBundle" "$PROJECT_ROOT/docs/api/FRONTEND_BACKEND_API_CONTRACT.md"
  # Check for "frontend MUST NOT compute diff" or equivalent
  if grep -qi "MUST NOT compute diff\|不允许前端计算\|frontend.*not.*compute.*diff" "$PROJECT_ROOT/docs/api/FRONTEND_BACKEND_API_CONTRACT.md" 2>/dev/null; then
    pass "契约文档明确前端不计算 diff";
  else
    fail "契约文档未明确前端不计算 diff";
  fi
fi
echo ""

# ── Section 12e: Real Client Transport Phase5 检查 ──────────────────────
echo "── Section 12e：Phase5 Real Client Transport 检查 ──"
check_file "config.ts 存在" "$FRONTEND_DIR/src/api/config.ts"

# Check config.ts has default mock mode
if [ -f "$FRONTEND_DIR/src/api/config.ts" ]; then
  if grep -qi "mode.*mock\|mode:.*mock\|mode = .*mock" "$FRONTEND_DIR/src/api/config.ts" 2>/dev/null; then
    pass "config.ts 默认 mode 为 mock";
  else
    fail "config.ts 默认 mode 不是 mock";
  fi
fi

# Check provider.ts uses config.ts
if [ -f "$FRONTEND_DIR/src/api/provider.ts" ]; then
  if grep -qi "from.*config\|isMockMode\|isRealMode" "$FRONTEND_DIR/src/api/provider.ts" 2>/dev/null; then
    pass "provider.ts 使用 config.ts";
  else
    fail "provider.ts 未使用 config.ts";
  fi
fi

# Check realClient.ts uses config.ts and fetch
if [ -f "$FRONTEND_DIR/src/api/realClient.ts" ]; then
  if grep -qi "from.*config\|getBaseUrl\|isRealMode" "$FRONTEND_DIR/src/api/realClient.ts" 2>/dev/null; then
    pass "realClient.ts 使用 config.ts";
  else
    fail "realClient.ts 未使用 config.ts";
  fi
  if grep -qi "fetch" "$FRONTEND_DIR/src/api/realClient.ts" 2>/dev/null; then
    pass "realClient.ts 使用 native fetch";
  else
    fail "realClient.ts 未使用 fetch";
  fi
fi

# Check realClient.ts has no forbidden libs (excluding comments)
if [ -f "$FRONTEND_DIR/src/api/realClient.ts" ]; then
  if grep -v '^//' "$FRONTEND_DIR/src/api/realClient.ts" | grep -qi "axios\|react-query\|swr" 2>/dev/null; then
    fail "realClient.ts 包含禁止库（axios/react-query/swr）";
  else
    pass "realClient.ts 无禁止库";
  fi
fi

# Check config.ts and provider.ts have no production URLs
for f in "$FRONTEND_DIR/src/api/config.ts" "$FRONTEND_DIR/src/api/provider.ts"; do
  if [ -f "$f" ]; then
    if grep -v '^//' "$f" | grep -qi "https://.*\.\|http://production\|https://production" 2>/dev/null; then
      fail "$(basename $f) 包含生产 URL";
    else
      pass "$(basename $f) 无生产 URL";
    fi
  fi
done

# ── Section 12f: Real Client Guard Hardening Phase6 检查 ──────────────
echo "── Section 12f：Phase6 Real Client Guard Hardening 检查 ──"

# Check DEFAULT_API_MODE exists and is mock
if [ -f "$FRONTEND_DIR/src/api/config.ts" ]; then
  if grep -qi "DEFAULT_API_MODE.*mock\|DEFAULT_API_MODE:.*mock\|const DEFAULT_API_MODE.*mock" "$FRONTEND_DIR/src/api/config.ts" 2>/dev/null; then
    pass "config.ts DEFAULT_API_MODE 为 mock";
  else
    fail "config.ts 缺少 DEFAULT_API_MODE 或不是 mock";
  fi
fi

# Check resetApiConfig exists
if [ -f "$FRONTEND_DIR/src/api/config.ts" ]; then
  if grep -qi "resetApiConfig" "$FRONTEND_DIR/src/api/config.ts" 2>/dev/null; then
    pass "config.ts 有 resetApiConfig";
  else
    fail "config.ts 缺少 resetApiConfig";
  fi
fi

# Check isLocalBaseUrl exists in config.ts
if [ -f "$FRONTEND_DIR/src/api/config.ts" ]; then
  if grep -qi "isLocalBaseUrl" "$FRONTEND_DIR/src/api/config.ts" 2>/dev/null; then
    pass "config.ts 有 isLocalBaseUrl";
  else
    fail "config.ts 缺少 isLocalBaseUrl";
  fi
fi

# Check provider.ts uses isLocalBaseUrl (fallback to mock)
if [ -f "$FRONTEND_DIR/src/api/provider.ts" ]; then
  if grep -qi "isLocalBaseUrl" "$FRONTEND_DIR/src/api/provider.ts" 2>/dev/null; then
    pass "provider.ts 使用 isLocalBaseUrl fallback";
  else
    fail "provider.ts 未使用 isLocalBaseUrl fallback";
  fi
fi

# Check validateBaseUrl blocks production URLs (guard only checks the function exists)
if [ -f "$FRONTEND_DIR/src/api/config.ts" ]; then
  if grep -qi "validateBaseUrl\|localhost\|127\.0\.0\.1" "$FRONTEND_DIR/src/api/config.ts" 2>/dev/null; then
    pass "config.ts 有 baseUrl 校验逻辑";
  else
    fail "config.ts 缺少 baseUrl 校验逻辑";
  fi
fi
echo ""

# ── 结果汇总 ─────────────────────────────────────────────────
echo "══════════════════════════════════════════════════════"
echo -e "  通过：${GRN}${PASS}${NC}  失败：${RED}${FAIL}${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
  echo "FRONTEND_COMPONENTIZATION_PHASE1_CHECK_PASS"
  echo "══════════════════════════════════════════════════════"
  echo ""
  exit 0
else
  echo -e "  ${RED}发现以下问题：${NC}"
  for err in "${ERRORS[@]}"; do
    echo "  - $err"
  done
  echo ""
  echo "FRONTEND_COMPONENTIZATION_PHASE1_CHECK_FAIL"
  echo "══════════════════════════════════════════════════════"
  echo ""
  exit 1
fi
