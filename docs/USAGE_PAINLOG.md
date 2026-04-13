# Usage Pain Log

> 真实使用痛点记录。所有后续迭代优先级由本日志驱动，非拍脑袋。
> 项目阶段：L4 稳定期 — Usage-Driven Optimization Mode

---

## 评分规则

### Frequency（频率）

| 值 | 含义 |
|----|------|
| 1 | 首次遇到 / 极罕见 |
| 2 | 偶尔（月度） |
| 3 | 经常（每周） |
| 4 | 频繁（每次使用） |

### Severity（严重度）

| 值 | 含义 |
|----|------|
| 1 | 轻微不便，不影响结果 |
| 2 | 需要额外操作绕过，但不丢数据 |
| 3 | 阻断部分工作流，需要手动修复 |
| 4 | 数据丢失 / 结果不可信 / 核心流程不可用 |

### Workflow Blocking（工作流阻断）

| 值 | 含义 |
|----|------|
| 1 | 不阻断，仅体验不佳 |
| 2 | 绕过后可继续 |
| 3 | 需要切换工具/手动干预 |
| 4 | 完全阻断，无法继续 |

### Trust Risk（信任风险）

| 值 | 含义 |
|----|------|
| 1 | 无信任影响 |
| 2 | 轻微疑虑，可自行验证 |
| 3 | 需要额外确认才敢信任结果 |
| 4 | 信任受损，不再依赖该功能 |

### Pain Score 计算公式

```
Pain Score = Frequency × 2 + Severity × 3 + Workflow Blocking × 2 + Trust Risk × 4
```

| 范围 | 优先级 |
|------|--------|
| 30–40 | **Critical** — 本轮必须修复 |
| 20–29 | **High** — 近期排期 |
| 10–19 | **Medium** — 排入 Backlog |
| 1–9 | **Low** — Parking Lot |

---

## Pain Log

### PAIN-001：RuleEditor JSON 手工编辑易出错

| 字段 | 值 |
|------|-----|
| **Pain ID** | PAIN-001 |
| **日期** | 2026-04-12 |
| **使用场景** | 编辑 threshold 规则参数 |
| **触发路径** | 选择 rule_type → JSON TextArea 手动输入 params |
| **问题描述** | JSON TextArea 无语法校验、无字段提示、无自动补全。输入 `operator: "great_than"` 拼写错误时，校验端点返回的错误信息仅显示 `metric_type not found`，field_path 不够精确 |
| **实际影响** | 平均每次编辑需要 2-3 次试错才能通过校验 |
| **临时绕过方式** | 复制已有规则 JSON 改参数 |
| **Frequency** | 4 |
| **Severity** | 2 |
| **Workflow Blocking** | 2 |
| **Trust Risk** | 2 |
| **Pain Score** | 4×2 + 2×3 + 2×2 + 2×4 = **26** (High) |
| **建议方案** | Monaco Editor 替换 TextArea + 规则 Schema 暴露给前端 + 编译错误 field_path 精确映射 |
| **当前状态** | Open |

---

### PAIN-002：回滚候选只展示第一条规则，无法确认完整规则集

| 字段 | 值 |
|------|-----|
| **Pain ID** | PAIN-002 |
| **日期** | 2026-04-12 |
| **使用场景** | 从历史版本回滚 |
| **触发路径** | 选择历史版本 → 创建回滚候选 → 编辑器仅显示第一条规则 |
| **问题描述** | 虽然 B2 已返回完整 `rule_set`，但前端编辑器仍只渲染 `draft_data`（第一条规则）。用户无法在确认前看到回滚将恢复的全部规则列表，不确定回滚是否正确 |
| **实际影响** | 不敢直接发布回滚候选，需要手动对照 diff 确认 |
| **临时绕过方式** | 先查看 Diff 页面确认规则列表，再执行回滚 |
| **Frequency** | 3 |
| **Severity** | 2 |
| **Workflow Blocking** | 3 |
| **Trust Risk** | 3 |
| **Pain Score** | 3×2 + 2×3 + 3×2 + 3×4 = **30** (Critical) |
| **建议方案** | 前端 RollbackConfirmView 展示完整 rule_set 规则列表，支持逐条确认 |
| **当前状态** | Open |

---

### PAIN-003：Publish 阶段触发后端代码错误阻断发布

| 字段 | 值 |
|------|-----|
| **Pain ID** | PAIN-003 |
| **日期** | 2026-04-13 |
| **使用场景** | 提交草稿进行发布 (Prepare Publish -> Confirm Publish) |
| **触发路径** | 点击 Validate 成功后，点击 Prepare Publish，然后点击 Confirm Publish |
| **问题描述** | Validate 阶段显示校验通过，但在最终发布校验时后端抛出 `An unexpected error occurred during compilation: 'CompiledRule' object has no attribute 'validate'`。这是由于代码中调用了不存在的方法导致的，彻底阻断了发布流程。 |
| **实际影响** | 无法完成任何新规则或草稿的发布，核心闭环断裂 |
| **临时绕过方式** | 无 |
| **Frequency** | 4 |
| **Severity** | 4 |
| **Workflow Blocking** | 4 |
| **Trust Risk** | 4 |
| **Pain Score** | 4×2 + 4×3 + 4×2 + 4×4 = **44** (Critical) |
| **建议方案** | 修复 `RuleEditorGovernanceBridgeService` 中的代码逻辑，移除 `compiled_rule.validate()` 调用或实现该方法 |
| **当前状态** | Open |

