from dataclasses import dataclass
from typing import Optional, List

@dataclass
class DeviceFact:
    device_name: str
    device_type: Optional[str]
    status: Optional[str]
    _source_sheet: str

@dataclass
class PortFact:
    device_name: str
    port_name: str
    port_status: Optional[str]
    _source_sheet: str

@dataclass
class LinkFact:
    src_device: str
    src_port: str
    dst_device: str
    dst_port: str
    _source_sheet: str

@dataclass
class NormalizedDataset:
    devices: List[DeviceFact]
    ports: List[PortFact]
    links: List[LinkFact]
