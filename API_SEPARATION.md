# API Separation Documentation

## Overview

The system uses **TWO SEPARATE APIs** for different purposes:

1. **Enrollment API** - For static image upload and embedding storage
2. **Sync API** - For live feed devices to fetch embeddings

These are completely separate systems running on different ports.

---

## API 1: Enrollment API (Static Images)

### File: `backend/api.py`
### Port: `8000` (default)
### Purpose: Handle static image uploads and embedding storage

### Endpoints:
- `POST /api/persons/upload-embedding` - Upload embedding from static image
- `GET /api/persons/{person_id}` - Get person information
- `GET /api/persons/{person_id}/embeddings` - Get person's embeddings
- `GET /api/embeddings/{embedding_id}/vector` - Get embedding vector

### Run:
```bash
./run_backend.sh
# or
uvicorn backend.api:app --host 0.0.0.0 --port 8000
```

### Usage:
- Used by enrollment side (main server)
- Receives embeddings from static image processing
- Stores embeddings in PostgreSQL
- Creates sync log entries

---

## API 2: Sync API (Live Feed)

### File: `backend/sync_api.py`
### Port: `8001` (default)
### Purpose: Handle embedding synchronization for live feed devices

### Endpoints:
- `GET /api/sync-embeddings` - Get unsynced embeddings (trigger-based)
- `POST /api/sync-embeddings/mark-synced` - Mark embeddings as synced

### Run:
```bash
./run_sync_api.sh
# or
uvicorn backend.sync_api:sync_app --host 0.0.0.0 --port 8001
```

### Usage:
- Used by live feed devices (Jetson Nano)
- Fetches new embeddings when they're added to database
- Marks embeddings as synced after fetching

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              ENROLLMENT SYSTEM (Main Server)            │
│                                                         │
│  Static Image Upload                                    │
│       ↓                                                 │
│  Generate Embedding                                     │
│       ↓                                                 │
│  Enrollment API (Port 8000)                            │
│  POST /api/persons/upload-embedding                    │
│       ↓                                                 │
│  PostgreSQL Database                                    │
│  - face_embeddings table                                │
│  - embedding_sync_log table (synced="false")           │
└─────────────────────────────────────────────────────────┘
                        │
                        │ (Database)
                        ↓
┌─────────────────────────────────────────────────────────┐
│         SURVEILLANCE SYSTEM (Jetson Nano)              │
│                                                         │
│  Live Camera Feed                                       │
│       ↓                                                 │
│  Sync API Client                                        │
│  GET /api/sync-embeddings (Port 8001)                  │
│       ↓                                                 │
│  Fetch Unsynced Embeddings                              │
│       ↓                                                 │
│  Store Locally                                          │
│       ↓                                                 │
│  POST /api/sync-embeddings/mark-synced                 │
│       ↓                                                 │
│  Face Recognition Comparison                            │
└─────────────────────────────────────────────────────────┘
```

---

## Running Both APIs

### Option 1: Separate Terminals

**Terminal 1 - Enrollment API:**
```bash
./run_backend.sh
# Runs on port 8000
```

**Terminal 2 - Sync API:**
```bash
./run_sync_api.sh
# Runs on port 8001
```

### Option 2: Different Machines

- **Enrollment API**: Run on main server (port 8000)
- **Sync API**: Run on same server OR separate server (port 8001)

---

## Configuration

### Enrollment API
- **File**: `backend/api.py`
- **App Name**: `app`
- **Default Port**: 8000
- **Environment**: Main server

### Sync API
- **File**: `backend/sync_api.py`
- **App Name**: `sync_app`
- **Default Port**: 8001
- **Environment**: Can run on same server or separate server

### Change Ports

**Enrollment API:**
```bash
uvicorn backend.api:app --host 0.0.0.0 --port 8000
```

**Sync API:**
```bash
SYNC_API_PORT=8001 uvicorn backend.sync_api:sync_app --host 0.0.0.0 --port 8001
```

---

## Live Feed Client Configuration

When using the sync client on Jetson Nano, point it to the Sync API:

```python
from modules.recognition.sync_embeddings import EmbeddingSyncClient

# Point to Sync API (port 8001)
client = EmbeddingSyncClient(
    api_base_url="http://your-server:8001",  # Sync API port
    local_cache_dir="data/local_embeddings"
)

# Fetch unsynced embeddings
result = client.sync_new_embeddings()
```

---

## Key Points

1. ✅ **Separate APIs**: Enrollment and Sync are completely separate
2. ✅ **Different Ports**: 8000 for enrollment, 8001 for sync
3. ✅ **Different Files**: `api.py` vs `sync_api.py`
4. ✅ **Different Purposes**: Upload vs Sync
5. ✅ **Same Database**: Both access same PostgreSQL database
6. ✅ **Independent**: Can run on same or different servers

---

## Summary

- **Enrollment API** (`backend/api.py`, port 8000): Static image uploads
- **Sync API** (`backend/sync_api.py`, port 8001): Live feed synchronization
- **Completely Separate**: Different files, ports, and purposes
- **Same Database**: Both use PostgreSQL for data storage

