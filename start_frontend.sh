#!/bin/bash
set -e

echo "=============================================="
echo " Starting Rule Editor Frontend Server "
echo "=============================================="

# Ensure we are in the frontend directory
cd frontend

echo "[1/3] Installing dependencies..."
npm install

echo "[2/3] Setting VITE_USE_MOCK_API=false for real backend integration..."
# Creating/overwriting .env file
echo "VITE_USE_MOCK_API=false" > .env
echo "VITE_API_BASE_URL=http://localhost:8000/api" >> .env

echo "[3/3] Starting Vite development server on port 5173..."
npm run dev -- --host 0.0.0.0
