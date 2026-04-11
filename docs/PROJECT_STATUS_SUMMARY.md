# 项目状态汇总 (Project Status Summary)

本文档旨在为接手本仓库的研发、产品或测试人员提供当前项目的“一句话定位”与整体健康度概览。

## 一、当前版本一句话定位

> **“基于严格状态机与真实 FastAPI 后端双向绑定的三栏规则工作台 MVP (v1.0)，已具备端到端发布、防错校验与历史回滚闭环。”**

## 二、架构健康度与交付物状态

| 模块/能力 | 状态 | 简述 |
| --- | --- | --- |
| **前端状态机 (Reducer)** | 🟢 稳态收口 | 废弃了散落的 `useState`/`useEffect`，统一由 `pageReducer.ts` 接管。`publish_checking`、`publish_blocked`、`published`、`rollback_ready_edit` 等复杂语义已全部实现显式跳转，具备完全的工程可推导性。 |
| **数据契约对齐 (DTOs)** | 🟢 严格一致 | 前端 `types/dto.ts` 与后端 `presentation/api/dto_models.py` 字段已严格对齐，消除了因字段缺失或类型错误导致的 UI 崩溃风险。 |
| **前后端 API 适配层** | 🟢 已生效 | 前端 `api/adapters.ts` 已实现 Raw Response 向 DTO 的安全归一化转换，即使后端部分字段为空也能平稳降级渲染。双通道切换（Mock vs Real）可用。 |
| **FastAPI 后端壳层** | 🟢 已接通 | 建立在原有领域模型之上，对外提供 6 个标准的 RESTful 接口（包括只读与写入），成功实现了前端的联调落地，打通了网络层。 |
| **JSON 文件持久化** | 🟢 原子写入 | `baselines.json` 采用 `tempfile.mkstemp` + `os.replace` 的原子级文件操作方案，解决了并发或进程崩溃导致的数据损坏痛点。 |
| **领域校验映射** | 🟢 已打通 | 领域层 `RuleCompiler` 抛出的 `RuleCompileError` 已被成功捕获并映射为前端理解的 `ValidationIssueDTO`，且前端已实现基于 DOM 的错误字段物理定位回显（CSS Ring）。 |
| **回归测试防线** | 🟢 最小可用 | 后端已补齐 8 个 `pytest` 集成用例，覆盖了读取树、验证草稿、阻断发布、成功发布与回滚候选生成的全生命周期。 |

## 三、下一步推荐动作 (Next Actions)

如果您是新加入的开发者或验收人员，建议按以下顺序阅读与操作：

1. **执行验收演示**：参阅 [DEMO_SCRIPT.md](./DEMO_SCRIPT.md)，启动前后端服务并跑通一遍发布与回滚流程。
2. **了解系统限制**：参阅 [KNOWN_GAPS.md](./KNOWN_GAPS.md)，区分哪些是当前架构的取舍，哪些是未来需要增强的功能。
3. **规划下一迭代**：参阅 [NEXT_PHASE_ROADMAP.md](./NEXT_PHASE_ROADMAP.md)，着手评估将 Monaco Editor 与 PostgreSQL 纳入下一个 Sprint 的工作量。
4. **查阅 UI 状态表**：若需改动前端交互，务必先参阅 [UI_ARCHITECTURE.md](./UI_ARCHITECTURE.md) 中的状态迁移矩阵。

---
*生成日期：2026-04-11*
