import sys

content = """
## Iteration 2026-W16 / 2026-04-13 (W16 Recovery Validation)

### 本周期使用概况
- 核心操作路径：尝试验证 W16 后半段修复声明（Draft Model 升级为 rule_set-level draft, Validation stale UI 修复, Save Draft 性能 debounce 优化）。
- 执行了 4 大核心专项验证：A. Multi-rule Draft Recovery Validation, B. Full Workflow Recovery Validation, C. Validation Stale UI Recovery Validation, D. Debounced Persistence Reliability Validation。

### 新发现 Pain
| Pain ID | 一句话描述 | Pain Score | 优先级 |
|---------|-----------|------------|--------|
| PAIN-004 | Draft payload 不支持 rule_set 导致多规则草稿丢失 | 44 | Critical |
| PAIN-005 | Validate/Publish/Diff 不支持 rule_set 导致全链路语义缺失 | 44 | Critical |
| PAIN-006 | UPDATE_DRAFT 未清理 validationResult 导致严重 stale UI | 37 | Critical |
| PAIN-007 | Save Draft 同步落盘，未实现任何 debounce/pending cache | 18 | Moderate |

### 关键结论
1. **Draft Model 是否稳定**：**FAIL**。API 接口和 DTO 完全不支持多规则 `rule_set` 的保存。
2. **Validation UI 是否可信**：**FAIL**。修改 draft 后旧的校验成功状态仍然残留，造成严重误导。
3. **Debounce Persistence 是否可接受**：**FAIL**。未实现任何 debounce 逻辑，依然是同步阻塞写入。
4. **是否允许项目从 L4 Alpha 回升到 L4 Stable Candidate**：**不允许**。由于 W16 声明的特性完全不存在或严重缺失，成熟度被强制下调为 **L4 Alpha (Failed Implementation)**。必须优先重新开发并修复 W16 的假实现。

### Top Priority Next Cycle
1. **PAIN-004, PAIN-005**：真实落地 Rule Set Level Draft 模型并贯穿全链路。
2. **PAIN-006**：在前端 State Reducer 彻底清理过期状态。

"""

with open("docs/ITERATION_REVIEW.md", "r") as f:
    orig = f.read()

parts = orig.split("## Iteration YYYY-WXX / YYYY-MM-DD", 1)
if len(parts) == 2:
    new_content = parts[0] + "## Iteration YYYY-WXX / YYYY-MM-DD" + parts[1].split("```\n")[0] + "```\n\n" + content + parts[1].split("```\n")[1]
    with open("docs/ITERATION_REVIEW.md", "w") as f:
        f.write(new_content)

