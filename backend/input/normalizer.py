# backend/input/normalizer.py
# Dataset normalizer scaffold.
# WARNING: This is a scaffold only. No real business rules applied.
# No database, no AI/LLM, no external API.

import uuid
from datetime import datetime

from .models import RawTabularDataset, NormalizedDataset


def normalize_raw_dataset(raw: RawTabularDataset) -> NormalizedDataset:
    """Normalize a raw tabular dataset to intermediate representation.

    This is a scaffold normalizer. It only:
    - Converts raw sheets to table format
    - Extracts metadata
    - Assigns a dataset ID

    It does NOT:
    - Apply business rules
    - Generate issues
    - Validate device types
    - Validate cable connections
    - Connect to database

    Args:
        raw: RawTabularDataset from LocalInputReader.

    Returns:
        NormalizedDataset - intermediate representation.
    """
    tables = []

    for sheet in raw.sheets:
        tables.append({
            "name": sheet.sheet_name,
            "headers": sheet.headers,
            "rows": sheet.rows,
        })

    total_rows = sum(sheet.row_count for sheet in raw.sheets)

    return NormalizedDataset(
        dataset_id=str(uuid.uuid4()),
        source_file=raw.source_file,
        normalized_at=datetime.now(),
        sheet_count=len(raw.sheets),
        total_row_count=total_rows,
        tables=tables,
    )
