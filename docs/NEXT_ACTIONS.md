# 下一阶段执行清单 (Next Actions)

本文档基于《项目定位决策 (Project Positioning)》中选定的**产品化路径 (Rule Governance Tool)** 目标，并结合了从真实用户视角进行首次全流程演示后暴露出的轻量级体验痛点，输出了后续（不超过 10 项）的具体任务清单。

## 一、轻量级体验优化（演示遗留痛点修复）

在首次零认知用户视角的模拟演示中，暴露了以下问题：
1. **历史元数据缺失**：历史版本右侧栏（VersionMeta）未渲染真实的 `publisher`、`published_at`，这使得版本追溯这一核心业务价值感知变弱。
2. **操作按钮错位**：用户的视线在 Validate 后会自然停留在右侧栏，但“Prepare Publish”按钮却在中栏顶部，这打破了典型三栏工具“右栏负责操作与摘要”的惯性思维。
3. **JSON 输入门槛**：`params` 的纯文本框输入非常容易导致格式错误，出错时只有 Toast 提示而没有具体定位。
4. **Diff 技术感过重**：Diff 视图的中栏明细直接抛出了深层 JSON 的对比，非研发用户难以理解。

### 优化任务列表

*此部分任务目标是“低成本、高收益”，在不大改架构的前提下快速提升可用性。*

| 序号 | 优先级 | 任务名 | 价值与描述 | 状态 |
| :--- | :--- | :--- | :--- | :--- |
| **1** | P0 | **补齐 Version Meta 渲染** | 修改 `RightPanel.tsx` 和 `App.tsx`，将真实下发的 `version_history_meta` 信息渲染到右侧栏的 Alert 下方，直观展示“发布人、时间、摘要”。 | Todo |
| **2** | P1 | **重组核心行动按钮区** | 在不改动组件嵌套的前提下，考虑在右栏（Validation Results 等面板下方）增加 Publish 按钮的镜像或快捷入口，或在中栏用更醒目的颜色与分组框区分“Validate”和“Publish”。 | Todo |
| **3** | P1 | **增加 JSON 输入防呆提示** | 在 EditorView 的 `params` 输入框上方添加 `<Text type="secondary">Ensure valid JSON format.</Text>`，并增加一个简单的格式化按钮（JSON.stringify），降低语法出错率。 | Todo |
| **4** | P1 | **统一 Publish Blocked 展示** | 当前拦截错误在 Center Panel 展示，而校验错误在 Right Panel 展示。需统一到右栏，保持用户视线聚焦。 | Todo |

---

## 二、产品化能力增强（系统级演进）

*此部分任务目标是支撑系统向企业级工具迈进。*

| 序号 | 优先级 | 任务名 | 价值与描述 | 状态 |
| :--- | :--- | :--- | :--- | :--- |
| **5** | P0 | **集成 Monaco Editor** | 替换当前的 `<TextArea>` 为 `@monaco-editor/react`。这是风控治理平台的标配，能通过语法高亮和折叠极大降低配置难度，并支持将 API 返回的 `field_path` 映射为红波浪线（Markers）。 | Todo |
| **6** | P1 | **关系型数据库迁移 (PostgreSQL)** | 废弃当前的 `baselines.json` 临时文件原子写入方案。将持久化层迁移至 SQLAlchemy ORM，支撑复杂树状查询和高并发读写。 | Todo |
| **7** | P1 | **乐观锁并发防覆盖** | 在 Publish API 中增加 `parent_version` 参数校验。若用户提交的版本落后于 DB 最新版本，则阻断并提示。防止多人编辑时的脏写（Dirty Write）。 | Todo |
| **8** | P2 | **集成深度 JSON Diff 算法** | 后端引入 `deepdiff`，前端引入专用 diff 组件（如 `react-diff-viewer`）。在 Compare 视图中精准高亮到具体的 Key-Value 变化，而非抛出整段 JSON。 | Todo |
| **9** | P2 | **接入真实用户身份 (RBAC)** | 在 FastAPI 接入 `Depends(get_current_user)`，提取 JWT。将 `version_history_meta` 中的 `admin` 替换为真实员工域账号，并控制前端按钮的展示权限。 | Todo |
| **10** | P3 | **引入发布审批流** | 在状态机中新增 `pending_approval` 状态。发布后需经过主管审批才能成为活跃版本，满足政企金融客户对规则变动的合规审计要求。 | Todo |

> *注：上述任务的执行必须严格遵循《项目定位决策》中定下的原则——不脱离业务痛点、不破坏现有状态机闭环稳态。*
