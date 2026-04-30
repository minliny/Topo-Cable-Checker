# backend/main.py
# TopoChecker Backend API Skeleton
# This is a minimal API skeleton that returns mock-compatible data
# NOT connected to real database or check engine

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import (
    baselines_router,
    rules_router,
    versions_router,
    execution_router,
    runs_router,
    diff_router,
)
from .routers.profiles import router as profiles_router

app = FastAPI(
    title="TopoChecker Backend API",
    description="API skeleton for TopoChecker frontend integration",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(baselines_router)
app.include_router(rules_router)
app.include_router(versions_router)
app.include_router(execution_router)
app.include_router(runs_router)
app.include_router(diff_router)
app.include_router(profiles_router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "mode": "mock"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "TopoChecker Backend API",
        "version": "0.1.0",
        "mode": "mock",
        "message": "This is a mock API skeleton. Not connected to real database or check engine.",
    }