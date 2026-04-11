# Rule Editor UI - 三栏工作台架构设计

> **当前状态更新 (2026-04-10)**：本项目已经完成**前端三栏架构、强类型 DTO Adapter 以及与 FastAPI 真实后端的网络联调、Diff 算法与 Publish 真实持久化**。系统已正式进入“稳定可验收阶段”。后续开发者可以直接参考 `docs/ACCEPTANCE_CHECKLIST.md` 运行端到端回归验收。

本文档记录了 Rule Editor MVP 页面重构后的“三栏规则编辑工作台”架构设计。旨在帮助其他开发者（及 AI 助手）快速理解该页面的目标交互模型、组件职责、状态流以及交互约束。

## 一、页面定位与三栏职责

该页面不仅仅是一个普通的 CRUD 展示页，而是一个**带状态切换、草稿保护、校验联动、Diff 辅助分析的规则编辑工作台**。

布局严格遵循 `280px` (左) / `1fr` (中，自适应) / `420px` (右) 的固定比例约束，保证三栏各自独立滚动。

### 1. 左栏 (Left Column - BaselineList)
- **定位**：导航选择区。支持树形结构展示 (Baseline 下包含 Draft 与多个 Version)。
- **职责**：展示基线列表、普通草稿 (`working_draft`)、回滚候选草稿 (`rollback_candidate`)、历史版本 (`published_version`) 等导航对象。仅支持点击切换当前上下文。
- **约束**：绝对不负责复杂编辑和表单提交。它是纯粹的受控组件，依赖外部传入 `items` 与 `selectedId`，仅暴露 `onSelect` 事件。节点模型支持 `parentId`, `sourceVersionId` 等关系字段，不强耦合显示文本。

### 2. 中栏 (Center Column - CenterViews)
- **定位**：唯一主视图区。
- **职责**：完全由 `centerMode` 驱动的纯粹受控渲染区，包含表单编辑、规则参数编辑、发布确认、发布预检 (`publish_checking`)、发布阻塞 (`publish_blocked`)、发布成功 (`published`)、历史详情、Diff 主视图展示。
- **约束**：它是唯一可以触发 `dirty` (未保存修改) 状态的区域。内部表单组件作为受控组件，由顶层传入 `draftData`，通过 `onChange` 向外同步草稿状态。不同模式必须渲染不同的独立组件，严禁在一个组件内混合不同模式的 UI。

### 3. 右栏 (Right Column - RightPanel)
- **定位**：辅助分析与操作工具区。
- **职责**：展示字段说明、实时校验结果、Diff 摘要、版本元信息、发布检查结果等。
- **约束**：它不是静态展示区，它可以反向驱动中栏定位（例如点击某条校验错误可跳至对应字段）。绝不承担主输入职责。

## 二、状态机驱动模型 (State Machine Driven)

页面抛弃了传统的“点击按钮 -> 调用 API -> 设值”的命令式流程，转而采用**Reducer 集中管理状态**和**派发 Action 触发状态转移**的架构。所有的 UI 都是当前 `PageState` 的纯函数映射。所有的状态转换都受到明确的 `guard` 保护，拒绝不合法的隐式跳转。

### 核心状态 (`PageState` 在 `src/types/ui.ts`)

```typescript
export interface PageState {
  // 上下文导航状态
  selectedBaselineId?: string;       // 当前左栏选中的基线 ID
  selectedVersionId?: string;        // 当前左栏选中的具体版本 ('draft' 或 'v1.x')
  selectedNodeType?: BaselineNodeType; // 节点类型，如 rollback_candidate
  
  // 核心视图模式驱动
  centerMode: CenterMode;            // 中栏当前模式 ('edit', 'diff', 'publish_blocked', 'published' 等)
  rightPanelMode: RightPanelMode;    // 右栏当前模式 ('help', 'validation', 'diff_summary' 等)
  
  // 数据与防丢保护
  draftData: DraftData;              // 当前编辑中的草稿数据
  dirty: boolean;                    // 是否存在未保存修改
  
  // 异步数据结果缓存
  validationResult: ValidationResult | null; // 校验结果
  publishBlockedIssues: any[] | null;        // 发布被阻断时的错误信息
  diffData: DiffResponse | null;             // Diff 差异数据
  
  // Diff 上下文
  diffContext?: {
    sourceVersionId: string;
    targetVersionId: string;
  };
}
```

