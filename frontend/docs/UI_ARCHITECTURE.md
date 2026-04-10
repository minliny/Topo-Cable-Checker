# Rule Editor UI - 三栏工作台架构设计

本文档记录了 Rule Editor MVP 页面重构后的“三栏规则编辑工作台”架构设计。旨在帮助其他开发者（及 AI 助手）快速理解该页面的目标交互模型、组件职责、状态流以及交互约束。

## 一、页面定位与三栏职责

该页面不仅仅是一个普通的 CRUD 展示页，而是一个**带状态切换、草稿保护、校验联动、Diff 辅助分析的规则编辑工作台**。

布局严格遵循 `280px` (左) / `1fr` (中，自适应) / `420px` (右) 的固定比例约束，保证三栏各自独立滚动。

### 1. 左栏 (Left Column - BaselineList)
- **定位**：导航选择区。支持树形结构展示 (Baseline 下包含 Draft 与多个 Version)。
- **职责**：展示基线列表、草稿、历史版本、规则分组等导航对象。仅支持点击切换当前上下文。
- **约束**：绝对不负责复杂编辑和表单提交。它是纯粹的受控组件，依赖外部传入 `items` 与 `selectedId`，仅暴露 `onSelect` 事件。

### 2. 中栏 (Center Column - CenterViews)
- **定位**：唯一主视图区。
- **职责**：完全由 `centerMode` 驱动的纯粹受控渲染区，包含表单编辑、规则参数编辑、发布确认、历史详情、Diff 主视图展示。
- **约束**：它是唯一可以触发 `dirty` (未保存修改) 状态的区域。内部表单组件作为受控组件，由顶层传入 `draftData`，通过 `onChange` 向外同步草稿状态。不同模式必须渲染不同的独立组件，严禁在一个组件内混合不同模式的 UI。

### 3. 右栏 (Right Column - RightPanel)
- **定位**：辅助分析与操作工具区。
- **职责**：展示字段说明、实时校验结果、Diff 摘要、版本元信息、发布检查结果等。
- **约束**：它不是静态展示区，它可以反向驱动中栏定位（例如点击某条校验错误可跳至对应字段）。绝不承担主输入职责。

## 二、状态机驱动模型 (State Machine Driven)

页面抛弃了传统的“点击按钮 -> 调用 API -> 设值”的命令式流程，转而采用**状态机驱动**和**状态派生副作用**的声明式模型。所有的 UI 都是当前 `PageState` 的纯函数映射。

### 核心状态 (`PageState` 在 `src/types/ui.ts`)

```typescript
export interface PageState {
  // 上下文导航状态
  selectedBaselineId?: string;       // 当前左栏选中的基线 ID
  selectedVersionId?: string;        // 当前左栏选中的具体版本 ('draft' 或 'v1.x')
  
  // 核心视图模式驱动
  centerMode: CenterMode;            // 中栏当前模式 ('edit', 'diff', 'history_detail', 'publish_confirm')
  rightPanelMode: RightPanelMode;    // 右栏当前模式 ('help', 'validation', 'diff_summary' 等)
  
  // 数据与防丢保护
  draftData: DraftData;              // 当前编辑中的草稿数据
  dirty: boolean;                    // 是否存在未保存修改
  
  // 副作用请求信号 (状态机跃迁指令)
  validationRequested: boolean;      // 触发校验副作用的信号
  publishRequested: boolean;         // 触发发布副作用的信号
  diffRequested: boolean;            // 触发拉取 Diff 的信号
  
  // 异步数据结果缓存
  validationResult: ValidationResult | null; // 校验结果
  diffData: DiffResponse | null;             // Diff 差异数据
}
```

### 状态流转时序 (State Transitions)

**流转原则**：按钮点击只改变状态 (`setState`)，`useEffect` 监听状态变化并执行异步副作用 (API 调用)，完成后再次更新状态。

1. **进入编辑态 (Edit)**
   - 左栏选择 draft -> `centerMode = 'edit'`, `rightPanelMode = 'help'` -> 加载 draft 数据。
   - 用户编辑 -> `dirty = true`。

2. **触发校验 (Validate)**
   - 用户点击校验 -> `validationRequested = true`。
   - `useEffect` 捕获到信号 -> 调用 validate API -> 更新 `validationResult`, `validationRequested = false`, `rightPanelMode = 'validation'`。

