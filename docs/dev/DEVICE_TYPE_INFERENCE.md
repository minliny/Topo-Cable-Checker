# Device Type Inference Scaffold

> **Status:** SCAFFOLD PHASE — Header-based device type inference ready
> **Scope:** Infers device types from field values, no real business rules
> **Last updated:** 2026-05-02

---

## 1. 概述

### 1.1 目的

`backend/recognition/type_inference.py` 模块实现设备类型推断，基于字段值（设备名称、型号、类型等）推断设备类型。

### 1.2 当前状态

| 组件 | 状态 | 说明 |
|------|------|------|
| `DeviceType` | ✅ 已定义 | switch / router / firewall / server 等 |
| `InferredDeviceType` | ✅ 已定义 | 单行推断结果 |
| `DeviceTypeSummary` | ✅ 已定义 | 类型统计摘要 |
| `infer_device_type()` | ✅ 已实现 | 从字段值推断类型 |
| `infer_and_summarize_tables()` | ✅ 已实现 | 批量推断并统计 |

### 1.3 限制

- ❌ **不执行真实业务规则检查**
- ❌ **不生成 IssueItem**
- ❌ **不接数据库 / SQLite / ORM**
- ❌ **不引入 AI / LLM**

---

## 2. 支持的设备类型

| 类型 | 说明 | 推断规则 |
|------|------|----------|
| `switch` | 交换机 | device_type=switch 或名称含 CE/XH/switch |
| `router` | 路由器 | device_type=router 或名称含 router/RT |
| `firewall` | 防火墙 | device_type=firewall 或名称含 firewall/FW |
| `server` | 服务器 | device_type=server 或名称含 server/PowerEdge |
| `ai_network` | AI 网络设备 | 名称含 LINGQU/灵衢/LQ_L2 |
| `optical_resource` | 光链路资源 | 名称含 optical/光资源/链路光 |
| `network_resource` | 网络资源模块 | 名称含 network_resource/网络资源 |
| `unknown` | 未知 | 无法匹配任何规则 |

---

## 3. 推断规则

### 3.1 优先级规则

推断规则按优先级排序，高优先级规则优先匹配：

```python
# 优先级 (priority) 从高到低:
100: AI Network (LINGQU/灵衢/LQ_L2)
90:  Optical Resource (光资源模块)
80:  Network Resource (网络资源模块)
70:  Switch (CE/XH/switch)
60:  Router
50:  Firewall
40:  Server
```

### 3.2 规则匹配逻辑

1. **device_type 字段直读** (最高置信度 0.95)
   - 优先检查 device_type 字段
   - 直接匹配枚举值

2. **名称/型号关键词匹配** (置信度基于优先级)
   - 搜索 device_name + model + role 组合值
   - 使用子串匹配

### 3.3 关键规则

| 规则 | 类型 | 说明 |
|------|------|------|
| CE 开头 | switch | 如 Catalyst9300-CE |
| XH 开头 | switch | 如 S5735-XH |
| LINGQU/灵衢/LQ_L2 | ai_network | AI 网络交换机 |
| 光资源/Optical | optical_resource | 光链路模块 |
| 网络资源/Network | network_resource | 网络资源模块 |
| Router/RT | router | 路由器 |
| Firewall/FW | firewall | 防火墙 |
| Server/PowerEdge | server | 服务器 |

---

## 4. 使用方式

### 4.1 基本使用

```python
from backend.recognition import (
    infer_device_type,
    infer_device_types_in_table,
    infer_and_summarize_tables,
)

# 单行推断
inferred = infer_device_type(
    device_name="Core-SW-01",
    model="Catalyst9300-CE",
)
print(f"Type: {inferred.device_type}, Confidence: {inferred.confidence}")

# 批量推断并统计
summary = infer_and_summarize_tables(recognition_summary)
for st in summary.device_type_summaries:
    print(f"{st.device_type}: {st.count}")
```

### 4.2 在 RealEngineAdapter 中集成

`RealEngineAdapter.start_recognition()` 自动调用设备类型推断：

```python
from backend.recognition import (
    DatasetRecognizer,
    infer_and_summarize_tables,
)

# Recognize tables
recognition_summary = self.recognizer.recognize(normalized)

# Infer device types
recognition_summary = infer_and_summarize_tables(recognition_summary)

# Save to workspace
recognition_data["recognition_summary"] = recognition_summary.model_dump(mode="json")
```

---

## 5. 数据模型

### 5.1 DeviceType

```python
class DeviceType(str, Enum):
    SWITCH = "switch"
    ROUTER = "router"
    FIREWALL = "firewall"
    SERVER = "server"
    OPTICAL_RESOURCE = "optical_resource"
    NETWORK_RESOURCE = "network_resource"
    AI_NETWORK = "ai_network"
    UNKNOWN = "unknown"
```

### 5.2 InferredDeviceType

```python
class InferredDeviceType(BaseModel):
    device_type: DeviceType
    confidence: float  # 0.0-1.0
    evidence_fields: list[str]  # 贡献字段
    raw_value: Optional[str]  # 原始值
```

### 5.3 DeviceTypeSummary

```python
class DeviceTypeSummary(BaseModel):
    device_type: DeviceType
    count: int
    confidence: float  # 平均置信度
    evidence_fields: list[str]  # 贡献的证据字段
```

---

## 6. 示例输入

`workspace/inputs/sample_topology.csv` 包含以下设备类型示例：

```csv
DeviceID,DeviceName,DeviceType,...,Model
DEV-001,Core-SW-01,switch,...,Catalyst9300-CE    # CE 开头 → switch
DEV-004,Access-SW-01,switch,...,S5735-XH         # XH 开头 → switch
DEV-009,LINGQU-EDGE-01,ai_network,...,LQ_L2-SWITCH # LINGQU → ai_network
DEV-010,灵衢-CORE-01,ai_network,...,LQ_L3-CORE     # 灵衢 → ai_network
DEV-011,NET-RES-MOD-01,network_resource,...,Network-Module
DEV-012,OPT-LINK-MOD-01,optical_resource,...,Optical-Link-Module
```

---

## 7. Workspace 保存

设备类型推断结果保存在 `recognition_summary.device_type_summaries` 中：

```json
{
  "device_type_summaries": [
    {"device_type": "switch", "count": 4, "confidence": 0.85, "evidence_fields": [...]},
    {"device_type": "ai_network", "count": 2, "confidence": 0.90, "evidence_fields": [...]},
    {"device_type": "server", "count": 2, "confidence": 0.95, "evidence_fields": [...]},
    ...
  ]
}
```

---

## 8. 下一步建议

1. **扩展规则**
   - 添加更多设备型号关键词
   - 支持中文设备类型名称

2. **添加设备子类型**
   - 核心交换机 / 接入交换机 / 汇聚交换机
   - 边界路由器 / 核心路由器

3. **添加配置验证**
   - 检测设备型号与端口配置是否匹配
   - 生成警告信息

4. **集成到规则检查**
   - 基于设备类型应用不同规则
   - 生成 CheckResultBundle
