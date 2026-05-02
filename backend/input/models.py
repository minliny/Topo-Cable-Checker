# backend/input/models.py
# Input file data models for local Excel/CSV reading scaffold.
# No database, no AI/LLM, no external API.

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class InputFileMetadata(BaseModel):
    """Metadata for a read input file."""

    file_path: str
    file_name: str
    file_size: int
    file_type: str  # xlsx, xls, csv
    sheet_count: int
    read_at: datetime = Field(default_factory=datetime.now)


class RawSheetData(BaseModel):
    """Raw data from a single sheet/table."""

    sheet_name: str
    headers: list[str]
    rows: list[list[str]]
    row_count: int
    column_count: int


class RawTabularDataset(BaseModel):
    """Raw tabular dataset from input file (one or more sheets)."""

    metadata: InputFileMetadata
    sheets: list[RawSheetData]
    source_file: str  # original file path


class NormalizedDataset(BaseModel):
    """Normalized dataset scaffold.

    This is an intermediate representation after parsing.
    No real business rules applied yet.
    """

    dataset_id: str
    source_file: str
    normalized_at: datetime = Field(default_factory=datetime.now)
    sheet_count: int
    total_row_count: int
    tables: list[dict] = Field(default_factory=list)
    # tables format: [{"name": str, "headers": list[str], "rows": list[list[str]]}]
