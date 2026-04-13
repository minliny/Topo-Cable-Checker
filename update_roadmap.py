with open("docs/ROADMAP.md", "r") as f:
    orig = f.read()

active_lines = """
| PAIN-004 | Draft Payload 支持 rule_set | 44 (Critical) | 后端支持多规则 Draft 保存 | W16 假实现 |
| PAIN-005 | 完整工作流语义闭环 | 44 (Critical) | Validate/Publish/Diff 接口支持 rule_set | W16 假实现 |
| PAIN-006 | 彻底清理 Stale UI | 37 (Critical) | UPDATE_DRAFT 清理过期校验状态 | W16 假实现 |
| PAIN-007 | Draft Debounced Persistence | 18 (Moderate) | 实现前端/后端 Save Debounce | W16 假实现 |
"""

new_content = orig.replace(
    "| PAIN-002 | 回滚确认展示完整 rule_set | 30 (Critical) | RollbackConfirmView 展示完整规则列表 + 逐条确认 | — |",
    active_lines.strip() + "\n| PAIN-002 | 回滚确认展示完整 rule_set | 30 (Critical) | RollbackConfirmView 展示完整规则列表 + 逐条确认 | — |"
)

new_content = new_content.replace(
    "- **成熟度**：L4.0（0 伪实现，272+ 测试全通过）",
    "- **成熟度**：L4 Alpha（W16 假实现导致成熟度下调）"
)

with open("docs/ROADMAP.md", "w") as f:
    f.write(new_content)

