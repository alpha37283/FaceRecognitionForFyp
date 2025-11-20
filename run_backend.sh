#!/bin/bash

# Backend API Server Startup Script

echo "=========================================="
echo "  🚀 Starting Backend API Server"
echo "=========================================="
echo ""

cd /home/alpha/Desktop/FYP/faceSystem
source myenv/bin/activate

# Check if uvicorn is installed
if ! python -c "import uvicorn" 2>/dev/null; then
    echo "[-] uvicorn not found. Installing dependencies..."
    pip install -q fastapi uvicorn sqlalchemy pydantic requests
fi

echo "[INFO] Starting API server on http://localhost:8000"
echo "[INFO] API docs available at http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="
echo ""

uvicorn backend.api:app --host 0.0.0.0 --port 8000 --reload

