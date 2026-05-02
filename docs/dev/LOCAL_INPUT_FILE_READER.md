# Local Input File Reader Scaffold

> **Status:** SCAFFOLD PHASE — LocalInputReader scaffold ready
> **Scope:** Read local Excel/CSV files, no real check engine integration
> **Last updated:** 2026-05-02

---

## 1. 概述

### 1.1 目的

`backend/input/` 模块提供本地输入文件读取的 scaffold，为后续真实 recognition/check engine 做准备。

### 1.2 当前状态

| 组件 | 状态 | 说明 |
|------|------|------|
| `LocalInputReader` | ✅ Scaffold | 读取 .xlsx/.xls/.csv 文件 |
| `InputFileMetadata` | ✅ 已定义 | 输入文件元数据 |
| `RawTabularDataset` | ✅ 已定义 | 原始表格数据 |
| `NormalizedDataset` | ✅ Scaffold | 标准化中间表示 |
| `normalize_raw_dataset()` | ✅ Scaffold | 最小标准化转换 |

### 1.3 限制

- ❌ **不执行真实规则检查** — scaffold only
- ❌ **不生成 issue** — 无业务逻辑
- ❌ **不接数据库** — 无 SQLite/ORM
- ❌ **不引入 AI/LLM** — 基于规则
- ❌ **不自动读取真实文件** — 仅按需调用

---

## 2. 模块结构

```
backend/input/
├── __init__.py          # 模块导出
├── models.py            # Pydantic 模型
├── reader.py            # LocalInputReader 类
└── normalizer.py        # normalize_raw_dataset()
```

---

## 3. 模型定义

### 3.1 InputFileMetadata

```python
class InputFileMetadata(BaseModel):
    file_path: str
    file_name: str
    file_size: int
    file_type: str  # xlsx, xls, csv
    sheet_count: int
    read_at: datetime
```

### 3.2 RawSheetData

```python
class RawSheetData(BaseModel):
    sheet_name: str
    headers: list[str]
    rows: list[list[str]]
    row_count: int
    column_count: int
```

### 3.3 RawTabularDataset

```python
class RawTabularDataset(BaseModel):
    metadata: InputFileMetadata
    sheets: list[RawSheetData]
    source_file: str
```

### 3.4 NormalizedDataset

```python
class NormalizedDataset(BaseModel):
    dataset_id: str
    source_file: str
    normalized_at: datetime
    sheet_count: int
    total_row_count: int
    tables: list[dict]  # 中间表示
```

---

## 4. 使用方式

### 4.1 读取文件

```python
from backend.input import LocalInputReader, normalize_raw_dataset

reader = LocalInputReader()
raw = reader.read_file("workspace/inputs/devices.xlsx")
normalized = normalize_raw_dataset(raw)
```

### 4.2 支持格式

| 格式 | 扩展名 | 读取方式 |
|------|--------|----------|
| Excel | .xlsx | openpyxl |
| Excel (旧) | .xls | openpyxl |
| CSV | .csv | csv 模块 |

---

## 5. 与 Engine 的关系

### 5.1 数据流

```
本地 Excel/CSV 文件
    │
    ▼
LocalInputReader.read_file()
    │ RawTabularDataset
    ▼
normalize_raw_dataset()
    │ NormalizedDataset (中间表示)
    ▼
RealEngineAdapter (未来)
    │ 应用业务规则
    ▼
CheckResultBundle
```

### 5.2 当前阶段

- RealEngineAdapter 尚未实现真实方法
- LocalInputReader 仅返回 raw/normalized 数据
- 后续会接入 RealEngineAdapter.start_recognition()

---

## 6. Workspace 集成

### 6.1 文件保存

读取后的数据可以保存到 workspace：

```
workspace/
├── inputs/           # 原始输入文件
├── snapshots/        # normalized datasets (未来)
└── ...
```

### 6.2 不改变 API Response

- LocalInputReader 不在 API 路由中自动调用
- 不影响现有 API contract
- 后续通过 RealEngineAdapter 接入

---

## 7. 禁止事项

- ❌ **不执行真实规则检查**
- ❌ **不生成 IssueItem**
- ❌ **不接数据库 / SQLite / ORM**
- ❌ **不引入 AI / LLM**
- ❌ **不自动在 API 默认路径读取真实文件**
- ❌ **不改变现有 API response**

---

## 8. 下一步建议

1. **实现 RealEngineAdapter.recognition**
   - 调用 LocalInputReader 读取文件
   - 生成 RecognitionResult

2. **实现设备类型识别**
   - 基于列名/值识别设备类型
   - 生成 normalized dataset

3. **实现规则检查**
   - 基于 baseline rules 检查
   - 生成 CheckResultBundle

4. **集成到服务层**
   - ExecutionService 调用 RealEngineAdapter
   - 保存结果到 workspace/runs/
