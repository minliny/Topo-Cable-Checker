# backend/recognition/__init__.py
# Device recognition module for header-based table identification.
# No database, no AI/LLM.

from .models import (
    RecognizedTableKind,
    RecognizedField,
    RecognizedTable,
    DatasetRecognitionSummary,
    DeviceType,
    InferredDeviceType,
    DeviceTypeSummary,
)
from .recognizer import DatasetRecognizer
from .type_inference import (
    infer_device_type,
    infer_device_types_in_table,
    summarize_device_types,
    infer_and_summarize_tables,
)

__all__ = [
    "RecognizedTableKind",
    "RecognizedField",
    "RecognizedTable",
    "DatasetRecognitionSummary",
    "DeviceType",
    "InferredDeviceType",
    "DeviceTypeSummary",
    "DatasetRecognizer",
    "infer_device_type",
    "infer_device_types_in_table",
    "summarize_device_types",
    "infer_and_summarize_tables",
]