3. **进入发布确认与发布 (Publish)**
   - 用户点击发布准备 -> `centerMode = 'publish_confirm'`, `rightPanelMode = 'publish_check'`。
   - 确认发布 -> `publishRequested = true`。
   - `useEffect` 捕获到信号 -> 调用 publish API -> 更新左栏树结构, `centerMode = 'history_detail'`, `rightPanelMode = 'version_meta'`, `dirty = false`, `publishRequested = false`。

4. **查看历史与 Diff (History & Diff)**
   - 左栏选择某版本 (v1.0) -> (触发 Dirty Guard 若有脏数据) -> 确认后 `centerMode = 'history_detail'`, `selectedVersionId = 'v1.0'`。
   - 用户点击查看 Diff -> `centerMode = 'diff'`, `rightPanelMode = 'diff_summary'`, `diffRequested = true`。
   - `useEffect` 捕获到信号 -> 调用 diff API -> 更新 `diffData`, `diffRequested = false`。

## 三、状态迁移表 (State Transition Table)

系统行为被收敛在状态迁移和对应的 Effect 队列中，以下是主要业务流的状态流转：

### 1. 规则编辑与校验 (Edit & Validation)
| 起始状态 | 触发动作 | 目标状态 (Center/Right) | 附加副作用 |
|---------|---------|-------------------------|------------|
| (any) | 左栏点击 Draft | `edit` / `help` | 加载 Draft |
| `edit` | 表单输入 | `edit` / 保持不变 | `dirty = true` |
| `edit` | 点击 Validate | `edit` / 保持不变 | 发送 `validationRequested = true` 信号 |
| `edit` | Validation 成功 | `edit` / `validation` | 收到结果，`validationRequested = false` |

### 2. 发布工作流 (Publish Flow)
发布不再是一个简单的按钮，而是一个具有预检和确认的完整流程。
| 起始状态 | 触发动作 | 目标状态 (Center/Right) | 附加副作用 |
|---------|---------|-------------------------|------------|
| `edit` | 点击 Prepare Publish | `publish_confirm` / `publish_check` | |
| `publish_confirm` | 点击 Cancel | `edit` / `validation` | 返回编辑态 |
| `publish_confirm` | 点击 Confirm Publish | 保持不变 | 发送 `publishRequested = true` 信号 |
| `publish_confirm` | Publish 完成 | `history_detail` / `version_meta` | `dirty = false`, `publishRequested = false`, 左栏刷新 |

### 3. 历史与回滚工作流 (History & Rollback Flow)
直接回滚是不安全的，系统必须通过生成“回滚候选草稿”让用户二次确认和修改。
| 起始状态 | 触发动作 | 目标状态 (Center/Right) | 附加副作用 |
|---------|---------|-------------------------|------------|
| (any) | 左栏点击历史版本 | `history_detail` / `version_meta` | 过 Dirty Guard 保护 |
| `history_detail` | 点击 Compare Changes | `diff` / `diff_summary` | 发送 `diffRequested = true` |
| `history_detail` | 点击 Rollback to this | `rollback_confirm` / `version_meta` | |
| `rollback_confirm` | 点击 Cancel | `history_detail` / `version_meta` | |
| `rollback_confirm` | 点击 Confirm Rollback| `rollback_preparing` / `version_meta` | 发送 `rollbackRequested = true` |
| `rollback_preparing`| Rollback 数据加载完毕 | `rollback_ready_edit` / `help` | `dirty = true` (强转为未保存草稿)，加载历史参数至编辑区 |

## 四、脏数据守卫 (Dirty Guard)
- **触发条件**：当 `dirty = true` 时，用户尝试切换左栏节点，或者尝试从中栏编辑态切出。
- **行为约束**：必须弹出确认框 (Modal.confirm)，要求用户选择“放弃修改”或“取消切换”。不能静默丢失用户数据，也不能在有脏数据时直接拉取新上下文。

## 四、右栏反向定位交互
右栏的 `ValidationResult` 或 `DiffSummary` 必须是可交互的。
- 错误列表点击时：触发 `onJumpToField(fieldPath)`，中栏的表单组件通过 `form.scrollToField(fieldPath)` 等方式将对应输入框滚动至可视区域并高亮。
- Diff 列表点击时：触发 `onJumpToRule(ruleId)`，中栏跳转或滚动到具体的规则块。