## 三、状态迁移总表 (State Transition Table)

系统所有关键的视图和模式切换都被严格定义在 `pageReducer` 中。以下是核心状态的迁移矩阵，任何脱离下表的跳转都会被 Guard 拒绝：

### 1. 发布闭环工作流 (Publish Flow)
| Current State (Center) | Action | Guard 校验 | Next State (Center) | 状态变更说明 |
|------------------------|--------|-----------|---------------------|--------------|
| `edit` / `rollback_ready_edit` | `PREPARE_PUBLISH` | 必须在编辑态 | `publish_confirm` | 唤起右侧 `publish_check` 面板 |
| `publish_confirm` / `publish_blocked` | `CANCEL_PUBLISH` | 必须在确认或阻塞态 | `edit` 或 `rollback_ready_edit` | 退回对应的草稿态 |
| `publish_confirm` | `REQUEST_PUBLISH` | 必须在确认态 | `publish_checking` | 锁定界面，开始网络请求 |
| `publish_checking` | `PUBLISH_BLOCKED` | 必须在校验态 | `publish_blocked` | 展示 `publishBlockedIssues` |
| `publish_checking` | `PUBLISH_SUCCESS` | 必须在校验态 | `published` | **正式进入发布成功态**，清理 `dirty=false` |
| `published` | `TRIGGER_POST_PUBLISH_NAVIGATION` | **必须在 published 态** | `history_detail` | 收尾操作：切换上下文至新版本，刷新左栏 |

> **关于 `published` 的正式状态声明**：
> `published` 是一个**显式停留结果态**，提供成功的视觉反馈。它不允许组件隐式地使用 `setTimeout` 盲目跳转，而是必须显式派发 `TRIGGER_POST_PUBLISH_NAVIGATION` 才能退出该状态进入历史详情页。

### 2. 回滚候选生命周期 (Rollback Lifecycle)
| Current State (Center) | Action | Guard 校验 | Next State (Center) | 状态变更说明 |
|------------------------|--------|-----------|---------------------|--------------|
| `history_detail` | `REQUEST_ROLLBACK_CONFIRM` | 必须在历史版本页 | `rollback_confirm` | - |
| `rollback_confirm` | `REQUEST_ROLLBACK` | 必须在确认态 | `rollback_preparing`| - |
| `rollback_preparing` | `ROLLBACK_READY` | 必须在准备态 | `rollback_ready_edit`| **创建回滚候选**。`dirty=true`，节点标记为 `rollback_candidate` |
| `rollback_ready_edit` | `DISCARD_ROLLBACK_CANDIDATE` | - | `empty` | 放弃回滚，清空脏数据，左栏退回 |

> **`rollback_candidate` 生命周期规则**：
> 1. **创建时机**：当用户在 `history_detail` 确认回滚且数据加载完毕时。
> 2. **唯一性**：每个基线下只允许存在一个活跃的 `working_draft` 或 `rollback_candidate`。若冲突需弹窗提示用户覆盖。
> 3. **销毁条件**：(1) 发布成功转为正式版本；(2) 手动点击 Discard；(3) 被新的草稿覆盖。
> 4. **UI 表现**：左栏树独立显示紫色节点并记录 `sourceVersionId`。

