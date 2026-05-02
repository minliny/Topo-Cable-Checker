# backend/engine/provider.py
# Engine provider: returns MockEngineAdapter by default.
# Supports TOPOCHECKER_ENGINE=mock|real environment variable.
# Default is mock. Real engine is scaffold only, NOT for production.

import os
from typing import Optional, Union

from .mock_engine import MockEngineAdapter
from .real_engine import RealEngineAdapter

_engine_cache: Optional[Union[MockEngineAdapter, RealEngineAdapter]] = None


def get_engine() -> Union[MockEngineAdapter, RealEngineAdapter]:
    """Get engine adapter based on TOPOCHECKER_ENGINE env var.

    Default: MockEngineAdapter (safe, returns mock data)
    Optional: TOPOCHECKER_ENGINE=real for RealEngineAdapter (scaffold only)

    RealEngineAdapter is a scaffold. All methods raise NotImplementedError.
    Do NOT use TOPOCHECKER_ENGINE=real in production.
    """
    global _engine_cache

    if _engine_cache is not None:
        return _engine_cache

    engine_mode = os.environ.get("TOPOCHECKER_ENGINE", "mock").lower().strip()

    if engine_mode == "real":
        _engine_cache = RealEngineAdapter()
    else:
        # Default to mock (safe fallback)
        _engine_cache = MockEngineAdapter()

    return _engine_cache


def reset_engine() -> None:
    """Reset engine cache. Used for testing or env var changes."""
    global _engine_cache
    _engine_cache = None
