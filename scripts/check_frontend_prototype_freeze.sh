#!/usr/bin/env bash
# ============================================================
# check_frontend_prototype_freeze.sh
# TopoChecker — 前台原型冻结静态回归护栏
# 目标：阻断 READY_CANDIDATE 状态的 P0/P1/P2 架构回退
# 用法：bash scripts/check_frontend_prototype_freeze.sh
# ============================================================
set -euo pipefail

TARGET="TopoChecker 完整前台.html"
PASS=0
FAIL=0
ERRORS=()

# ── 颜色 ──────────────────────────────────────────────────────
RED='\033[0;31m'
GRN='\033[0;32m'
YLW='\033[1;33m'
NC='\033[0m'

pass() { echo -e "  ${GRN}✓${NC} $1"; PASS=$((PASS+1)); }
fail() { echo -e "  ${RED}✗${NC} $1"; FAIL=$((FAIL+1)); ERRORS+=("$1"); }

check_present() {
  local label="$1" pattern="$2"
  if grep -qF "$pattern" "$TARGET" 2>/dev/null; then
    pass "$label"
  else
    fail "缺失：$label ($pattern)"
  fi
}

check_absent() {
  local label="$1" pattern="$2"
  if grep -qF "$pattern" "$TARGET" 2>/dev/null; then
    fail "禁止词出现：$label ($pattern)"
  else
    pass "无禁止词：$label"
  fi
}

check_single_def() {
  local label="$1" pattern="$2"
  local count
  count=$(grep -cF "$pattern" "$TARGET" 2>/dev/null || true)
  if [ "$count" -eq 1 ]; then
    pass "$label 仅定义一次"
  elif [ "$count" -eq 0 ]; then
    fail "$label 未找到定义 ($pattern)"
  else
    fail "$label 存在重复定义，共 $count 次 ($pattern)"
  fi
}

# ── 文件存在检查 ───────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════════════"
echo "  TopoChecker 前台原型冻结静态护栏"
echo "  目标文件：$TARGET"
echo "══════════════════════════════════════════════════════"
echo ""

if [ ! -f "$TARGET" ]; then
  echo -e "${RED}[FATAL] 目标文件不存在：$TARGET${NC}"
  exit 1
fi

# ── Section 1：必须存在的关键模型/标识 ───────────────────────
echo "── Section 1：关键模型标识 ──"
check_present "PARAMETER_PROFILES"         "PARAMETER_PROFILES"
check_present "THRESHOLD_PROFILES"         "THRESHOLD_PROFILES"
check_present "SCOPE_SELECTORS"            "SCOPE_SELECTORS"
check_present "RULE_SETS"                  "RULE_SETS"
check_present "BASELINE_PROFILE_MAP"       "BASELINE_PROFILE_MAP"
check_present "RULE_PROFILE_MAP"           "RULE_PROFILE_MAP"
check_present "VERSION_CHANGE_SUMMARIES"   "VERSION_CHANGE_SUMMARIES"
check_present "VERSION_SNAPSHOTS"          "VERSION_SNAPSHOTS"
check_present "VERSION_DIFF_SNAPSHOTS"     "VERSION_DIFF_SNAPSHOTS"
check_present "RECHECK_DIFF_SNAPSHOTS"     "RECHECK_DIFF_SNAPSHOTS"
check_present "recognition_status"         "recognition_status"
check_present "canCheck"                   "canCheck"
check_present "drilldown"                  "drilldown"
check_present "rule_overrides"             "rule_overrides"
check_present "DATA_SOURCES"               "DATA_SOURCES"
check_present "EXECUTION_SCOPES"           "EXECUTION_SCOPES"
check_present "RECOGNITION_RESULTS"        "RECOGNITION_RESULTS"
echo ""

# ── Section 2：禁止出现的回退关键词 ──────────────────────────
echo "── Section 2：禁止回退关键词 ──"
check_absent "idsA"                        "idsA"
check_absent "idsB"                        "idsB"
check_absent "newIssues"                   "newIssues"
check_absent "removedIssues"               "removedIssues"
check_absent "ra.diff_summary"             "ra.diff_summary"
check_absent "硬编码-本地快照"             "本地快照（离线）"
check_absent "硬编码-全量DC"               "全量（DC-A / DC-B）"
check_absent "硬编码-预估耗时"             "~30s"
echo ""

