# Local Workspace File Persistence

> **Status:** SCAFFOLD (Phase 1)  
> **Scope:** Local file persistence only — no database, no SQLite, no ORM.  
> **Last updated:** 2026-05-01

---

## 1. 设计原则

TopoChecker 是**本地轻量工具**，所有数据持久化通过**本地 JSON 文件**完成：

- **不接数据库** — 不引入 SQLite / PostgreSQL / MySQL / MongoDB
- **不接 ORM** — 不引入 SQLAlchemy / Peewee / Tortoise / Prisma
- **本地文件优先** — 任务、运行、快照、报告均保存为本地文件
- **可移植** — workspace/ 目录可整体复制、备份、归档

---

## 2. Workspace 目录结构

```
workspace/
├── inputs/          # 用户上传的原始输入文件（Excel, CSV, JSON）
├── tasks/           # 任务定义 JSON（Task Definition）
├── runs/            # 运行结果 JSON（Run Result）
├── snapshots/       # 版本快照 JSON（Version Snapshot）
├── reports/         # 报告文件（HTML, CSV, Excel）+ 元数据 JSON
└── exports/         # 导出数据（JSON, CSV, Excel）
```

### 2.1 目录说明

| 目录 | 用途 | 文件格式 |
|------|------|----------|
| `inputs/` | 存放用户上传的原始数据文件 | `.xlsx`, `.csv`, `.json` |
| `tasks/` | 存放检查任务定义 | `.json` |
| `runs/` | 存放检查运行结果 | `.json` |
| `snapshots/` | 存放基线版本快照 | `.json` |
| `reports/` | 存放生成的报告文件 | `.html`, `.csv`, `.xlsx` + `.json` 元数据 |
| `exports/` | 存放导出的数据文件 | `.json`, `.csv`, `.xlsx` |

---

## 3. JSON 文件格式

### 3.1 Task Definition (`workspace/tasks/{task_id}.json`)

```json
{
  "task_id": "task-001",
  "baseline_id": "BL-2024-Q1",
  "data_source_id": "DS-001",
  "scope_id": "SCOPE-ALL",
  "parameter_profile_id": "PP-DEFAULT",
  "threshold_profile_id": "TP-STANDARD",
  "created_at": "2024-01-15T09:00:00Z",
  "updated_at": "2024-01-15T09:00:00Z"
}
```

### 3.2 Run Result (`workspace/runs/{run_id}.json`)

```json
{
  "run_id": "run-20240115-001",
  "task_id": "task-001",
  "baseline_id": "BL-2024-Q1",
  "status": "completed",
  "started_at": "2024-01-15T09:05:00Z",
  "completed_at": "2024-01-15T09:05:30Z",
  "bundle_id": "bundle-001",
  "severity_summary": {
    "critical": 2,
    "high": 5,
    "medium": 12,
    "low": 3
  }
}
```

### 3.3 Version Snapshot (`workspace/snapshots/{version_id}.json`)

```json
{
  "version_id": "v1.2.0",
  "baseline_id": "BL-2024-Q1",
  "snapshot": {
    "ruleset_ids": ["RS-001", "RS-002"],
    "parameter_profile_id": "PP-DEFAULT",
    "threshold_profile_id": "TP-STANDARD",
    "scope_id": "SCOPE-ALL"
  },
  "created_at": "2024-01-10T00:00:00Z"
}
```

### 3.4 Report Metadata (`workspace/reports/{report_id}.json`)

```json
{
  "report_id": "report-001",
  "run_id": "run-20240115-001",
  "format": "html",
  "file_path": "workspace/reports/report-001.html",
  "generated_at": "2024-01-15T09:06:00Z"
}
```

---

## 4. 数据生命周期

### 4.1 任务生命周期

1. **创建** — 用户在 ExecutionConfig 页面配置检查任务
2. **保存** — 任务定义保存为 `workspace/tasks/{task_id}.json`
3. **执行** — 触发检查，生成运行记录
4. **归档** — 任务可长期保留在本地 workspace 中

### 4.2 运行生命周期

1. **排队** — 创建运行记录，`status: "queued"`
2. **执行中** — 检查引擎处理，`status: "running"`
3. **完成** — 检查结果保存为 `workspace/runs/{run_id}.json`
4. **报告生成** — 基于运行结果生成报告到 `workspace/reports/`

### 4.3 快照生命周期