### PAIN-004：草稿与编辑器架构仅支持单条规则编辑

| 字段 | 值 |
|------|-----|
| **Pain ID** | PAIN-004 |
| **日期** | 2026-04-13 |
| **使用场景** | 尝试连续修改多条规则或执行多规则场景 (Day 2 / 批量编辑) |
| **触发路径** | 选中 Baseline -> 点击 Draft -> 编辑器中仅能输入单一 Rule ID 和 Params |
| **问题描述** | MVP 版本的 `RuleDraftSaveService` 和前端 `EditorView` 强制将 Draft 建模为单一规则（`rule_id`, `rule_type`, `params`）。不支持在一次 Draft 中添加、删除或修改多条规则。这导致多规则并发编辑、批量重构等高频场景无法完成。 |
| **实际影响** | 无法支持真实业务中复杂的规则集重构，每个规则变更都必须走一次完整的 Publish 流程，效率极低。 |
| **临时绕过方式** | 只能逐个规则单独建立草稿、单独发布 |
| **Frequency** | 4 |
| **Severity** | 3 |
| **Workflow Blocking** | 3 |
| **Trust Risk** | 1 |
| **Pain Score** | 4×2 + 3×3 + 3×2 + 1×4 = **27** (High) |
| **建议方案** | 升级 Draft 数据模型，支持 `rule_set` 级别的全量草稿或多条增量变更；前端增加规则列表导航以支持多规则切换编辑。 |
| **当前状态** | Open |

### PAIN-005：修改草稿参数后未清理历史校验结果

| 字段 | 值 |
|------|-----|
| **Pain ID** | PAIN-005 |
| **日期** | 2026-04-13 |
| **使用场景** | 在通过 Validate 后继续编辑草稿 |
| **触发路径** | 填写合法 JSON -> 点击 Validate (通过) -> 再次修改 JSON 为非法格式 -> 页面依然显示绿色的 "Validation Results" 通过状态 |
| **问题描述** | 只要不再次点击 Validate 并成功触发 API（或如果被前端 try-catch 拦截而未更新页面状态），右侧面板的 Validation Results 状态不会自动重置为未校验或隐藏。如果 JSON.parse 抛出异常被前端捕获并 toast 报错，由于 `dispatch({ type: 'VALIDATION_FAILED' })` 没能正确清空历史成功的 payload，旧的绿色 check-circle 会一直保留，极大误导用户。 |
| **实际影响** | 用户看到明显的语法错误，但右侧却显示“校验通过”，引发严重信任危机 |
| **临时绕过方式** | 忽略右侧状态，只看 toast 提示 |
| **Frequency** | 4 |
| **Severity** | 2 |
| **Workflow Blocking** | 1 |
| **Trust Risk** | 4 |
| **Pain Score** | 4×2 + 2×3 + 1×2 + 4×4 = **32** (Critical) |
| **建议方案** | `pageReducer.ts` 在 `UPDATE_DRAFT` (dirty 状态变为 true) 时，应自动清除 `validationResult` 和 `publishBlockedIssues`。 |
| **当前状态** | Open |

### PAIN-006：Save Draft 触发全量同步写盘，导致大规模数据下性能雪崩

| 字段 | 值 |
|------|-----|
| **Pain ID** | PAIN-006 |
| **日期** | 2026-04-13 |
| **使用场景** | Day 4: 大规模数据下的压力测试 (Save Draft) |
| **触发路径** | 规则数达到 10000+ 时，连续点击 Save Draft |
| **问题描述** | `BaselineRepository` 当前使用同步阻塞式 I/O (`_write_json`) 全量覆盖 `baselines.json` 文件。在测试 10,000 条规则时，每次 Save Draft 都需序列化并重写整个 JSON 文件，导致请求耗时激增（单次 >180ms），不仅前端卡顿，且由于是同步操作，会阻塞 FastAPI 事件循环，导致其他用户的并发请求超时。 |
| **实际影响** | 无法支撑生产环境中的大规模基线存储和并发编辑场景 |
| **临时绕过方式** | 无 |
| **Frequency** | 4 |
| **Severity** | 4 |
| **Workflow Blocking** | 2 |
| **Trust Risk** | 2 |
| **Pain Score** | 4×2 + 4×3 + 2×2 + 2×4 = **32** (Critical) |
| **建议方案** | 引入真正的数据库（如 PostgreSQL/SQLite），按 Rule 或 Draft 进行增量记录；或至少改用异步 I/O 及读写锁机制，避免阻塞主线程。 |
| **当前状态** | Open |
