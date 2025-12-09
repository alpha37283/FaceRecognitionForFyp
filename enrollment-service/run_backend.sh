#!/bin/bash
# Run Enrollment API Server (for Static Image Upload)
# This is the main API for enrollment side - separate from sync API

# Backend API Server Startup Script

echo "=========================================="
echo "  🚀 Starting Backend API Server"
echo "=========================================="
echo ""

cd "$(dirname "$0")"
# Activate virtual environment (adjust path if needed)
if [ -d "../myenv" ]; then
    source ../myenv/bin/activate
elif [ -d "myenv" ]; then
    source myenv/bin/activate
fi

# Check if uvicorn is installed
if ! python -c "import uvicorn" 2>/dev/null; then
    echo "[-] uvicorn not found. Installing dependencies..."
    pip install -q fastapi uvicorn sqlalchemy pydantic requests
fi

# Check if psycopg2 is installed (required for PostgreSQL)
if ! python -c "import psycopg2" 2>/dev/null; then
    echo "[INFO] Installing PostgreSQL driver (psycopg2)..."
    pip install -q psycopg2-binary
fi

echo "[INFO] Starting API server on http://localhost:8000"
echo "[INFO] API docs available at http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="
echo ""

cd "$(dirname "$0")"
uvicorn backend.api:app --host 0.0.0.0 --port 8000 --reload

