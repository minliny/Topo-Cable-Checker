# Real Engine Recognition Scaffold

> **Status:** SCAFFOLD PHASE — Recognition scaffold ready for local file reading
> **Scope:** Read local Excel/CSV, no real rule checking, no IssueItem generation
> **Last updated:** 2026-05-02

---

## 1. 概述

### 1.1 目的

本模块实现 RealEngineAdapter 的 recognition scaffold，用于从本地 Excel/CSV 文件读取数据并生成 RecognitionResult。

### 1.2 当前状态

| 方法 | 状态 | 说明 |
|------|------|------|
| `get_recognition_status()` | ✅ 实现 | 返回 "ready" |
| `start_recognition()` | ✅ 实现 | 读取文件 → normalize → 保存 snapshot |
| `get_recognition_result()` | ✅ 实现 | 从 snapshot 返回 RecognitionResult |
| `confirm_recognition()` | ✅ 实现 | 标记确认为 confirmed |
| `start_check()` | ❌ Scaffold | NotImplementedError |
| 其他方法 | ❌ Scaffold | NotImplementedError |

### 1.3 限制

- ❌ **不执行真实规则检查**
- ❌ **不生成 IssueItem**
- ❌ **不接数据库 / SQLite / ORM**
- ❌ **不引入 AI / LLM**

---

## 2. 数据流

```
workspace/inputs/sample_topology.csv
           │
           ▼
LocalInputReader.read_file()
           │ RawTabularDataset
           ▼
normalize_raw_dataset()
           │ NormalizedDataset
           ▼
WorkspaceManager (save to snapshots/recognition/)
           │
           ▼
RecognitionResult
```

---

## 3. 使用方式

### 3.1 环境变量

```bash
# 激活 RealEngineAdapter (仅开发测试)
export TOPOCHECKER_ENGINE=real

# 启动后端
bash scripts/dev_start_backend.sh
```

### 3.2 API 调用

```bash
# 1. 启动 recognition
curl -X POST http://127.0.0.1:8000/recognition/start \
  -H "Content-Type: application/json" \
  -d '{"data_source_id": "sample", "scope_id": "scope-full"}'

# 2. 获取 recognition result
curl http://127.0.0.1:8000/recognition/status/{recognition_id}

# 3. 确认 recognition
curl -X POST http://127.0.0.1:8000/recognition/confirm/{recognition_id}
```

### 3.3 示例输入文件

`workspace/inputs/sample_topology.csv`:

```csv
DeviceID,DeviceType,DeviceName,Location,Floor,Rack,ManagementIP,Status
DEV-001,Switch,Core-SW-01,Floor-1-Bldg-A,R1,10.0.1.1,Active
DEV-002,Switch,Core-SW-02,Floor-1-Bldg-A,R2,10.0.1.2,Active
...
```

---

## 4. Workspace 保存位置

Recognition 结果保存在：

```
workspace/snapshots/recognition/{recognition_id}.json
```

示例内容：

```json
{
  "recognition_id": "rec-a1b2c3d4",
  "data_source_id": "sample",
  "scope_id": "scope-full",
  "status": "confirmed",
  "source_file": "workspace/inputs/sample_topology.csv",
  "dataset_id": "uuid-here",
  "normalized_at": "2026-05-02T10:00:00",
  "sheet_count": 1,
  "total_row_count": 8,
  "tables": [...]
}
```

---

## 5. 默认 Engine

**默认仍是 MockEngineAdapter**。使用 RealEngineAdapter 必须设置 `TOPOCHECKER_ENGINE=real`。

| 环境变量 | Engine | 用途 |
|----------|--------|------|
| `TOPOCHECKER_ENGINE` | `mock` (默认) | 开发/测试/生产 |
| `TOPOCHECKER_ENGINE` | `real` | 手动验证 recognition |

---

## 6. 禁止事项

- ❌ **不使用 TOPOCHECKER_ENGINE=real 生产**
- ❌ **不执行真实规则检查**
- ❌ **不生成 IssueItem**
- ❌ **不接数据库**
- ❌ **不引入 AI/LLM**

---

## 7. 下一步建议

1. **实现 start_check() 方法**
   - 基于 normalized dataset 执行规则检查
   - 生成 CheckResultBundle

2. **实现设备类型识别**
   - 基于列名/值识别设备类型
   - 验证连接关系

3. **实现 get_recheck_diff() 方法**
   - 对比两个 run 的 CheckResultBundle
   - 生成 RecheckDiffSnapshot
