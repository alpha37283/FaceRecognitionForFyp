#!/bin/bash
# Run Sync API Server (for Live Feed Devices)
# This is a separate API server from the enrollment API

cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "myenv" ]; then
    source myenv/bin/activate
fi

# Set PostgreSQL password
export POSTGRES_PASSWORD=alpha

# Set default port for sync API (different from enrollment API)
SYNC_API_PORT=${SYNC_API_PORT:-8001}

echo "=========================================="
echo "  Starting Sync API Server"
echo "  Port: $SYNC_API_PORT"
echo "  Purpose: Live Feed Device Synchronization"
echo "=========================================="
echo ""

# Run the sync API
uvicorn backend.sync_api:sync_app --host 0.0.0.0 --port $SYNC_API_PORT --reload