1. **基线发布** — 发布基线版本时创建快照
2. **保存** — 快照保存为 `workspace/snapshots/{version_id}.json`
3. **对比** — 版本对比时加载两个快照进行 diff
4. **回滚** — 可从快照恢复基线配置

---

## 5. 实现架构

```
backend/
├── workspace/
│   ├── __init__.py      # 导出 WorkspacePaths, WorkspaceManager
│   ├── paths.py         # 目录路径定义
│   ├── schema.py        # JSON 结构 schema 参考（非强制校验）
│   └── manager.py       # 文件读写操作
├── repositories/
│   ├── interface.py     # Repository 抽象接口
│   ├── mock_repository.py   # Mock 实现（默认）
│   ├── file_repository.py   # 本地文件实现（scaffold）
│   └── provider.py      # 仓库提供者（默认 mock）
```

### 5.1 WorkspaceManager

- `save_task(task: dict) -> Path` — 保存任务到 `workspace/tasks/`
- `load_task(task_id: str) -> dict | None` — 从 `workspace/tasks/` 读取任务
- `list_tasks() -> list[dict]` — 列出所有任务
- `save_run(run: dict) -> Path` — 保存运行结果到 `workspace/runs/`
- `load_run(run_id: str) -> dict | None` — 从 `workspace/runs/` 读取运行结果
- `list_runs() -> list[dict]` — 列出所有运行结果
- `save_snapshot(snapshot: dict) -> Path` — 保存快照到 `workspace/snapshots/`
- `load_snapshot(version_id: str) -> dict | None` — 读取快照
- `list_snapshots() -> list[dict]` — 列出所有快照
- `save_report(report: dict, content: str) -> Path` — 保存报告到 `workspace/reports/`
- `list_reports() -> list[dict]` — 列出所有报告元数据
- `save_export(export_id: str, data: dict, fmt: str) -> Path` — 保存导出到 `workspace/exports/`

### 5.2 FileRepository

`FileRepository` 实现 `Repository` 接口，使用 `WorkspaceManager` 进行本地文件读写：

- **已实现**：`save_task`, `save_run`, `save_snapshot`, `save_report`
- **部分实现**：`get_all_runs`, `get_run_by_id`（优先读 workspace，fallback 到 mock）
- **待迁移**：Baseline/Rule/Profile 等读取方法（当前 fallback 到 MockRepository）

> **注意**：FileRepository 当前为 **SCAFFOLD 状态**，默认仍使用 MockRepository。

---

## 6. 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `TOPOCHECKER_WORKSPACE` | `workspace` | workspace 根目录路径 |
| `TOPOCHECKER_REPO` | `mock` | 仓库实现：`mock` 或 `file`（未来） |

---

## 7. 迁移计划

### Phase 1（当前）
- [x] 创建 workspace 目录结构
- [x] 创建 WorkspaceManager 文件读写 scaffold
- [x] 创建 FileRepository scaffold（fallback 到 mock）
- [x] 更新 provider.py 预留 FileRepository 分支
- [x] 默认仍使用 MockRepository

### Phase 2（未来）
- [ ] 将 mock baselines/rules/profiles 导出为 workspace JSON 文件
- [ ] 实现 FileRepository 完整的读取方法
- [ ] 支持通过 `TOPOCHECKER_REPO=file` 切换实现

### Phase 3（未来）
- [ ] 移除 MockRepository fallback
- [ ] FileRepository 成为默认实现
- [ ] 支持 workspace 备份/恢复/导出

---

## 8. 与数据库方案的对比

| 特性 | 本地文件（当前） | 数据库（不采用） |
|------|-----------------|-----------------|
| 依赖 | 零额外依赖 | SQLite / ORM 库 |
| 可移植性 | 目录整体复制即可 | 需要导出/导入 |
| 版本控制 | JSON 可 diff | 二进制/不可读 |
| 查询能力 | 文件遍历（足够轻量） | SQL 查询 |
| 并发 | 单用户本地工具足够 | 多用户支持 |
| 复杂度 | 低 | 高 |

---

## 9. 禁止事项

- ❌ 禁止引入 `sqlite3`, `psycopg`, `pymysql`, `sqlalchemy`, `peewee`, `tortoise`
- ❌ 禁止引入 `mongodb`, `pymongo`
- ❌ 禁止引入任何 ORM 框架
- ❌ 禁止在 FileRepository 中写 SQL
- ❌ 禁止修改 API response 结构
- ❌ 禁止切换默认 repository 为 FileRepository（直到完全实现）
