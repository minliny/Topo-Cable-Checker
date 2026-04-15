# Known Gaps & Future Enhancements

本文档明确区分当前系统中的“已知问题（Known Issues）”与“未来增强（Future Enhancements）”，以确保验收过程和下一阶段规划的清晰性。

## 一、已知问题 (Known Issues)
这些问题存在于当前版本中，但已确认**不阻断**本次三栏工作台的 MVP 核心主流程验收。

### 1. 物理定位与复杂嵌套表单滚动 (Frontend)
- **现象**：当后端返回 `validate` 错误包含深层 `field_path` 时，右栏点击错误能够正确触发 `JUMP_TO_FIELD` 动作，中栏状态机也能正确接收。但由于目前使用简化的 Ant Design 表单或原生 JSON 渲染，物理的 `scrollToField` 在嵌套极深或不可见字段上可能会失效或定位不精准。
- **影响**：用户体验降级，但不影响错误拦截和重新编辑。
- **规避方案**：已添加基于 DOM 的兜底高亮动画（CSS Ring）。

### 2. Diff 详情粒度与可读性仍可提升 (Backend)
- **现象**：当前 `GET /api/baselines/{id}/diff` 已能返回深层 `field_path`（如 `params.metric_type`）并提供变更摘要，但对复杂结构的“人类可读解释”仍偏粗粒度。
- **影响**：Diff 视图的中栏明细在复杂规则下仍可能需要人工对照前后快照。
- **规避方案**：前端已容错，仍可在必要时展示完整前/后快照。

### 3. 多人并发编辑冲突 (Backend)
- **现象**：目前 `publish` 接口未实现基于 `parent_version` 的乐观锁（Optimistic Locking）校验。如果两个用户同时基于 `v1.0` 进行编辑并发布，后发布者会覆盖前者的修改（尽管底层写入是原子的）。
- **影响**：存在并发覆盖风险。
- **规避方案**：当前仅作为单用户演示系统，暂不涉及并发操作。

---

## 二、未来增强 (Future Enhancements)
这些是计划在下一阶段（Phase 2/3）引入的系统级架构与产品化能力提升。

### 1. 接入真实的 RBAC 权限与用户信息
- **目标**：在 FastAPI 中接入 `Depends(get_current_user)`，提取真实的 JWT Token。
- **价值**：将 `version_history_meta` 中的 `publisher` 从硬编码的 `"admin"` 替换为真实的用户名，并在前端根据权限控制“发布”与“回滚”按钮的亮起状态。

### 2. 引入 Monaco Editor 提升编辑体验
- **目标**：将中栏 EditorView 中的原生文本域或简易 JSON 表单替换为 `@monaco-editor/react`。
- **价值**：支持代码高亮、语法检查、折叠，并且能够完美支持将 `validate` 返回的 `field_path` 映射为具体的代码行号和错误波浪线（Markers）。

### 3. 持久化层迁移至关系型数据库
- **目标**：将当前的 `baselines.json` 文件存储替换为 PostgreSQL + SQLAlchemy。
- **价值**：支持海量规则基线、复杂的树状查询优化、事务隔离以及高可用部署。

### 4. 完善发布审批流 (Approval Workflow)
- **目标**：在 `publish_checking` 和 `published` 之间引入真实的审批状态（Pending Approval）。
- **价值**：支持企业级的规则发布管控，符合金融/政企客户的合规要求。
