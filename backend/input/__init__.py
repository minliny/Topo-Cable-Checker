# backend/input/__init__.py
# Local input file reader module.
# Scaffold for reading Excel/CSV files.
# No database, no AI/LLM.

from .models import (
    InputFileMetadata,
    RawSheetData,
    RawTabularDataset,
    NormalizedDataset,
)
from .reader import LocalInputReader
from .normalizer import normalize_raw_dataset

__all__ = [
    "InputFileMetadata",
    "RawSheetData",
    "RawTabularDataset",
    "NormalizedDataset",
    "LocalInputReader",
    "normalize_raw_dataset",
]
