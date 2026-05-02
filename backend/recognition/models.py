# backend/recognition/models.py
# Device recognition data models for header-based table identification.
# No database, no AI/LLM, no external API.

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class RecognizedTableKind(str, Enum):
    """Kind of recognized table."""
    DEVICE = "device"      # Device table (switches, routers, servers, etc.)
    LINK = "link"          # Link/connection table (cables, ports, VLANs)
    UNKNOWN = "unknown"    # Unknown or unrecognized table


class RecognizedField(BaseModel):
    """A recognized field in a table."""
    field_name: str                    # Original field name from header
    normalized_name: Optional[str] = None  # Normalized field name if matched
    is_key_field: bool = False         # Whether this is a key/identifier field


class RecognizedTable(BaseModel):
    """A recognized table from the dataset."""
    table_name: str
    table_kind: RecognizedTableKind
    headers: list[str]
    row_count: int
    recognized_fields: list[RecognizedField] = Field(default_factory=list)
    confidence: float = 0.0  # 0.0-1.0, how confident we are about the table kind


class DatasetRecognitionSummary(BaseModel):
    """Summary of dataset recognition results.

    This is an intermediate result. No real business rules applied.
    """
    dataset_id: str
    source_file: str
    recognized_at: datetime = Field(default_factory=datetime.now)
    sheet_count: int
    total_row_count: int

    # Recognized tables
    device_tables: list[RecognizedTable] = Field(default_factory=list)
    link_tables: list[RecognizedTable] = Field(default_factory=list)
    unknown_tables: list[RecognizedTable] = Field(default_factory=list)

    # Device/link count summary
    total_device_count: int = 0
    total_link_count: int = 0
    unrecognized_table_count: int = 0

    # Warnings
    warnings: list[str] = Field(default_factory=list)

    def get_all_tables(self) -> list[RecognizedTable]:
        """Get all recognized tables."""
        return self.device_tables + self.link_tables + self.unknown_tables
