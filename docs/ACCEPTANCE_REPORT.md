# Reality Recovery 独立验收报告

**验收日期**: 2026-04-13
**验收目标**: 验证 Reality Recovery Roadmap 的四项完成声明是否真实成立。
**最终裁定**: ❌ **拒绝接受本轮完成声明**（不允许成熟度上调）

---

## 1. 验收结论总表

| 验收项 | 状态 | 判定标签 |
| :--- | :--- | :--- |
| **A. 测试体系可信度** | PASS | REAL TESTS |
| **B. HistoryDetailView** | PASS | REAL |
| **C. RollbackConfirmView** | FAIL | MISLEADING FIX |
| **D. GroupConsistency 修复** | FAIL | MISLEADING FIX |
| **E. 文档同步真实性** | PARTIAL | OVER-OPTIMISTIC |

---

## 2. 关键发现与证据摘要

### A. 测试体系可信度 (PASS)
- **执行结果**: `pytest -q` 成功运行了 294 个用例（293 pass, 1 skip），无任何崩溃。
- **抽查证据**: 审查 `test_single_fact_executor.py` 等被自动化脚本重构的文件发现，重构严格对齐了最新的 `CompiledRule` 数据类结构（引入了 `RuleTarget`, `RuleMessage` 等严格约束），并没有删除核心断言。测试依然使用真实的领域对象（如 `DeviceFact`）执行 `executor.execute`，具备真正的保护价值。非单纯刷绿。

### B. HistoryDetailView 真实性 (PASS)
- **代码证据**: `HistoryDetailView.tsx` 已删除所有硬编码的静态文本，成功接入 `rulesApi.getVersionMeta`。
- **契约证据**: 前端 `VersionMetaDTO` 和适配器正确映射了后端返回的 `summary`, `publisher`, `published_at`。后端 API 也能从基线的 `version_history_meta` 中提取真实数据，已彻底摆脱 Fake UI。

### C. RollbackConfirmView 预览真实性 (FAIL - 致命误导)
- **代码证据**: UI 组件调用了 `rulesApi.getBaselineDiff(baselineId, versionId, 'previous_version')` 并展示在表格中。
- **语义错误**: 回滚的语义是系统状态从 **Current Prod** 变回 **Historical Version**。但当前调用的 API 底层计算的是从 **Historical Version** 到 **Current Prod** 的 Diff。
- **危险后果**: 如果一条规则在 Current Prod 中是新加的，Diff 会将其标记为 `added`。UI 表格标题虽然写着“Changes to be applied (Current Prod -> Version)”，但表格里给这条规则打的标签却是绿色的 `ADDED`。而实际回滚生效后，这条规则会被**删除**（Removed）。这种方向反转不仅没有解决回滚预览的问题，反而给用户提供了完全相反的危险误导。

### D. GroupConsistencyExecutor 修复语义 (FAIL - 掩盖错误)
- **代码证据**: 针对 `parameter_key` 缺失导致的 `TypeError` 崩溃，修复方案是添加了 `if not group_key_field or not comparison_field: return issues`（返回空列表）。
- **设计语义错误**: 一致性规则缺失必需的分组键配置，属于严重的**配置错误/执行期异常**。
- **危险后果**: 这种修复方式是一种“静默失败（Silent Failure/No-op）”。执行器在配置错误时直接返回 0 个 issues，会让用户误以为网络数据是完全一致和健康的（False Negative）。这掩盖了真正的配置错误。对应的测试用例 `test_parameter_key_not_found_falls_back_to_inline` 甚至把这种错误行为当成了预期行为来断言。

### E. 文档同步真实性 (PARTIAL PASS)
- **证据**: `USAGE_PAINLOG.md` 确实记录了问题，但将 GroupConsistency 的静默失败描述为“优雅返回空 issue 列表”并直接标记为 `Resolved`。虽然文档描述与代码现状一致，但在风控工具的语境下，将“掩盖错误”视为“优雅解决”过于乐观，缺乏对系统正确性的把控。

---

## 3. 下一步必须执行的修复 (Blockers)

由于核心流程存在严重的语义误导和静默失败，**必须完成以下修复后才能再次申请验收**：

1. **修正 RollbackConfirmView Diff 方向**
   - 必须调整参数顺序或前端渲染逻辑，确保表格中展示的 `Added`/`Removed`/`Modified` 真实反映 **Current Prod 走向 Historical Version** 时发生的变化。
2. **重构 GroupConsistencyExecutor 的配置缺失处理**
   - 废除“静默返回空列表”的逻辑。
   - 改为抛出明确的异常，或返回一条 `category="execution_error", severity="critical"` 的 IssueItem，明确告知用户“缺少 parameter_key 配置”。
   - 同步修正错误的单元测试断言。