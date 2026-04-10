# Rule Editor UI - 三栏工作台架构设计

本文档记录了 Rule Editor MVP 页面重构后的“三栏规则编辑工作台”架构设计。旨在帮助其他开发者（及 AI 助手）快速理解该页面的目标交互模型、组件职责、状态流以及交互约束。

## 一、页面定位与三栏职责

该页面不仅仅是一个普通的 CRUD 展示页，而是一个**带状态切换、草稿保护、校验联动、Diff 辅助分析的规则编辑工作台**。

布局严格遵循 `280px` (左) / `1fr` (中，自适应) / `420px` (右) 的固定比例约束，保证三栏各自独立滚动。

### 1. 左栏 (Left Column - BaselineList)
- **定位**：导航选择区。
- **职责**：展示基线列表、草稿、历史版本、规则分组等导航对象。仅支持点击切换当前上下文。
- **约束**：绝对不负责复杂编辑和表单提交。它是纯粹的受控组件，依赖外部传入 `items` 与 `selectedId`，仅暴露 `onSelect` 事件。

### 2. 中栏 (Center Column - RuleEditor)
- **定位**：唯一主编辑区。
- **职责**：负责表单编辑、规则参数编辑、发布确认、历史详情、Diff 主视图展示。
- **约束**：它是唯一可以触发 `dirty` (未保存修改) 状态的区域。内部表单组件作为受控组件，由顶层传入 `draftData`，通过 `onChange` 向外同步草稿状态。

### 3. 右栏 (Right Column - RightPanel)
- **定位**：辅助分析与导航区。
- **职责**：展示字段说明、实时校验结果、Diff 摘要、版本元信息、发布检查结果等。
- **约束**：它不是静态展示区，它可以反向驱动中栏定位（例如点击某条校验错误可跳至对应字段）。绝不承担主输入职责。

## 二、状态管理模型 (State Management)

为了防止三栏组件各自维护割裂的上下文，页面级的共享状态全部提升至顶层容器 (`App.tsx` 或未来的 `RuleEditorPage.tsx`)。

### 核心状态 (`PageState` 在 `src/types/ui.ts`)

```typescript
export interface PageState {
  selectedBaselineId?: string;       // 当前左栏选中的对象 ID
  centerMode: CenterMode;            // 中栏当前模式 ('empty', 'create', 'edit', 'diff' 等)
  rightPanelMode: RightPanelMode;    // 右栏当前模式 ('help', 'validation', 'diff_summary' 等)
  draftData: DraftData;              // 当前编辑中的草稿数据
  dirty: boolean;                    // 是否存在未保存修改
  validationResult: ValidationResult | null; // 校验结果
  diffData: DiffResponse | null;     // Diff 差异数据
}
```

## 三、关键交互时序与约束

### 1. 脏数据守卫 (Dirty Guard)
- **触发条件**：当 `dirty = true` 时，用户尝试切换左栏基线、切换历史版本，或者尝试从中栏编辑态切出。
- **行为约束**：必须弹出确认框 (Modal.confirm)，要求用户选择“放弃修改”或“取消切换”。不能静默丢失用户数据，也不能在有脏数据时直接拉取新上下文。

### 2. 校验与错误联动 (Validation Flow)
1. 用户在中栏修改表单，触发 `dirty = true`。
2. 用户点击“Validate”。中栏通过 props 触发页面层 `handleValidate`。
3. 页面层调用后端 API，更新 `validationResult`，并将 `rightPanelMode` 切换至 `'validation'`。
4. 右栏展示错误，点击错误项触发 `onJumpToField`，通知中栏进行滚动/聚焦定位。

### 3. 发布与 Diff 流转 (Publish & Diff Flow)
1. 左栏选中某 Baseline，进入 `'edit'` 模式，右栏默认加载 `'diff_summary'`。
2. 用户点击中栏“Publish”。
3. 页面层调用后端 API，发布成功后更新左侧标识（若有），并强制清除 `dirty` 状态。
4. 页面层自动刷新当前 Baseline 的 Diff 数据，右栏实时展现发布后的最新差异变更摘要。

## 四、后续演进方向建议
1. **中栏模式扩展**：目前中栏主要支持 `edit`。后续增加 `diff` (明细视图)、`history_detail` (历史只读) 视图时，可将 `RuleEditor.tsx` 拆分为多态组件或采用渲染函数分配。
2. **右栏交互增强**：完善 `onJumpToField` 的真实锚点逻辑（结合 `useRef` 或通过表单的 `scrollToField` 方法）。
3. **状态抽取**：当逻辑继续膨胀时，将 `App.tsx` 中关于 `pageState` 和接口调用的逻辑抽离为自定义 Hook（例如 `useRuleEditorPage`），保持视图层纯净。
