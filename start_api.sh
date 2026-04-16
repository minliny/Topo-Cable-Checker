#!/bin/bash
set -e

echo "=============================================="
echo " Starting Rule Editor API Backend Server "
echo "=============================================="

# 1. Install dependencies if not already installed
echo "[1/3] Checking dependencies..."
pip install -r requirements.txt

# 2. Run minimal regression tests
echo "[2/3] Running API integration tests..."
pytest tests/test_api_integration.py -v

# 3. Start the server
echo "[3/3] Starting FastAPI server on port 8000..."
echo "NOTE: Single-writer mode. Do NOT run multiple API processes/workers pointing at the same data/ directory."
echo "NOTE: Do NOT run CLI commands that write data/ while the API is serving the same data/ directory."
python3 -m uvicorn src.presentation.api.main:app --host 0.0.0.0 --port 8000 --reload --workers 1
