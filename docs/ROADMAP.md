# Roadmap — Usage-Driven

> 项目已进入 L4 稳定期，开发模式从"建设驱动"切换为"真实使用驱动优化"。
> 所有优先级由 `docs/USAGE_PAINLOG.md` 驱动，非预设计划。

---

## 当前状态

- **成熟度**：L4 Alpha（W16 假实现导致成熟度下调）
- **开发模式**：Usage-Driven Optimization
- **迭代机制**：Pain Log → Iteration Review → Roadmap 排期
- **测试基准**：272 passed, 1 skipped, 0 failed

---

## Active（当前高优 — 来自 Pain Log Critical/High）

| Pain ID | 项目 | Pain Score | 目标 | 关联风险 |
|---------|------|-----------|------|---------|
| PAIN-004 | Draft Payload 支持 rule_set | 44 (Critical) | 后端支持多规则 Draft 保存 | W16 假实现 |
| PAIN-005 | 完整工作流语义闭环 | 44 (Critical) | Validate/Publish/Diff 接口支持 rule_set | W16 假实现 |
| PAIN-006 | 彻底清理 Stale UI | 37 (Critical) | UPDATE_DRAFT 清理过期校验状态 | W16 假实现 |
| PAIN-007 | Draft Debounced Persistence | 18 (Moderate) | 实现前端/后端 Save Debounce | W16 假实现 |
| PAIN-002 | 回滚确认展示完整 rule_set | 30 (Critical) | RollbackConfirmView 展示完整规则列表 + 逐条确认 | — |
| PAIN-001 | RuleEditor JSON 编辑体验 | 26 (High) | Monaco Editor + Schema 暴露 + 编译错误精确映射 | — |

---

## Backlog（已确认，未排期）

| ID | 项目 | 来源 | 说明 |
|----|------|------|------|
| BL-001 | tasks.json Schema Migration | RISK-003 | 为 tasks.json 增加 `__schema_version__` + migration registry |
| BL-002 | GroupConsistencyExecutor TypeError 修复 | RISK-008 | `parameter_key` 找不到时 fallback 返回 None 导致 TypeError |
| BL-003 | 前端 bundle 体积优化 | RISK-007 | 当前 >500KB，考虑 code splitting |
| BL-004 | 修复 Pre-existing CLI Test | test_run_core.py | task lifecycle 状态机与 test fixture 不匹配 |
| BL-005 | 编译错误 field_path 精确映射 | PAIN-001 子项 | RuleCompileError 的 field_path 粒度不够，返回 `params` 而非 `params.operator` |
| BL-006 | 回滚版本链追踪 | P2-4 | rollback 记录中保留 `rollback_target_version` + `reason` 到 `version_history_meta` |

---

## Parking Lot（低优 / 暂缓）

| ID | 项目 | 暂缓原因 |
|----|------|---------|
| PL-001 | 根目录脚本归档 | 不影响使用，自维护维度 P2 |
| PL-002 | 文档去重合并 | 已由本次重构部分完成，剩余低优 |
| PL-003 | `user_input.json` 清理 | 不影响使用 |
| PL-004 | 结构化 JSON 日志 | 当前文本日志可满足排查需求 |
| PL-005 | `/health` 健康检查端点 | 单用户场景非刚需 |
| PL-006 | 每基线独立文件存储 | 当前单文件 JSON 可支撑 |
| PL-007 | 批量规则发布 | Pain Log 无相关痛点 |
| PL-008 | 发布前变更摘要预览 | 当前 Diff 页面已可满足 |
| PL-009 | 规则模板 Schema 暴露给前端 | PAIN-001 子项，随 Monaco Editor 一起排期更合理 |

---

## Future Triggers（条件触发的大能力）

以下项目在出现真实需求前不做。触发条件明确写入。

| ID | 能力 | 触发条件 | 预估规模 |
|----|------|---------|---------|
| FT-001 | PostgreSQL 替换 JSON 持久化 | 数据量 >10k 规则 / 并发写入 / 多进程部署 | 大 |
| FT-002 | RBAC 权限控制 | 从单用户扩展到多人协作 | 大 |
| FT-003 | 审批流（Publish Approval） | 团队规则变更需审核 | 大 |
| FT-004 | 多语言规则模板 / i18n | 非中文用户需求出现 | 中 |
| FT-005 | 规则版本 diff 三方合并 | 两人同时编辑同一规则 | 大 |

---

## 已完成归档

以下阶段已完成，详细记录见 `docs/PROJECT_STATE_SNAPSHOT.yaml` 的 `remediation_history`。

| 阶段 | 完成日期 | 关键成果 |
|------|---------|---------|
| P0 | 2026-04-11 | Executor 修复 + 数据安全 + 可观测性（7 项） |
| P1.0 | 2026-04-11 | 主链路真实性闭环（3 项） |
| P1.1 | 2026-04-11 | 构建链 + Diff 语义 + Schema Migration（3 项） |
| Phase A | 2026-04-11 | Save Draft 真实落地 + Executor 测试补齐（2 项） |
| Phase B | 2026-04-12 | Deep Diff 递归比较 + 完整 Rule Set Rollback（2 项） |

---

## 里程碑

```
[M1] Phase B 完成 ✅ → L4.0（0伪实现 + 272测试通过）
[Now] Usage-Driven Mode 启动 → Pain Log 驱动迭代
[Next] PAIN-002 修复 → 回滚体验闭环
[Future] PAIN-001 修复 → 编辑体验质变
[FT] 触发条件满足时 → FT-001~FT-005 评估启动
```
