# backend/recognition/type_inference.py
# Device type inference based on field values.
# WARNING: This is a scaffold only. No real business rules applied.
# No database, no AI/LLM, no external API.

from collections import defaultdict
from typing import Optional

from ..input.models import NormalizedDataset
from .models import (
    DeviceType,
    InferredDeviceType,
    DeviceTypeSummary,
    RecognizedTable,
    DatasetRecognitionSummary,
)


# Inference rules: patterns mapped to device types
# Higher priority rules come first
TYPE_INFERENCE_RULES = [
    # AI Network: LINGQU / 灵衢 / LQ_L2
    {
        "type": DeviceType.AI_NETWORK,
        "patterns": [
            "lingqu", "灵衢", "lq_l2", "lq_l3",
            "ai_network", "ai-switch", "ai-router",
        ],
        "priority": 100,
        "evidence": "name/model contains LINGQU/灵衢/LQ pattern",
    },

    # Optical Resource: 链路光资源模块
    {
        "type": DeviceType.OPTICAL_RESOURCE,
        "patterns": [
            "光资源", "光模块", "光纤", "optical",
            "optical_resource", "optical-module",
            "链路光", "光链路",
        ],
        "priority": 90,
        "evidence": "name/model contains optical/光 resource pattern",
    },

    # Network Resource: 网络资源模块
    {
        "type": DeviceType.NETWORK_RESOURCE,
        "patterns": [
            "网络资源", "network_resource", "网络模块",
            "network-module", "net-resource",
            "资源模块", "网络设备",
        ],
        "priority": 80,
        "evidence": "name/model contains network resource pattern",
    },

    # Switch: CE / XH prefix or switch keyword
    {
        "type": DeviceType.SWITCH,
        "patterns": [
            "ce", "xh", "s57", "s57h", "s5700", "s5800", "s9300",
            "switch", "sw", "交换机", "接入交换机", "核心交换机",
            "catalyst", "poe-switch",
        ],
        "priority": 70,
        "evidence": "name/model contains CE/XH/switch pattern",
    },

    # Router
    {
        "type": DeviceType.ROUTER,
        "patterns": [
            "router", "rt", "路由器", "边缘路由器",
            "mx", "ar", "ne", "nbr",
        ],
        "priority": 60,
        "evidence": "name/model contains router pattern",
    },

    # Firewall
    {
        "type": DeviceType.FIREWALL,
        "patterns": [
            "firewall", "fw", "防火墙", "下一代防火墙",
            "ngfw", "palo", "fortinet", "hillstone",
        ],
        "priority": 50,
        "evidence": "name/model contains firewall pattern",
    },

    # Server
    {
        "type": DeviceType.SERVER,
        "patterns": [
            "server", "srv", "服务器", "主机",
            "poweredge", "r740", "r640", "dell",
            "blade", "物理机", "虚拟机",
        ],
        "priority": 40,
        "evidence": "name/model contains server pattern",
    },
]


def infer_device_type(
    device_name: Optional[str] = None,
    device_type: Optional[str] = None,
    model: Optional[str] = None,
    role: Optional[str] = None,
) -> InferredDeviceType:
    """Infer device type from field values.

    Args:
        device_name: Device name field value
        device_type: Device type field value
        model: Model/型号 field value
        role: Device role field value

    Returns:
        InferredDeviceType with type, confidence, and evidence.
    """
    # Combine all values to search
    search_values = [
        v.lower().strip() if v else ""
        for v in [device_name, device_type, model, role]
    ]
    combined = " ".join(search_values)

    evidence_fields = []
    matched_type = DeviceType.UNKNOWN
    highest_priority = -1
    confidence = 0.0

    for rule in TYPE_INFERENCE_RULES:
        for pattern in rule["patterns"]:
            pattern_lower = pattern.lower()
            # Check exact match or prefix match
            if pattern_lower in combined:
                if rule["priority"] > highest_priority:
                    highest_priority = rule["priority"]
                    matched_type = rule["type"]
                    evidence_fields = [rule["evidence"]]
                    confidence = min(0.7 + rule["priority"] / 200, 1.0)
                break

    # Direct device_type field mapping (highest confidence)
    if device_type:
        dt_lower = device_type.lower().strip()
        type_mapping = {
            "switch": DeviceType.SWITCH,
            "router": DeviceType.ROUTER,
            "firewall": DeviceType.FIREWALL,
            "server": DeviceType.SERVER,
            "optical_resource": DeviceType.OPTICAL_RESOURCE,
            "network_resource": DeviceType.NETWORK_RESOURCE,
            "ai_network": DeviceType.AI_NETWORK,
            "ai-switch": DeviceType.AI_NETWORK,
        }
        if dt_lower in type_mapping:
            matched_type = type_mapping[dt_lower]
            confidence = 0.95
            evidence_fields = ["device_type field direct match"]

    return InferredDeviceType(
        device_type=matched_type,
        confidence=confidence,
        evidence_fields=evidence_fields,
        raw_value=device_type or device_name or "",
    )


