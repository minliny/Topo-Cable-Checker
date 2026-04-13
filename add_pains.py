import sys

pain_content = """
---

### PAIN-004：W16 Recovery Validation - Draft Model Fake Implementation

| 字段 | 值 |
|------|-----|
| **Pain ID** | PAIN-004 |
| **日期** | 2026-04-13 |
| **使用场景** | 尝试保存包含多条规则的 Draft（W16 验证） |
| **触发路径** | 修改基线中多条规则并点击保存草稿 |
| **问题描述** | `SaveDraftRequestDTO` 和 `save_draft` 接口仅支持单条 `rule_id` / `rule_type` / `params`，完全不支持保存 `rule_set`。 |
| **实际影响** | 无法保存多规则草稿，多规则编辑完全丢失。 |
| **临时绕过方式** | 每次只修改并保存一条规则 |
| **Frequency** | 4 |
| **Severity** | 4 |
| **Workflow Blocking** | 4 |
| **Trust Risk** | 4 |
| **Pain Score** | 4×2 + 4×3 + 4×2 + 4×4 = **44** (Critical) |
| **建议方案** | 必须在后端 API 层面重构 `SaveDraftRequestDTO` 以支持完整 `rule_set`，并在 `rule_draft_save_service.py` 中正确序列化。 |
| **当前状态** | Open |

---

### PAIN-005：W16 Recovery Validation - Full Workflow Semantic Missing

| 字段 | 值 |
|------|-----|
| **Pain ID** | PAIN-005 |
| **日期** | 2026-04-13 |
| **使用场景** | 尝试对多规则 Draft 进行 Validate 和 Publish（W16 验证） |
| **触发路径** | 修改多条规则后，执行校验和发布 |
| **问题描述** | Validate, Publish, Diff 接口均只接收/处理单条规则的 DTO，不支持完整 rule_set 的全链路闭环。 |
| **实际影响** | 多规则修改无法一起发布和校验，只能逐条进行，完全破坏了 rule_set-level draft 的设计语义。 |
| **临时绕过方式** | 逐条规则校验发布 |
| **Frequency** | 4 |
| **Severity** | 4 |
| **Workflow Blocking** | 4 |
| **Trust Risk** | 4 |
| **Pain Score** | 4×2 + 4×3 + 4×2 + 4×4 = **44** (Critical) |
| **建议方案** | 重构所有相关 DTO 和 Service，将 `rule_id`/`params` 升级为接受整个 `rule_set`。 |
| **当前状态** | Open |

---

### PAIN-006：W16 Recovery Validation - Validation Stale UI

| 字段 | 值 |
|------|-----|
| **Pain ID** | PAIN-006 |
| **日期** | 2026-04-13 |
| **使用场景** | 修改规则参数后，验证状态区是否清理（W16 验证） |
| **触发路径** | 校验成功 -> 修改参数 -> 观察 UI |
| **问题描述** | 前端 `pageReducer.ts` 的 `UPDATE_DRAFT` action 未清理 `validationResult` 和 `publishBlockedIssues`。 |
| **实际影响** | 严重误导用户，认为修改后的错误配置仍然是“校验通过”的。 |
| **临时绕过方式** | 无 |
| **Frequency** | 4 |
| **Severity** | 3 |
| **Workflow Blocking** | 2 |
| **Trust Risk** | 4 |
| **Pain Score** | 4×2 + 3×3 + 2×2 + 4×4 = **37** (Critical) |
| **建议方案** | 在 `UPDATE_DRAFT` 触发时，重置 `validationResult` 和 `publishBlockedIssues` 为 `null`。 |
| **当前状态** | Open |

---

### PAIN-007：W16 Recovery Validation - Debounced Persistence Missing

| 字段 | 值 |
|------|-----|
| **Pain ID** | PAIN-007 |
| **日期** | 2026-04-13 |
| **使用场景** | 连续快速编辑并保存草稿（W16 验证） |
| **触发路径** | 快速触发多次 Save Draft |
| **问题描述** | 前后端均未发现 debounce 或 pending write cache 的实现。Burst Save benchmark 证明依然是同步落盘。 |
| **实际影响** | 导致 IO 性能问题和 UI 卡顿。 |
| **临时绕过方式** | 无 |
| **Frequency** | 3 |
| **Severity** | 2 |
| **Workflow Blocking** | 1 |
| **Trust Risk** | 1 |
| **Pain Score** | 3×2 + 2×3 + 1×2 + 1×4 = **18** (Moderate) |
| **建议方案** | 在前端 API 层引入 debounce 队列，或在后端引入基于内存的 Write Buffer 和定时 Flush 机制。 |
| **当前状态** | Open |

"""

with open("docs/USAGE_PAINLOG.md", "a") as f:
    f.write(pain_content)
