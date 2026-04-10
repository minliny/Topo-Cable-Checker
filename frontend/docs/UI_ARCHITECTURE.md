# Rule Editor UI - 三栏工作台架构设计

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

页面抛弃了传统的“点击按钮 -> 调用 API -> 设值”的命令式流程，转而采用**Reducer 集中管理状态**和**派发 Action 触发状态转移**的架构。所有的 UI 都是当前 `PageState` 的纯函数映射。

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
}
```

### 状态流转时序 (State Transitions)

**流转原则**：所有状态变更均通过 `dispatch(Action)` 由 `pageReducer` 集中处理，保证状态流转的安全性和一致性。

1. **进入编辑态 (Edit)**
   - 左栏选择 draft -> Dispatch `SWITCH_CONTEXT` -> `centerMode = 'edit'`, `rightPanelMode = 'help'` -> 加载 draft 数据。
   - 用户编辑 -> Dispatch `UPDATE_DRAFT` -> `dirty = true`。

2. **触发校验 (Validate)**
   - 用户点击校验 -> Dispatch `REQUEST_VALIDATION` -> 显示 loading。
   - API 调用成功 -> Dispatch `VALIDATION_SUCCESS` -> 更新 `validationResult`, `rightPanelMode = 'validation'`。

3. **完整发布工作流闭环 (Publish Flow)**
   - **预备**：用户点击发布准备 -> Dispatch `PREPARE_PUBLISH` -> `centerMode = 'publish_confirm'`, `rightPanelMode = 'publish_check'`。
   - **发起**：确认发布 -> Dispatch `REQUEST_PUBLISH` -> `centerMode = 'publish_checking'` (显示过渡态)。
   - **阻断**：若接口校验不通过 -> Dispatch `PUBLISH_BLOCKED` -> `centerMode = 'publish_blocked'`，展示阻断项。可点击返回编辑态修复。
   - **成功**：若接口成功 -> Dispatch `PUBLISH_SUCCESS` -> `centerMode = 'published'`, `dirty = false`。
   - **收尾**：短暂展示 published 成功页后，自动 Dispatch `GO_TO_HISTORY` -> `centerMode = 'history_detail'`, `rightPanelMode = 'version_meta'`, 左栏精准定位到新版本节点。

4. **查看历史与 Diff (History & Diff)**
   - 左栏选择某版本 (v1.0) -> (触发 Dirty Guard 若有脏数据) -> 确认后 Dispatch `SWITCH_CONTEXT` -> `centerMode = 'history_detail'`。
   - 用户点击查看 Diff -> Dispatch `REQUEST_DIFF` -> 显示 loading。
   - API 调用成功 -> Dispatch `DIFF_SUCCESS` -> `centerMode = 'diff'`, `rightPanelMode = 'diff_summary'`。

5. **回滚候选语义补完 (Rollback Flow)**
   - 历史详情点击 Rollback -> Dispatch `REQUEST_ROLLBACK_CONFIRM` -> `centerMode = 'rollback_confirm'`。
   - (若已有普通草稿，触发冲突处理询问)。
   - 确认回滚 -> Dispatch `REQUEST_ROLLBACK` -> `centerMode = 'rollback_preparing'` (加载历史配置)。
   - 加载完毕 -> Dispatch `ROLLBACK_READY` -> `centerMode = 'rollback_ready_edit'`, `selectedNodeType = 'rollback_candidate'`, `dirty = true`。左栏显式标记为回滚候选草稿，并记录来源版本 ID。

## 三、真实后端 DTO 契约映射

即使当前采用 Mock 数据，UI 状态模型也已对齐真实后端接口结构 (`src/types/dto.ts`)。

- **BaselineNodeDTO**: 包含 `parentId`, `source_version_id`, `source_version_label` 等关系字段，支撑树状结构。
- **VersionMetaDTO**: 记录版本详细信息，如 `publisher`, `published_at`, `parent_version_id`。
- **ValidationIssueDTO**: 包含 `field_path`, `issue_type`, `message` 等，支撑右栏反向定位。
- **PublishResultDTO**: 支持携带 `blocked_issues`。
- **RollbackCandidateDTO**: 明确记录 `source_version_id` 和 `draft_data`。
- **DiffSourceTargetDTO**: 支持结构化的差异项列表 `DiffRuleDTO`，用于中栏的高亮对比。

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