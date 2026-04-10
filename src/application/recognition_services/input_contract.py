from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class HeaderMapping:
    standard_name: str
    aliases: List[str]
    required: bool = False
    default_value: Any = None

@dataclass
class SheetConfig:
    sheet_type: str  # e.g., "device", "port", "link"
    keywords: List[str]
    headers: List[HeaderMapping]

@dataclass
class InputContractConfig:
    sheets: List[SheetConfig]

# The default built-in contract
DEFAULT_CONTRACT = InputContractConfig(
    sheets=[
        SheetConfig(
            sheet_type="device",
            keywords=["device", "devices", "设备"],
            headers=[
                HeaderMapping("device_name", ["Device Name", "name", "设备名称"], required=True),
                HeaderMapping("device_type", ["Device Type", "type", "设备类型"], required=False),
                HeaderMapping("status", ["Status", "status", "状态"], required=False),
            ]
        ),
        SheetConfig(
            sheet_type="port",
            keywords=["port", "ports", "端口"],
            headers=[
                HeaderMapping("device_name", ["Device Name", "设备名称"], required=True),
                HeaderMapping("port_name", ["Port Name", "端口名称"], required=True),
                HeaderMapping("port_status", ["Port Status", "端口状态"], required=False),
            ]
        ),
        SheetConfig(
            sheet_type="link",
            keywords=["link", "links", "链路", "连接"],
            headers=[
                HeaderMapping("src_device", ["Source Device", "源设备"], required=True),
                HeaderMapping("src_port", ["Source Port", "源端口"], required=True),
                HeaderMapping("dst_device", ["Dest Device", "目的设备"], required=True),
                HeaderMapping("dst_port", ["Dest Port", "目的端口"], required=True),
            ]
        )
    ]
)

@dataclass
class ExtractedRow:
    original_row: Dict[str, Any]
    mapped_data: Dict[str, Any]
    missing_required: List[str]
    source_row_index: int

@dataclass
class SheetExtractionResult:
    sheet_type: str
    sheet_name: str
    extracted_rows: List[ExtractedRow]
    unmapped_headers: List[str]
    missing_headers: List[str]
