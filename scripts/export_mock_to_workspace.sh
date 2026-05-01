#!/usr/bin/env bash
# ============================================================
# export_mock_to_workspace.sh
# TopoChecker — Export mock data to workspace JSON fixtures
# Usage: bash scripts/export_mock_to_workspace.sh
# ============================================================
set -euo pipefail

CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$CURRENT_DIR/.." && pwd)"

echo "══════════════════════════════════════════════════════"
echo "  TopoChecker Mock Data -> Workspace Fixture Export"
echo "══════════════════════════════════════════════════════"
echo ""

# Check Python is available
if ! command -v python3 &>/dev/null; then
  echo "Error: python3 not found"
  exit 1
fi

# Run the export script directly from project root
# The script handles its own module loading via importlib
cd "$PROJECT_ROOT"
python3 backend/scripts/export_mock_to_workspace.py

echo ""
echo "══════════════════════════════════════════════════════"
echo "  Export complete. Workspace fixtures ready."
echo "══════════════════════════════════════════════════════"