# ── Section 3：Workbench 越界检查 ─────────────────────────────
# 检查 Workbench 内是否出现基线/规则/版本/执行的管理入口文案
# （保守全文检查，避免误报误用）
echo "── Section 3：Workbench 边界 ──"
# 这些文案若出现在 Workbench 组件上下文中则为越界；
# 全文检查作为保守护栏（导航定义区例外）
check_absent "Workbench-编辑基线"           "编辑基线"
# 规则编辑、版本管理、执行配置可能出现在导航常量 NAV 中是合法的；
# 只检查不合法的跳转文案（带操作语义的按钮文本）
if grep -qF "setNav.*rules" "$TARGET" 2>/dev/null; then
  # 确保跳转到 rules 的只在 BaselineDetail/A页，不在 AnalysisWorkbench 内
  # 保守策略：只要 AnalysisWorkbench 函数体内不出现 sub:'rules' 跳转即可
  wb_block=$(awk '/function AnalysisWorkbench/,/^function [A-Z]/' "$TARGET" 2>/dev/null || true)
  if echo "$wb_block" | grep -qF "sub:'rules'"; then
    fail "Workbench 内出现规则编辑跳转 (sub:'rules')"
  else
    pass "Workbench 内无规则编辑越界跳转"
  fi
else
  pass "Workbench 内无规则编辑越界跳转"
fi
if awk '/function AnalysisWorkbench/,/^function [A-Z]/' "$TARGET" 2>/dev/null | grep -qF "sub:'versions'"; then
  fail "Workbench 内出现版本管理跳转 (sub:'versions')"
else
  pass "Workbench 内无版本管理越界跳转"
fi
if awk '/function AnalysisWorkbench/,/^function [A-Z]/' "$TARGET" 2>/dev/null | grep -qF "sub:'config'"; then
  fail "Workbench 内出现执行配置跳转 (sub:'config')"
else
  pass "Workbench 内无执行配置越界跳转"
fi
echo ""

# ── Section 4：组件重复定义检查 ───────────────────────────────
echo "── Section 4：组件重复定义 ──"
check_single_def "DiffCompare"        "function DiffCompare("
check_single_def "AnalysisWorkbench"  "function AnalysisWorkbench("
check_single_def "VersionMgmt"        "function VersionMgmt("
check_single_def "ExecutionConfig"    "function ExecutionConfig("
check_single_def "BaselineDetail"     "function BaselineDetail("
check_single_def "RuleEditor"         "function RuleEditor("
echo ""

# ── Section 5：P0 关键守卫存在性 ─────────────────────────────
echo "── Section 5：P0 关键守卫 ──"
check_present "recognitionStatus 状态机"    "recognitionStatus==='confirmed'"
check_present "canCheck disabled 守卫"       "disabled={!canCheck}"
check_present "snapshotKey A→B 配对"         "snapshotKey"
check_present "RECHECK_DIFF_SNAPSHOTS 消费"  "RECHECK_DIFF_SNAPSHOTS[snapshotKey]"
echo ""

# ── 结果汇总 ─────────────────────────────────────────────────
echo "══════════════════════════════════════════════════════"
echo -e "  通过：${GRN}${PASS}${NC}  失败：${RED}${FAIL}${NC}"
echo ""

if [ ${#ERRORS[@]} -gt 0 ]; then
  echo -e "${YLW}失败项：${NC}"
  for e in "${ERRORS[@]}"; do
    echo -e "  ${RED}→ $e${NC}"
  done
  echo ""
fi

if [ "$FAIL" -eq 0 ]; then
  echo -e "${GRN}FRONTEND_PROTOTYPE_FREEZE_CHECK_PASS${NC}"
  echo "══════════════════════════════════════════════════════"
  exit 0
else
  echo -e "${RED}FRONTEND_PROTOTYPE_FREEZE_CHECK_FAIL — $FAIL 项检查未通过${NC}"
  echo "══════════════════════════════════════════════════════"
  exit 1
fi
