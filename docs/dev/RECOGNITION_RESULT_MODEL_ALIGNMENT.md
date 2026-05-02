# RECOGNITION_RESULT_MODEL_ALIGNMENT

## 概述

本文档定义了 recognition 产物的模型边界划分：
- **API RecognitionResult**：前端执行确认所需的稳定摘要字段
- **Workspace Snapshot**：完整的识别结果，包括内部推断数据

## API RecognitionResult（前端使用）

**文件位置**：`backend/models/execution.py`

```python
class RecognitionResult(BaseModel):
    recognized_device_count: int      # 识别的设备数量
    unmatched_device_count: int        # 未匹配的设备数量
    out_of_scope_device_count: int     # 范围外的设备数量
    warnings: list[str] = []           # 警告信息
```

**前端契约**（`frontend/src/api/contracts.ts`）：
```typescript
export interface RecognitionResult {
  recognized_device_count: number;
  unmatched_device_count: number;
  out_of_scope_device_count: number;
  warnings: string[];
}
```

### API 边界原则

1. **仅暴露执行确认所需字段**
   - `recognized_device_count`：前端需要知道有多少设备将参与检查
   - `unmatched_device_count`/`out_of_scope_device_count`：用于显示警告
   - `warnings`：显示识别过程中的问题

2. **不暴露的内容**
   - 完整的 raw dataset / rows
   - `recognition_summary` 结构
   - `inferred_device_types` 详情
   - 内部识别逻辑细节

3. **前端不做识别推断**
   - 前端仅消费 API 返回的摘要
   - 所有识别逻辑由后端/engine 负责
   - 前端不解析 raw data 或 header

## Workspace Recognition Snapshot

**文件位置**：`workspace/snapshots/recognition/{recognition_id}.json`

### 完整字段结构

```json
{
  "recognition_id": "rec-xxxx",
  "data_source_id": "ds-001",
  "scope_id": "scope-full",
  "status": "completed|confirmed",
  "source_file": "/path/to/input.csv",
  "dataset_id": "dataset-xxxx",
  "normalized_at": "2026-05-02T10:00:00",
  "sheet_count": 1,
  "total_row_count": 100,
  "tables": [...],                    // 原始归一化表格
  "recognition_summary": {
    "dataset_id": "...",
    "source_file": "...",
    "recognized_at": "...",
    "sheet_count": 1,
    "total_row_count": 100,
    "device_tables": [...],
    "link_tables": [...],
    "unknown_tables": [...],
    "total_device_count": 80,
    "total_link_count": 150,
    "unrecognized_table_count": 0,
    "device_type_summaries": [
      {"device_type": "switch", "count": 50, ...},
      {"device_type": "router", "count": 20, ...},
      {"device_type": "ai_network", "count": 10, ...}
    ],
    "warnings": []
  }
}
```

### Snapshot 字段说明

| 字段 | 说明 | API 暴露 |
|------|------|----------|
| `recognition_id` | 识别任务 ID | 否 |
| `data_source_id` | 数据源 ID | 否 |
| `scope_id` | 执行范围 ID | 否 |
| `status` | 识别状态 | 否 |
| `source_file` | 源文件路径 | 否 |
| `dataset_id` | 数据集 ID | 否 |
| `normalized_at` | 归一化时间 | 否 |
| `sheet_count` | Excel sheet 数量 | 否 |
| `total_row_count` | 总行数 | 摘要 |
| `tables` | 原始归一化表格 | 否 |
| `recognition_summary` | 识别摘要 | 否 |
| `recognition_summary.total_device_count` | 设备数量 | API via RecognitionResult |
| `recognition_summary.device_type_summaries` | 设备类型统计 | 否 |
| `recognition_summary.warnings` | 警告 | API via RecognitionResult |

### 核心原则

1. **Snapshot 包含完整信息**
   - 用于审计、回溯、调试
   - 保存原始表格和识别详情
   - 不直接暴露给前端 API

2. **API 仅返回摘要**
   - `get_recognition_result()` 从 snapshot 提取摘要
   - 转换为稳定的 `RecognitionResult` 格式
   - 不暴露内部结构

3. **inferred_device_types 默认只在 snapshot**
   - `device_type_summaries` 存储在 snapshot 中
   - 前端执行确认不需要这些详情
   - 未来可通过专用 API 端点暴露（可选）

## Backend Model 对齐

### DatasetRecognitionSummary（内部使用）

```python
class DatasetRecognitionSummary(BaseModel):
    dataset_id: str
    source_file: str
    recognized_at: datetime
    sheet_count: int
    total_row_count: int

    device_tables: list[RecognizedTable]      # 设备表
    link_tables: list[RecognizedTable]         # 链路表
    unknown_tables: list[RecognizedTable]      # 未知表

    total_device_count: int                    # 总设备数
    total_link_count: int                      # 总链路数
    unrecognized_table_count: int              # 未识别表数

    device_type_summaries: list[DeviceTypeSummary]  # 设备类型推断
    warnings: list[str]                        # 警告
```

### RecognizedTable（内部使用）

```python
class RecognizedTable(BaseModel):
    table_name: str
    table_kind: RecognizedTableKind
    headers: list[str]
    rows: list[list[str]]                      # 原始行数据
    row_count: int
    recognized_fields: list[RecognizedField]
    confidence: float
```

### 转换流程

```
输入文件 (Excel/CSV)
    ↓
LocalInputReader.read_file()
    ↓
normalize_raw_dataset() -> NormalizedDataset
    ↓
DatasetRecognizer.recognize() -> DatasetRecognitionSummary
    ↓
infer_and_summarize_tables() -> DatasetRecognitionSummary (with device_type_summaries)
    ↓
_snapshot = {
    ...metadata,
    "recognition_summary": summary.model_dump()
}
    ↓
WorkspaceManager.save_snapshot(_snapshot)
    ↓
get_recognition_result() -> RecognitionResult (API)
    ↓
前端显示设备数量和警告
```

## 技术约束

1. **不使用数据库**
   - 所有数据存储在 workspace JSON 文件
   - 使用 FileRepository 管理

2. **不使用 AI/LLM**
   - 识别规则基于 header 关键词匹配
   - 设备类型推断基于模式匹配
   - 不使用机器学习或外部 API

3. **前端不做推断**
   - 前端仅展示 API 返回的摘要
   - 不解析原始数据或识别 header
   - 不计算设备类型统计

4. **后端/engine 负责生成**
   - RealEngineAdapter 处理识别逻辑
   - 返回稳定的 API 格式
   - 保存完整 snapshot 到 workspace

## 文件清单

- `backend/models/execution.py` - RecognitionResult 定义
- `backend/recognition/models.py` - 内部识别模型
- `backend/engine/real_engine.py` - RealEngineAdapter 实现
- `backend/engine/mock_engine.py` - MockEngineAdapter 返回
- `workspace/snapshots/recognition/*.json` - 识别 snapshot
- `frontend/src/models/execution.ts` - 前端类型定义
- `frontend/src/api/contracts.ts` - 前端 API 契约