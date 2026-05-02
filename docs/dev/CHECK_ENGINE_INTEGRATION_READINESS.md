# Check Engine Integration Readiness Audit

> **Status:** SCAFFOLD PHASE — RealEngineAdapter scaffold + LocalInputReader scaffold ready
> **Scope:** RealEngineAdapter is scaffold only. LocalInputReader scaffold ready for input file reading.
> **Last updated:** 2026-05-02

---

## 1. 当前 Engine 状态

### 1.1 实现概况

| 组件 | 状态 | 说明 |
|------|------|------|
| `EngineAdapter` (interface) | ✅ 已定义 | 抽象接口，定义 engine 契约 |
| `MockEngineAdapter` | ✅ 当前默认 | 返回 mock 数据，无真实计算 |
| `RealEngineAdapter` | 🚧 Scaffold | 所有方法 raise NotImplementedError |
| `engine/provider.py` | ✅ 已实现 | 支持 TOPOCHECKER_ENGINE=mock\|real 环境变量 |
| `LocalInputReader` | 🚧 Scaffold | 读取本地 Excel/CSV 文件 |

### 1.2 EngineProvider 切换机制

`backend/engine/provider.py` 提供 engine 切换能力：

```python
from backend.engine import get_engine

# 默认返回 MockEngineAdapter（安全）
engine = get_engine()

# 设置 TOPOCHECKER_ENGINE=real 可切换到 RealEngineAdapter（scaffold）
# 警告：RealEngineAdapter 所有方法 raise NotImplementedError
```

| 环境变量 | 值 | 返回 | 用途 |
|----------|-----|------|------|
| `TOPOCHECKER_ENGINE` | `mock` (默认) | `MockEngineAdapter` | 开发/测试/生产 |
| `TOPOCHECKER_ENGINE` | `real` | `RealEngineAdapter` | 仅开发测试 scaffold |

**警告**：`TOPOCHECKER_ENGINE=real` 仅用于开发测试。RealEngineAdapter 是 scaffold，所有方法抛出 NotImplementedError。

### 1.3 输入文件读取

`backend/input/` 模块提供本地输入文件读取能力（详见 `LOCAL_INPUT_FILE_READER.md`）：

- `LocalInputReader`: 读取 .xlsx/.xls/.csv 文件
- `normalize_raw_dataset()`: 转换为中间标准化表示
- 后续将接入 RealEngineAdapter.start_recognition()

### 1.4 EngineAdapter 方法清单

`backend/engine/interface.py` 定义以下抽象方法：

| 方法 | 分类 | 当前输入 | 当前输出 | Mock 实现 |
|------|------|----------|----------|-----------|
| `get_recognition_status()` | Recognition | 无 | `str` (status) | 硬编码 `"not_started"` |
| `start_recognition(data_source_id, scope_id)` | Recognition | `str, str` | `str` (recognition_id) | 硬编码 `"rec-001"` |
| `get_recognition_result(recognition_id)` | Recognition | `str` | `RecognitionResult` | 硬编码 150 devices |
| `confirm_recognition(recognition_id)` | Recognition | `str` | `bool` | 硬编码 `True` |
| `start_check(baseline_id, data_source_id, scope_id, ...)` | Execution | `str, str, str, Optional[str], Optional[str]` | `str` (run_id) | 硬编码 `"run-new-001"` |
| `get_run_status(run_id)` | Execution | `str` | `str` (status) | 硬编码 `"completed"` |
| `get_bundle(run_id)` | Results | `str` | `Optional[CheckResultBundle]` | 委托 repository |
| `get_issue(issue_id)` | Results | `str` | `Optional[IssueItem]` | 委托 repository |
| `get_recheck_diff(base_run_id, target_run_id)` | Diff | `str, str` | `Optional[RecheckDiffSnapshot]` | 委托 repository |
| `list_data_sources()` | Metadata | 无 | `list[DataSource]` | 委托 repository |
| `list_scopes()` | Metadata | 无 | `list[ExecutionScope]` | 委托 repository |

### 1.3 Mock 数据标记

以下方法返回硬编码 mock 数据（非 repository 委托）：

- ✅ `get_recognition_status()` → `"not_started"`
- ✅ `start_recognition()` → `"rec-001"`
- ✅ `get_recognition_result()` → `RecognitionResult(150, 0, 0, [])`
- ✅ `confirm_recognition()` → `True`
- ✅ `start_check()` → `"run-new-001"`
- ✅ `get_run_status()` → `"completed"`

以下方法委托 repository（非 mock 硬编码，但数据仍来自 mock fixtures）：

