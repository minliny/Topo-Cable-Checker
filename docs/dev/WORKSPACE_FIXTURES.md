# Workspace Fixtures

> **Status:** PHASE 2 — Mock data exported to workspace JSON fixtures  
> **Scope:** Local file persistence only — no database, no SQLite, no ORM.  
> **Last updated:** 2026-05-01

---

## 1. 概述

Workspace fixtures 是将 `backend/data/mock_data.py` 中的 mock 数据导出为 `workspace/` 目录下 JSON 文件的过程。这是从 MockRepository 迁移到 FileRepository 的中间步骤。

---

## 2. 如何导出 Mock 到 Workspace

### 2.1 运行导出脚本

```bash
bash scripts/export_mock_to_workspace.sh
```

或直接使用 Python：

```bash
python3 scripts/export_mock_to_workspace.py
```

### 2.2 导出结果

脚本会将以下数据导出到 `workspace/` 目录：

| 数据类型 | 目标目录 | 文件格式 |
|----------|----------|----------|
| Baselines | `workspace/inputs/` | `baseline_{id}.json` |
| Rulesets | `workspace/inputs/` | `rulesets.json` |
| Rules | `workspace/inputs/` | `rules.json` |
| Parameter Profiles | `workspace/inputs/` | `parameter_profiles.json` |
| Threshold Profiles | `workspace/inputs/` | `threshold_profiles.json` |
| Scope Selectors | `workspace/inputs/` | `scope_selectors.json` |
| Data Sources | `workspace/inputs/` | `data_sources.json` |
| Execution Scopes | `workspace/inputs/` | `execution_scopes.json` |
| Baseline Profile Map | `workspace/inputs/` | `baseline_profile_map.json` |
| Baseline Version Snapshots | `workspace/inputs/` | `baseline_version_snapshots.json` |
| Tasks | `workspace/tasks/` | `{task_id}.json` |
| Runs | `workspace/runs/` | `{run_id}.json` |
| Bundles | `workspace/inputs/` | `bundles.json` |
| Version Snapshots | `workspace/snapshots/` | `{version_id}.json` |
| Version Diffs | `workspace/inputs/` | `version_diffs.json` |
| Recheck Diffs | `workspace/inputs/` | `recheck_diffs.json` |
| Reports | `workspace/reports/` | `{report_id}.html` + `.json` |
| Exports | `workspace/exports/` | `{export_id}.json` |

---

## 3. Workspace JSON 文件结构

### 3.1 列表型数据（`workspace/inputs/*.json`）

例如 `rulesets.json`：

```json
[
  {
    "ruleset_id": "rs-001",
    "name": "Duplicate Entity Rules",
    "description": "Rules for detecting duplicate entities",
    "rule_ids": ["rule-001", "rule-002"]
  }
]
```

### 3.2 字典型数据（`workspace/inputs/*.json`）

例如 `baseline_profile_map.json`：

```json
{
  "baseline-001": {
    "parameter_profile_id": "pp-001",
    "threshold_profile_id": "tp-001",
    "scope_selector_id": "sc-001",
    "ruleset_ids": ["rs-001", "rs-002", "rs-003", "rs-004"]
  }
}
```

### 3.3 单体型数据（`workspace/tasks/`, `workspace/runs/`）

例如 `workspace/runs/run-001.json`：

```json
{
  "run_id": "run-001",
  "baseline_id": "baseline-001",
  "baseline_name": "Production Baseline v1",
  "scenario_id": "scenario-001",
  "status": "completed",
  "severity_summary": {
    "critical": 0,
    "high": 2,
    "medium": 5,
    "low": 3,
    "info": 0
  },
  "device_count": 150,
  "issue_count": 10,
  "data_source_id": "ds-001",
  "scope_id": "scope-full",
  "bundle_id": "bundle-001"
}
```

---

## 4. FileRepository 当前状态

### 4.1 读取策略

FileRepository 实现以下读取优先级：

1. **优先读取 workspace JSON 文件** — 如果 `workspace/inputs/` 或 `workspace/tasks/` 等目录中存在对应的 JSON 文件，直接读取
2. **Fallback 到 MockRepository** — 如果 workspace 文件不存在，返回 mock 数据

### 4.2 当前仍是可选

- **默认 repository**：仍是 `MockRepository`
- **FileRepository**：可通过 `TOPOCHECKER_REPO=file` 环境变量激活
- **不建议生产使用**：FileRepository 仍在完善中

---

## 5. 如何切换到 FileRepository

### 5.1 当前方式（开发测试）

```bash
# 1. 导出 mock 数据到 workspace
bash scripts/export_mock_to_workspace.sh

# 2. 设置环境变量
export TOPOCHECKER_REPO=file

# 3. 启动后端
bash scripts/dev_start_backend.sh
```

### 5.2 验证 FileRepository 是否生效

```bash
# 检查 baseline 列表是否来自 workspace
curl http://localhost:8000/api/baselines
```

### 5.3 切回 MockRepository

```bash
unset TOPOCHECKER_REPO
# 或
export TOPOCHECKER_REPO=mock
```

---

## 6. 后续计划

### Phase 2（当前）
- [x] 导出 mock 数据到 workspace JSON fixtures
- [x] FileRepository 优先读取 workspace，fallback 到 mock
- [x] 默认仍为 MockRepository

### Phase 3（未来）
- [ ] 移除 FileRepository 中的 MockRepository fallback
- [ ] FileRepository 成为默认实现
- [ ] 支持直接编辑 workspace JSON 文件并实时生效

### Phase 4（未来）
- [ ] 支持 workspace 备份/恢复/导出
- [ ] 支持从真实检查引擎输出写入 workspace

---

## 7. 禁止事项

- ❌ 禁止引入 `sqlite3`, `psycopg`, `pymysql`, `sqlalchemy`, `peewee`, `tortoise`
- ❌ 禁止引入 `mongodb`, `pymongo`
- ❌ 禁止引入任何 ORM 框架
- ❌ 禁止在 FileRepository 中写 SQL
- ❌ 禁止修改 API response 结构
- ❌ 禁止切换默认 repository 为 FileRepository（直到完全实现）
