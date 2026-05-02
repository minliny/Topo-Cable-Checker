# backend/recognition/recognizer.py
# Dataset recognizer for header-based table identification.
# WARNING: This is a scaffold only. No real business rules applied.
# No database, no AI/LLM, no external API.

from ..input.models import NormalizedDataset
from .models import (
    RecognizedTableKind,
    RecognizedField,
    RecognizedTable,
    DatasetRecognitionSummary,
)


# Device table keywords (header patterns)
DEVICE_KEYWORDS = {
    "device_id", "deviceid", "device-name", "devicename",
    "device_name", "device-name", "device_name",
    "name", "hostname", "host_name", "host-name",
    "device_type", "device-type", "devicetype", "type",
    "device_role", "device-role", "role",
    "location", "机房", "位置",
    "floor", "平面", "楼层",
    "rack", "机架", "机柜",
    "management_ip", "mgmt_ip", "ip_address", "ip",
    "status", "状态", "设备状态",
    "model", "型号",
    "vendor", "厂商", "manufacturer",
}

# Link table keywords (header patterns)
LINK_KEYWORDS = {
    "src", "source", "起始端", "源端",
    "src_device", "source_device", "起始端设备",
    "src_port", "source_port", "起始端端口",
    "src_interface", "source_interface",
    "dst", "dest", "destination", "目的端", "终端",
    "dst_device", "dest_device", "destination_device", "目的端设备",
    "dst_port", "dest_port", "destination_port", "目的端端口",
    "dst_interface", "dest_interface",
    "port", "端口",
    "interface", "接口",
    "vlan", "vlan_id", "vlanid",
    "link_type", "linktype", "链路类型", "类型",
    "bandwidth", "带宽",
    "speed", "速率",
    "protocol", "协议",
    "cable", "线缆", "光纤",
    "patch", "跳线",
    "from_port", "to_port", "from_interface", "to_interface",
}

# Key fields that indicate identity
DEVICE_KEY_FIELDS = {
    "device_id", "deviceid", "device_name", "devicename",
    "name", "hostname", "host_name",
}

LINK_KEY_FIELDS = {
    "src", "dst", "source", "dest", "destination",
    "src_port", "dst_port", "source_port", "dest_port",
    "src_interface", "dst_interface",
}


class DatasetRecognizer:
    """Recognize device and link tables from normalized dataset.

    Uses header keyword matching only.
    WARNING: This is a scaffold. No real business validation.
    """

    def recognize(self, dataset: NormalizedDataset) -> DatasetRecognitionSummary:
        """Recognize tables in the dataset.

        Args:
            dataset: NormalizedDataset from input normalizer.

        Returns:
            DatasetRecognitionSummary with recognized tables.
        """
        device_tables = []
        link_tables = []
        unknown_tables = []

        for table in dataset.tables:
            recognized = self._recognize_table(table)
            if recognized.table_kind == RecognizedTableKind.DEVICE:
                device_tables.append(recognized)
            elif recognized.table_kind == RecognizedTableKind.LINK:
                link_tables.append(recognized)
            else:
                unknown_tables.append(recognized)

        # Calculate totals
        total_devices = sum(t.row_count for t in device_tables)
        total_links = sum(t.row_count for t in link_tables)

        # Generate warnings for edge cases
        warnings = []
        if not device_tables and not link_tables:
            warnings.append("未识别到设备表或链路表")

        return DatasetRecognitionSummary(
            dataset_id=dataset.dataset_id,
            source_file=dataset.source_file,
            sheet_count=dataset.sheet_count,
            total_row_count=dataset.total_row_count,
            device_tables=device_tables,
            link_tables=link_tables,
            unknown_tables=unknown_tables,
            total_device_count=total_devices,
            total_link_count=total_links,
            unrecognized_table_count=len(unknown_tables),
            warnings=warnings,
        )

    def _recognize_table(self, table: dict) -> RecognizedTable:
        """Recognize a single table by its headers.

        Args:
            table: dict with 'name', 'headers', 'rows'.

        Returns:
            RecognizedTable with detected kind and fields.
        """
        name = table.get("name", "unknown")
        headers = table.get("headers", [])
        rows = table.get("rows", [])

        # Normalize headers for matching
        normalized_headers = [h.lower().strip().replace(" ", "_") for h in headers]

        # Count keyword matches
        device_score = 0
        link_score = 0

        recognized_fields = []
        for header in headers:
            norm = header.lower().strip().replace(" ", "_")
            field = RecognizedField(field_name=header, normalized_name=norm)

            # Check if key field
            if norm in DEVICE_KEY_FIELDS or norm in LINK_KEY_FIELDS:
                field.is_key_field = True

            recognized_fields.append(field)

            # Count matches
            if norm in DEVICE_KEYWORDS:
                device_score += 1
            if norm in LINK_KEYWORDS:
                link_score += 1

        # Determine table kind based on scores
        if device_score > link_score and device_score > 0:
            kind = RecognizedTableKind.DEVICE
            confidence = min(device_score / max(len(headers), 1), 1.0)
        elif link_score > device_score and link_score > 0:
            kind = RecognizedTableKind.LINK
            confidence = min(link_score / max(len(headers), 1), 1.0)
        else:
            kind = RecognizedTableKind.UNKNOWN
            confidence = 0.0

        return RecognizedTable(
            table_name=name,
            table_kind=kind,
            headers=headers,
            row_count=len(rows),
            recognized_fields=recognized_fields,
            confidence=confidence,
        )