### 3. 对比工作流 (Diff Flow)
Diff 状态现已不再是简单的 mode，它依赖完整的上下文环境：
| Current State (Center) | Action | Next State (Center) | 状态变更说明 |
|------------------------|--------|---------------------|--------------|
| `history_detail` / `edit` / `rollback_ready_edit` | `REQUEST_DIFF` | 保持当前态 | 注入 `diffContext` (source/target ID) |
| (Any) | `DIFF_SUCCESS` | `diff` | 加载数据成功，右栏切至 `diff_summary` |
| `diff` | `CLOSE_DIFF` | 恢复原状 | 根据当前选中的节点类型退回 `edit` 或 `history_detail`，清空 `diffContext` |

---

## 四、真实后端 API 与 Adapter 适配层 (API Integration & Dual Channel)

为保障后端联调顺利，系统采用了**API 适配层 (Adapter)** 和 **Mock/Real 双通道策略**，前端 UI 层与 Reducer 绝不直接消费后端原始数据。

> **联调状态更新 (2026-04-10)**：第一轮真实网络联调已完成。所有 6 个核心接口均已接通 FastAPI 真实后端，状态机运行平稳，双通道验证通过。

### 1. 接口联调状态总览

| 接口 | 路由 | 状态 | 页面表现 | 当前已知缺口 (Gap Layer) |
|------|------|------|----------|--------------------------|
| **Baseline Tree** | `GET /baselines` | OK | 左栏树正常渲染，正确派生 root/draft/version 上下文 | 无。后端已实现组树聚合逻辑。 |
| **Version Detail** | `GET /baselines/{id}/versions/{version_id}` | OK | `history_detail` 右栏正常显示版本元信息 | **Domain/Infra**：底层存储目前不记录 `publisher` 等审计字段，暂由后端 API 兜底填充。 |
| **Diff** | `GET /baselines/{id}/diff` | PARTIAL | 中栏/右栏正常展现 Diff 结构与差异项 | **App Service**：后端尚未实现真正的配置 JSON 差异对比，目前仅返回结构化占位数据。 |
| **Validate** | `POST /rules/draft/validate` | OK | 右栏错误列表展示正常，点击可驱动中栏物理定位 | 无。后端已实现从 Domain Error 提取 `field_path`。 |
| **Publish** | `POST /rules/publish/{baseline_id}` | OK | 成功流转至 `publish_blocked` 并展示结构化阻断项 | **App Service**：后端暂未实现真正的落盘 commit 操作，仅模拟版本号生成。 |
| **Rollback** | `POST /rules/rollback` | OK | `rollback_ready_edit` 状态正常，中栏正确填充历史草稿参数 | 无。后端已成功从历史快照中 hydrated 真实数据。 |

### 2. Mock / Real 双通道策略
- 通过环境变量 `VITE_USE_MOCK_API=true/false` 切换 `src/api/client.ts` 中的 Axios Mock Adapter 拦截。
- 不管走哪条通道，API 返回的数据都必须经过 `src/api/adapters.ts` 进行规范化处理。这样在真实接口异常或格式变更时，能快速定位是 Network 还是 Adapter 层的问题。

### 2. API -> Adapter -> DTO -> Reducer 数据流

所有接口均已配备专属 `normalize` 函数，处理缺省值、格式错位与兜底降级：

#### (1) 左栏树加载
- **API**: `GET /api/baselines`
- **Adapter**: `normalizeBaselineTreeResponse`
- **DTO**: `BaselineNodeDTO[]`
- **UI State**: `baselines` 列表。UI 会基于 `type` (root/draft/published/rollback_candidate) 渲染图标，利用 `source_version_id` 追踪回滚来源。若缺失 ID，Adapter 会生成 fallback-id 防止 React Key 报错。

#### (2) 版本元数据加载 (右栏)
- **API**: `GET /api/baselines/{id}/versions/{version_id}`
- **Adapter**: `normalizeVersionDetailResponse`
- **DTO**: `VersionMetaDTO`
- **UI State**: 当 `centerMode = history_detail` 时，填入右栏 `version_meta` 面板展示发布者与日志。

