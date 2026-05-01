# backend/engine/__init__.py
from .interface import EngineAdapter
from .mock_engine import MockEngineAdapter

__all__ = ["EngineAdapter", "MockEngineAdapter"]