- ⚠️ `get_bundle()` → repository lookup
- ⚠️ `get_issue()` → repository lookup
- ⚠️ `get_recheck_diff()` → repository lookup
- ⚠️ `list_data_sources()` → repository lookup
- ⚠️ `list_scopes()` → repository lookup

---

## 2. 真实业务流核心数据

### 2.1 数据流概览

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  本地 Excel/CSV  │────▶│  Recognition     │────▶│ Normalized      │
│  输入文件        │     │  设备识别         │     │ Dataset         │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Check Result   │◀────│  Check Engine    │◀────│ Check Task      │
│  Bundle         │     │  规则检查         │     │ (baseline +     │
│                 │     │                  │     │  params + scope)│
└─────────────────┘     └──────────────────┘     └─────────────────┘
        │
        ▼
┌─────────────────┐     ┌──────────────────┐
│  workspace/runs │     │  Recheck Diff    │
│  运行结果 JSON   │     │  复测差异        │
└─────────────────┘     └──────────────────┘
```

### 2.2 各阶段数据定义

#### 2.2.1 本地 Excel / 表格输入

- **来源**：用户上传的 `workspace/inputs/*.xlsx` 或 `.csv`
- **内容**：网络拓扑设备清单（交换机、路由器、线缆等）
- **格式**：表格行 = 设备记录，列 = 属性字段
- **当前状态**：mock 数据源（`DataSource` 模型），无真实文件解析

#### 2.2.2 Recognition Result

- **模型**：`backend/models/execution.py::RecognitionResult`
- **字段**：
  - `recognized_device_count`: 识别到的设备数量
  - `unmatched_device_count`: 未匹配设备数量
  - `out_of_scope_device_count`: 范围外设备数量
  - `warnings`: 识别警告列表
- **当前状态**：mock 硬编码（150 devices, 0 unmatched）
- **真实引擎**：需解析输入文件，识别设备类型和关系

#### 2.2.3 Normalized Dataset

- **说明**：识别后的标准化数据集，供检查引擎使用
- **内容**：结构化设备对象、连接关系、属性值
- **当前状态**：mock 阶段无此概念，直接返回固定数据
- **真实引擎**：recognition 输出 → 内存中的 normalized graph

#### 2.2.4 Check Task

- **说明**：一次检查任务的完整配置
- **组成**：
  - `baseline_id`: 基线规则集
  - `data_source_id`: 数据源
  - `scope_id`: 执行范围
  - `parameter_profile_id`: 参数配置
  - `threshold_profile_id`: 阈值配置
- **当前状态**：通过 API request 传入，无持久化
- **真实引擎**：需持久化到 `workspace/tasks/{task_id}.json`

#### 2.2.5 Check Result Bundle

- **模型**：`backend/models/execution.py::CheckResultBundle`
- **字段**：
  - `bundle_id`: 结果包 ID
  - `run_id`: 关联运行 ID
  - `baseline_id`: 基线 ID
  - `severity_summary`: 严重等级统计
  - `issue_count`: 问题总数
  - `issues`: 问题详情列表
- **当前状态**：mock fixtures（`workspace/inputs/bundles.json`）
- **真实引擎**：检查完成后生成，写入 `workspace/runs/{run_id}.json`

#### 2.2.6 Issue Detail

- **模型**：`backend/models/execution.py::IssueItem`
- **字段**：
  - `issue_id`, `run_id`, `rule_id`, `rule_name`
  - `severity`: critical/high/medium/low/info
  - `entity_type`, `entity_id`, `entity_name`
  - `message`: 问题描述
  - `parameters`: 规则参数值
- **当前状态**：mock fixtures
- **真实引擎**：检查过程中逐条生成

#### 2.2.7 Recheck Diff

- **模型**：`backend/models/diff.py::RecheckDiffSnapshot`
- **字段**：
  - `diff_id`, `base_run_id`, `target_run_id`
  - `issue_count_change`: added/removed/unchanged/severity_changed
  - `added_issues`: 新增问题列表
  - `removed_issues`: 消除问题列表
  - `changed_issues`: 严重程度变化列表
  - `unchanged_issues`: 未变化问题列表
- **当前状态**：mock fixtures（`workspace/inputs/recheck_diffs.json`）
- **真实引擎**：backend 对比两个 CheckResultBundle 生成
- **重要**：前端不计算 diff，由 engine/backend 负责

---

## 3. 与 FileRepository / Workspace 的关系

### 3.1 数据流向

```
EngineAdapter (future RealEngineAdapter)
    │
    ├── start_check() ──▶ workspace/tasks/{task_id}.json  (保存任务)
    │
    ├── get_run_status() ──▶ workspace/runs/{run_id}.json  (读取状态)
    │
    ├── get_bundle() ──▶ workspace/runs/{run_id}.json  (读取结果)
    │
    └── get_recheck_diff() ──▶ 对比两个 run JSON 生成 diff
```

### 3.2 Workspace 文件映射

| Engine 操作 | Workspace 文件 | 说明 |
|-------------|----------------|------|
| 读取数据源 | `workspace/inputs/*.xlsx` | 用户上传的原始文件 |
| 保存任务 | `workspace/tasks/{task_id}.json` | 检查任务配置 |
| 保存运行 | `workspace/runs/{run_id}.json` | 运行结果和 bundle |
| 保存快照 | `workspace/snapshots/{version_id}.json` | 基线版本快照 |
| 读取基线 | `workspace/inputs/baseline_*.json` | 基线规则配置 |

### 3.3 FileRepository 作用

- FileRepository 负责 **读取** workspace JSON 文件
- RealEngineAdapter 负责 **写入** 检查结果到 workspace
- 两者通过 `WorkspaceManager` 协作，不直接交互

---

## 4. Recognition Confirm 流程接入真实 Engine

### 4.1 当前流程（Mock）

```
POST /recognition/start ──▶ MockEngineAdapter.start_recognition()
                              返回 "rec-001"

GET /recognition/status ──▶ MockEngineAdapter.get_recognition_status()
                              返回 "not_started"

POST /recognition/confirm ──▶ MockEngineAdapter.confirm_recognition()
                              返回 True
```

### 4.2 真实引擎流程（未来）

```
POST /recognition/start ──▶ RealEngineAdapter.start_recognition()
                              1. 读取 workspace/inputs/*.xlsx
                              2. 解析设备列表
                              3. 识别设备类型和关系
                              4. 生成 recognition_id
                              5. 返回 recognition_id

GET /recognition/status ──▶ RealEngineAdapter.get_recognition_status()
                              返回 "ready" (识别完成)

GET /recognition/result ──▶ RealEngineAdapter.get_recognition_result()
                              返回 RecognitionResult
                              (recognized/unmatched/out_of_scope counts)

POST /recognition/confirm ──▶ RealEngineAdapter.confirm_recognition()
                              1. 标记 recognition 为 confirmed
                              2. 生成 normalized dataset
                              3. 允许后续 check 执行
                              4. 返回 True
```

### 4.3 接入要点

- recognition 结果需持久化到 `workspace/`（如 `workspace/recognition/{rec_id}.json`）
- confirm 后生成 normalized dataset，供 check 阶段使用
- 未 confirm 前不能执行 check

---

## 5. Check Result 写入 Workspace

### 5.1 写入时机

| 阶段 | 写入文件 | 内容 |
|------|----------|------|
| Task 创建 | `workspace/tasks/{task_id}.json` | 检查任务配置 |
| Check 开始 | `workspace/runs/{run_id}.json` | 初始状态（status: queued） |
| Check 完成 | `workspace/runs/{run_id}.json` | 完整结果（status: completed, bundle, issues） |
| 版本发布 | `workspace/snapshots/{version_id}.json` | 基线版本快照 |

### 5.2 Run JSON 结构

```json
{
  "run_id": "run-2024-001",
  "task_id": "task-001",
  "baseline_id": "baseline-001",
  "status": "completed",
  "severity_summary": {
    "critical": 2,
    "high": 5,
    "medium": 12,
    "low": 3,
    "info": 0
  },
  "device_count": 150,
  "issue_count": 22,
  "bundle_id": "bundle-001",
  "data_source_id": "ds-001",
  "scope_id": "scope-full",
  "started_at": "2024-01-15T09:05:00Z",
  "completed_at": "2024-01-15T09:05:30Z"
}
```

### 5.3 写入职责划分

- **EngineAdapter**: 执行检查，生成原始结果
- **RunService**: 调用 engine，将结果写入 workspace via WorkspaceManager
- **FileRepository**: 读取已写入的 run JSON 供 API 返回

---

## 6. Recheck Diff 生成责任

### 6.1 原则

> **Recheck diff 必须由 engine/backend 生成，前端不计算 diff。**

### 6.2 当前实现

- `DiffService` 调用 `MockEngineAdapter.get_recheck_diff()`
- MockEngineAdapter 委托 repository 读取预计算 diff
- 前端接收完整的 `RecheckDiffSnapshot`，直接渲染

### 6.3 真实引擎实现

- `RealEngineAdapter.get_recheck_diff(base_run_id, target_run_id)` 应：
  1. 读取两个 run 的 `CheckResultBundle`
  2. 对比 issues 列表
  3. 计算 added/removed/changed/unchanged
  4. 返回 `RecheckDiffSnapshot`
- 或委托 `DiffService` 直接对比两个 bundle 生成

### 6.4 禁止事项

- ❌ 前端不计算 diff（不对比 issue ID 集合）
- ❌ 前端不生成 added_issues / removed_issues
- ✅ 前端只渲染 backend 返回的预计算 diff 快照

---

## 7. 真实 Engine 输入需求

### 7.1 必需输入

| 输入 | 来源 | 格式 |
|------|------|------|
| 设备数据文件 | `workspace/inputs/*.xlsx` | Excel/CSV |
| 基线规则集 | `workspace/inputs/rulesets.json` + `rules.json` | JSON |
| 参数配置 | `workspace/inputs/parameter_profiles.json` | JSON |
| 阈值配置 | `workspace/inputs/threshold_profiles.json` | JSON |
| 执行范围 | `workspace/inputs/execution_scopes.json` | JSON |
| 作用域选择器 | `workspace/inputs/scope_selectors.json` | JSON |

### 7.2 运行时输入

| 输入 | 说明 |
|------|------|
| `baseline_id` | 使用哪个基线规则集 |
| `data_source_id` | 使用哪个数据源文件 |
| `scope_id` | 检查范围（全量/增量/指定设备） |
| `parameter_profile_id` | 规则参数值 |
| `threshold_profile_id` | 阈值配置 |

---

## 8. 真实 Engine 输出格式

### 8.1 直接输出

| 输出 | 模型 | 说明 |
|------|------|------|
| `RecognitionResult` | `execution.py` | 识别结果统计 |
| `CheckResultBundle` | `execution.py` | 检查结果包 |
| `IssueItem` | `execution.py` | 单条问题详情 |
| `RecheckDiffSnapshot` | `diff.py` | 复测差异快照 |

### 8.2 持久化输出

| 输出 | 目标文件 |
|------|----------|
| 运行记录 | `workspace/runs/{run_id}.json` |
| 任务定义 | `workspace/tasks/{task_id}.json` |
| 版本快照 | `workspace/snapshots/{version_id}.json` |
| 报告文件 | `workspace/reports/{report_id}.html` |

---

## 9. 接入检查清单

### 9.1 接口准备

- [x] `EngineAdapter` 抽象接口已定义
- [x] 所有方法签名已确定
- [x] 输入/输出模型已定义（Pydantic）
- [x] `RealEngineAdapter` scaffold 已实现

### 9.2 数据准备

- [x] `CheckResultBundle` 模型
- [x] `IssueItem` 模型
- [x] `RecheckDiffSnapshot` 模型
- [x] `RecognitionResult` 模型
- [x] Workspace 目录结构
- [x] WorkspaceManager 文件读写

### 9.3 服务层准备

- [x] `ExecutionService` 调用 engine via provider
- [x] `RunService` 调用 engine via provider
- [x] `DiffService` 调用 engine via provider
- [ ] 实现真实 engine 方法（进行中）
- [ ] 写入 workspace 逻辑（未来）

### 9.4 路由层准备

- [x] `/recognition/start`
- [x] `/recognition/status`
- [x] `/recognition/confirm`
- [x] `/checks/start`
- [x] `/runs/{run_id}`
- [x] `/bundles/{bundle_id}`
- [x] `/diff/recheck`

---

## 10. 禁止事项

- ❌ **不实现真实检查引擎** — RealEngineAdapter 仅 scaffold（raise NotImplementedError）
- ❌ **不接数据库** — 不使用 SQLite / PostgreSQL / ORM
- ❌ **不引入 AI/LLM** — 检查引擎基于规则，不依赖 AI
- ❌ **不修改 API response** — 保持现有 API 契约
- ❌ **不修改前端业务页面** — 前端不感知 engine 变化
- ❌ **不移除 MockEngineAdapter** — 保留 mock 实现用于测试
- ❌ **不恢复 UI diff 计算** — diff 继续由 backend 生成
- ❌ **不使用 TOPOCHECKER_ENGINE=real 生产** — scaffold 仅开发测试用

---

## 11. 下一步建议

1. **实现 RealEngineAdapter 方法**
   - 当前所有方法 raise NotImplementedError
   - 逐步实现从 Excel 读取输入
   - 实现 normalized dataset 生成
   - 实现规则引擎
   - 保持 mock fallback

2. **保留 mock 兼容性**
   - `TOPOCHECKER_ENGINE=mock`（默认）继续工作
   - `TOPOCHECKER_ENGINE=real` 用于开发测试 scaffold
   - CI 继续运行 mock 模式

3. **完善 workspace 写入**
   - check 完成后自动写入 `workspace/runs/`
   - 支持版本快照保存到 `workspace/snapshots/`

4. **安全护栏**
   - `real_engine.py` 不读写真实 Excel
   - `real_engine.py` 不接数据库
   - API snapshot 保持通过
