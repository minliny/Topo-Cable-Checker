# Device Recognition Rules Scaffold

> **Status:** SCAFFOLD PHASE — Header-based table recognition ready
> **Scope:** Recognizes device/link tables by header keywords, no real business rules
> **Last updated:** 2026-05-02

---

## 1. 概述

### 1.1 目的

`backend/recognition/` 模块实现设备表/链路表的识别规则，基于表头关键词做候选识别。

### 1.2 当前状态

| 组件 | 状态 | 说明 |
|------|------|------|
| `RecognizedTableKind` | ✅ 已定义 | device / link / unknown |
| `RecognizedTable` | ✅ 已定义 | 识别后的表结构 |
| `DatasetRecognitionSummary` | ✅ 已定义 | 识别摘要 |
| `DatasetRecognizer` | ✅ 已实现 | 基于 header 关键词识别 |

### 1.3 限制

- ❌ **不执行真实业务规则检查**
- ❌ **不生成 IssueItem**
- ❌ **不接数据库 / SQLite / ORM**
- ❌ **不引入 AI / LLM**
- ❌ **不做最终业务校验** — 仅候选识别

---

## 2. 识别规则

### 2.1 设备表关键词

| 关键词 | 说明 |
|--------|------|
| `device_id`, `deviceid`, `device_name` | 设备标识 |
| `device_type`, `devicetype`, `type` | 设备类型 |
| `device_name`, `hostname`, `name` | 设备名称 |
| `location`, `机房`, `位置` | 位置信息 |
| `floor`, `平面`, `楼层` | 楼层平面 |
| `rack`, `机架`, `机柜` | 机架信息 |
| `management_ip`, `mgmt_ip`, `ip` | 管理 IP |
| `status`, `状态`, `设备状态` | 设备状态 |

### 2.2 链路表关键词

| 关键词 | 说明 |
|--------|------|
| `src`, `source`, `起始端`, `源端` | 起始端标识 |
| `src_device`, `source_device` | 起始端设备 |
| `src_port`, `source_port`, `起始端端口` | 起始端端口 |
| `dst`, `dest`, `destination`, `目的端` | 目的端标识 |
| `dst_device`, `destination_device` | 目的端设备 |
| `dst_port`, `destination_port`, `目的端端口` | 目的端端口 |
| `port`, `端口`, `interface`, `接口` | 端口信息 |
| `vlan`, `vlan_id` | VLAN |
| `link_type`, `链路类型`, `类型` | 链路类型 |

---

## 3. 使用方式

### 3.1 基本使用

```python
from backend.input import LocalInputReader, normalize_raw_dataset
from backend.recognition import DatasetRecognizer

# Read file
reader = LocalInputReader()
raw = reader.read_file("workspace/inputs/sample_topology.csv")

# Normalize
normalized = normalize_raw_dataset(raw)

# Recognize
recognizer = DatasetRecognizer()
summary = recognizer.recognize(normalized)

print(f"Device tables: {len(summary.device_tables)}")
print(f"Link tables: {len(summary.link_tables)}")
print(f"Total devices: {summary.total_device_count}")
```

### 3.2 在 RealEngineAdapter 中集成

`RealEngineAdapter.start_recognition()` 自动调用 `DatasetRecognizer`：

```python
# RealEngineAdapter.__init__
self.recognizer = DatasetRecognizer()

# RealEngineAdapter.start_recognition
normalized = normalize_raw_dataset(raw)
recognition_summary = self.recognizer.recognize(normalized)
# Save to workspace/snapshots/recognition/
```

---

## 4. 数据模型

### 4.1 RecognizedTableKind

```python
class RecognizedTableKind(str, Enum):
    DEVICE = "device"      # Device table
    LINK = "link"          # Link/connection table
    UNKNOWN = "unknown"    # Unknown table
```

### 4.2 RecognizedTable

```python
class RecognizedTable(BaseModel):
    table_name: str
    table_kind: RecognizedTableKind
    headers: list[str]
    row_count: int
    recognized_fields: list[RecognizedField]
    confidence: float  # 0.0-1.0
```

### 4.3 DatasetRecognitionSummary

```python
class DatasetRecognitionSummary(BaseModel):
    dataset_id: str
    source_file: str
    recognized_at: datetime
    sheet_count: int
    total_row_count: int

    device_tables: list[RecognizedTable]
    link_tables: list[RecognizedTable]
    unknown_tables: list[RecognizedTable]

    total_device_count: int
    total_link_count: int
    unrecognized_table_count: int
    warnings: list[str]
```

---

## 5. 识别算法

### 5.1 评分机制

1. 对每个 header 进行归一化（小写、下划线替换空格）
2. 统计匹配 device 关键词和 link 关键词的数量
3. 得分高的关键词类型决定表的类型
4. confidence = 匹配数 / 总 header 数

### 5.2 判定规则

```
if device_score > link_score:
    kind = DEVICE
elif link_score > device_score:
    kind = LINK
else:
    kind = UNKNOWN
```

---

## 6. Workspace 保存位置

识别摘要保存在 recognition snapshot 中：

```
workspace/snapshots/recognition/{recognition_id}.json
```

包含 `recognition_summary` 字段。

---

## 7. 下一步建议

1. **扩展设备类型识别**
   - 基于 DeviceType 字段值识别具体设备类型
   - 交换机、路由器、防火墙、服务器等

2. **扩展链路识别**
   - 基于源/目的端识别链路关系
   - 生成设备连接图

3. **添加更多关键词**
   - 根据实际数据添加更多识别关键词
   - 支持中文和英文混合

4. **添加数据质量检查**
   - 检测空行、重复设备 ID 等
   - 生成警告信息
