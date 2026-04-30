# backend/routers/__init__.py
from .baselines import router as baselines_router
from .rules import router as rules_router
from .versions import router as versions_router
from .execution import router as execution_router
from .runs import router as runs_router
from .diff import router as diff_router
from .profiles import router as profiles_router

__all__ = [
    "baselines_router",
    "rules_router",
    "versions_router",
    "execution_router",
    "runs_router",
    "diff_router",
    "profiles_router",
]