def infer_device_types_in_table(table: RecognizedTable) -> list[InferredDeviceType]:
    """Infer device types for all rows in a device table.

    Args:
        table: RecognizedTable with device rows

    Returns:
        List of InferredDeviceType for each row.
    """
    headers = table.headers
    normalized_headers = [h.lower().strip() for h in headers]

    # Find relevant column indices
    name_idx = _find_column_idx(normalized_headers, ["device_name", "name", "hostname", "device_id"])
    type_idx = _find_column_idx(normalized_headers, ["device_type", "type"])
    model_idx = _find_column_idx(normalized_headers, ["model", "型号", "device_model"])
    role_idx = _find_column_idx(normalized_headers, ["device_role", "role", "device_role"])

    results = []
    for row in table.rows:
        device_name = row[name_idx] if name_idx >= 0 and name_idx < len(row) else None
        device_type = row[type_idx] if type_idx >= 0 and type_idx < len(row) else None
        model = row[model_idx] if model_idx >= 0 and model_idx < len(row) else None
        role = row[role_idx] if role_idx >= 0 and role_idx < len(row) else None

        inferred = infer_device_type(device_name, device_type, model, role)
        results.append(inferred)

    return results


def _find_column_idx(headers: list[str], candidates: list[str]) -> int:
    """Find column index by header name candidates."""
    for candidate in candidates:
        for idx, header in enumerate(headers):
            if candidate in header:
                return idx
    return -1


def summarize_device_types(inferences: list[InferredDeviceType]) -> list[DeviceTypeSummary]:
    """Summarize inferred device types into counts.

    Args:
        inferences: List of InferredDeviceType from table rows

    Returns:
        List of DeviceTypeSummary with counts.
    """
    type_counts: dict[DeviceType, dict] = defaultdict(lambda: {"count": 0, "confidence_sum": 0.0, "evidence": set()})

    for inf in inferences:
        info = type_counts[inf.device_type]
        info["count"] += 1
        info["confidence_sum"] += inf.confidence
        info["evidence"].update(inf.evidence_fields)

    summaries = []
    for dtype, info in type_counts.items():
        count = info["count"]
        avg_confidence = info["confidence_sum"] / count if count > 0 else 0.0
        summaries.append(DeviceTypeSummary(
            device_type=dtype,
            count=count,
            confidence=avg_confidence,
            evidence_fields=list(info["evidence"]),
        ))

    # Sort by count descending
    summaries.sort(key=lambda s: s.count, reverse=True)
    return summaries


def infer_and_summarize_tables(summary: DatasetRecognitionSummary) -> DatasetRecognitionSummary:
    """Infer device types for all device tables and add to summary.

    Args:
        summary: DatasetRecognitionSummary from recognizer

    Returns:
        Updated summary with device_type_summaries populated.
    """
    all_inferences: list[InferredDeviceType] = []

    for table in summary.device_tables:
        inferences = infer_device_types_in_table(table)
        all_inferences.extend(inferences)

    # Summarize
    device_type_summaries = summarize_device_types(all_inferences)

    # Update summary
    summary.device_type_summaries = device_type_summaries

    return summary
