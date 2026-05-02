# backend/recognition/__init__.py
# Device recognition module for header-based table identification.
# No database, no AI/LLM.

from .models import (
    RecognizedTableKind,
    RecognizedField,
    RecognizedTable,
    DatasetRecognitionSummary,
)
from .recognizer import DatasetRecognizer

__all__ = [
    "RecognizedTableKind",
    "RecognizedField",
    "RecognizedTable",
    "DatasetRecognitionSummary",
    "DatasetRecognizer",
]
