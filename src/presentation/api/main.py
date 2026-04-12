from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.presentation.api.routers import baselines, rules
from src.presentation.api.error_handler import register_error_handlers, RequestIdMiddleware

app = FastAPI(
    title="Rule Editor API", 
    description="JSON API for Rule Editor UI (Three-Column Workbench)",
    version="1.0.0"
)

# P0-6: Request ID tracing middleware (must be added before CORS for proper header passthrough)
app.add_middleware(RequestIdMiddleware)

# Enable CORS for local development (Vite default port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# P0-5: Register unified error handlers
register_error_handlers(app)

app.include_router(baselines.router, prefix="/api/baselines", tags=["Baselines"])
app.include_router(rules.router, prefix="/api/rules", tags=["Rules"])

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Rule Editor API is running"}
