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
| **当前状态** | Closed |

---

### PAIN-003：Rollback 预览 Diff 方向错误导致 Added/Removed/Modified 语义反转

| 字段 | 值 |
|------|-----|
| **Pain ID** | PAIN-003 |
| **日期** | 2026-04-14 |
| **使用场景** | 从历史版本回滚前确认变更影响 |
| **触发路径** | 选择历史版本 → Rollback Confirm → 查看 Added/Removed/Modified 预览 |
| **问题描述** | Rollback Preview 实际请求为 Historical → Current Production 的 diff，但 UI 语义用于表达“回滚后将发生的变化”，导致 Added/Removed/Modified（以及 Modified 的 before/after）整体反转，误导用户判断 |
| **实际影响** | 用户会对回滚影响产生相反认知，属于高信任风险，可能导致错误发布或回滚决策 |
| **临时绕过方式** | 手动反向理解 diff（Added 当 Removed、Modified 前后互换），或改用离线对比 |
| **Frequency** | 2 |
| **Severity** | 4 |
| **Workflow Blocking** | 3 |
| **Trust Risk** | 4 |
| **Pain Score** | 2×2 + 4×3 + 3×2 + 4×4 = **38** (Critical) |
| **建议方案** | 提供专用 rollback effect diff（Current Production → Target Historical），或在适配层严格翻转 diff 语义并同步 summary/counts/labels |
| **当前状态** | Fixed |

---

### PAIN-004：（模板行 — 复制此块新增条目）

| 字段 | 值 |
|------|-----|
| **Pain ID** | PAIN-004 |
| **日期** | _填写日期_ |
| **使用场景** | _描述你在做什么_ |
| **触发路径** | _具体操作步骤_ |
| **问题描述** | _客观描述问题_ |
| **实际影响** | _对你工作的实际影响_ |
| **临时绕过方式** | _你怎么绕过的，或"无"_ |
| **Frequency** | _1-4_ |
| **Severity** | _1-4_ |
| **Workflow Blocking** | _1-4_ |
| **Trust Risk** | _1-4_ |
| **Pain Score** | _Frequency×2 + Severity×3 + Blocking×2 + Trust×4 = N_ |
| **建议方案** | _你认为该怎么解决，或"待评估"_ |
| **当前状态** | Open / Planned / Fixed / Deferred |
