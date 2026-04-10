from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.presentation.api.routers import baselines, rules

app = FastAPI(
    title="Rule Editor API", 
    description="JSON API for Rule Editor UI (Three-Column Workbench)",
    version="1.0.0"
)

# Enable CORS for local development (Vite default port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(baselines.router, prefix="/api/baselines", tags=["Baselines"])
app.include_router(rules.router, prefix="/api/rules", tags=["Rules"])

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Rule Editor API is running"}