#### (3) 草稿校验
- **API**: `POST /api/rules/draft/validate`
- **Adapter**: `normalizeValidationResponse` (兼容后端新旧版本 `{valid}` vs `{validation_result: {valid}}` 嵌套)
- **DTO**: `ValidationResultDTO` -> 包含 `ValidationIssueDTO[]`
- **UI State**: `validationResult`。当点击某条 `issue` 时，读取 `field_path` 并派发 `JUMP_TO_FIELD` 实现物理滚动。若后端仅返回字符串错误，Adapter 会封装为 `field_path: 'unknown'`。

#### (4) 版本发布
- **API**: `POST /api/rules/publish/{baseline_id}`
- **Adapter**: `normalizePublishResponse`
- **DTO**: `PublishResultDTO`
- **UI State**:
  - 成功：更新左栏，返回 `version_id` 用于触发后续的 `TRIGGER_POST_PUBLISH_NAVIGATION`。
  - 阻断：解析 `blocked_issues` 并填充 `publishBlockedIssues` 触发 `publish_blocked` 视图。

#### (5) 回滚生成
- **API**: `POST /api/rules/rollback`
- **Adapter**: `normalizeRollbackCandidateResponse`
- **DTO**: `RollbackCandidateDTO`
- **UI State**: 触发 `ROLLBACK_READY`。Adapter 会强行提取 `draft_data` 与 `source_version_id` 供 UI 恢复。

#### (6) 差异对比
- **API**: `GET /api/baselines/{id}/diff?source={id}&target={id}`
- **Adapter**: `normalizeDiffResponse`
- **DTO**: `DiffSourceTargetDTO` -> 包含 `DiffRuleDTO[]`
- **UI State**: 写入 `diffData`。右栏基于 `diff_summary` 绘制摘要，中栏基于 `rules` 绘制增删改代码块。Adapter 负责将后端分散的 added/removed/modified 数组聚合成统一的 Rule 列表，或直接消费统一的列表。

### 3. 前端容错与已知联调缺口
- 详见 `docs/API_INTEGRATION_CHECKLIST.md`。重点关注：真实后端的 validation 必须包含 `field_path`；真实后端的 publish 拦截必须包含 `blocked_issues`，否则高级反向定位和拦截面板将退化为普通 Error Toast。

## 四、脏数据守卫 (Dirty Guard)
- **触发条件**：当 `dirty = true` 时，用户尝试切换左栏节点，或者尝试从中栏编辑态切出。
- **行为约束**：必须弹出确认框 (Modal.confirm)，要求用户选择“放弃修改”或“取消切换”。不能静默丢失用户数据，也不能在有脏数据时直接拉取新上下文。

## 五、右栏反向定位交互
右栏的 `ValidationResult` 或 `publishBlockedIssues` 或 `DiffSummary` 必须是可交互的。
- 错误列表点击时：触发 `onJumpToField(fieldPath)`，中栏的表单组件通过 `form.scrollToField(fieldPath)` 等方式将对应输入框滚动至可视区域并高亮。若是 `publish_blocked` 态，则先返回 `edit` 态。
- Diff 列表点击时：触发 `onJumpToRule(ruleId)`，中栏跳转或滚动到具体的规则块。

## 六、当前保留缺口与下一阶段建议
1. **表单反向定位细节**：目前 `targetFieldPath` 仅传递到了 `EditorView`，需要 Antd Form 结合 `scrollToField` 进行实际 DOM 操作。
2. **多语言与 i18n**：目前提示和文案均为硬编码。
3. **真实 API 接入**：需将 `App.tsx` 中的 API 调用替换为真实环境请求。
4. **性能优化**：当 Draft 巨大时，频繁的 `UPDATE_DRAFT` 可能会导致卡顿，需要引入防抖或拆分上下文。