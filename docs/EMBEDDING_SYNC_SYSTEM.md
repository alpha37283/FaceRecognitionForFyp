# Embedding Sync System Documentation

## Overview

This system implements a **trigger-based embedding sync** between the enrollment side (main server) and the surveillance side (live camera feed/Jetson Nano). The live feed automatically fetches new embeddings only when they are added to the database, avoiding continuous polling.

---

## System Architecture

### Two Separate Systems

1. **Enrollment Side (Main Server)**
   - User uploads static images
   - System generates embeddings and stores in PostgreSQL
   - Creates sync log entries with `synced="false"`

2. **Surveillance Side (Live Camera Feed/Jetson Nano)**
   - Runs locally on device
   - Automatically fetches new embeddings when added to database
   - Stores embeddings locally for face recognition comparison
   - Does NOT continuously poll - only fetches when new embeddings exist

---

## How It Works

### 1. Enrollment Flow (Static Images)

```
User Uploads Image
    ↓
Face Detection + Embedding Generation
    ↓
Store in PostgreSQL (face_embeddings table)
    ↓
Create Sync Log Entry (embedding_sync_log table)
    - synced = "false"
    - action = "INSERT"
    - timestamp = now()
```

### 2. Sync Trigger (Automatic)

When a new embedding is stored:
- A sync log entry is automatically created with `synced="false"`
- This acts as a **trigger** for the live feed system

### 3. Live Feed Sync Flow

```
Live Feed System (Background Service)
    ↓
Periodically checks: GET /api/sync-embeddings
    ↓
Backend returns only unsynced embeddings (synced="false")
    ↓
Live feed stores embeddings locally
    ↓
Marks as synced: POST /api/sync-embeddings/mark-synced
    ↓
Backend updates: synced="true"
```

---

## Components

### Backend API (Main Server)

#### 1. Sync Endpoint: `GET /api/sync-embeddings`
- Returns all unsynced embeddings with person metadata
- Only returns embeddings where `synced="false"`
- Includes: embedding vector, person name, age, gender, notes, etc.

**Response:**
```json
{
  "success": true,
  "count": 2,
  "updates": [
    {
      "sync_id": 1,
      "embedding_id": 123,
      "person_id": 1,
      "person_name": "John Doe",
      "person_age": 35,
      "person_gender": "M",
      "person_notes": "Security guard",
      "embedding_vector": [0.123, -0.456, ...],
      "action": "INSERT",
      "timestamp": "2024-11-20T10:00:00Z"
    }
  ]
}
```

#### 2. Mark Synced Endpoint: `POST /api/sync-embeddings/mark-synced`
- Marks embeddings as synced after live feed fetches them
- Updates `synced="true"` in database

**Request:**
```json
{
  "sync_ids": [1, 2, 3]
}
```

### Live Feed Sync Module

#### 1. `EmbeddingSyncClient` (`modules/recognition/sync_embeddings.py`)
- Fetches unsynced embeddings from backend
- Stores embeddings locally (`.npy` files)
- Maintains local cache with person metadata
- Handles INSERT, UPDATE, DELETE actions

#### 2. `EmbeddingSyncService` (`modules/recognition/embedding_sync_service.py`)
- Background service that automatically syncs embeddings
- Runs in separate thread
- Periodically checks for new embeddings (configurable interval)
- Triggers sync only when new embeddings exist

---

## Usage

### For Live Feed System (Jetson Nano)

#### Option 1: Automatic Background Sync

```python
from modules.recognition.embedding_sync_service import EmbeddingSyncService

# Initialize sync service
sync_service = EmbeddingSyncService(
    api_base_url="http://your-backend-server:8000",
    local_cache_dir="data/local_embeddings",
    sync_interval=5.0  # Check every 5 seconds
)

# Start background sync
sync_service.start()

# Your live camera code here...
# The sync service runs in background and automatically fetches new embeddings

# When done, stop the service
sync_service.stop()
```

#### Option 2: Manual Sync

```python
from modules.recognition.sync_embeddings import EmbeddingSyncClient

# Initialize sync client
sync_client = EmbeddingSyncClient(
    api_base_url="http://your-backend-server:8000",
    local_cache_dir="data/local_embeddings"
)

# Manually trigger sync
result = sync_client.sync_new_embeddings()
print(f"Fetched {result['fetched_count']} new embeddings")

# Get locally cached embeddings for face comparison
local_embeddings = sync_client.get_local_embeddings()
```

#### Option 3: Integration with Live Camera

```python
from modules.recognition.embedding_sync_service import EmbeddingSyncService
from modules.detection.face_detection_live import live_face_detection

# Start sync service in background
sync_service = EmbeddingSyncService(
    api_base_url="http://your-backend-server:8000",
    sync_interval=5.0
)
sync_service.start()

# Start live camera detection
# The sync service will automatically fetch new embeddings in background
live_face_detection(method="mtcnn", generate_embeddings=True)

# Stop sync service when done
sync_service.stop()
```

---

## Local Storage Structure

```
data/local_embeddings/
├── synced_embeddings.json          # Metadata cache
├── embedding_123.npy               # Embedding vector (512-dim)
├── embedding_124.npy
└── ...
```

**synced_embeddings.json** contains:
```json
{
  "last_sync": "2024-11-20T10:05:00Z",
  "embeddings": {
    "123": {
      "embedding_id": 123,
      "person_id": 1,
      "person_name": "John Doe",
      "person_age": 35,
      "person_gender": "M",
      "person_notes": "Security guard",
      "embedding_path": "data/local_embeddings/embedding_123.npy",
      "action": "INSERT",
      "timestamp": "2024-11-20T10:00:00Z",
      "synced_at": "2024-11-20T10:05:00Z"
    }
  }
}
```

---

## Database Schema

### `embedding_sync_log` Table

| Field | Type | Description |
|-------|------|-------------|
| `sync_id` | INT | Primary key |
| `embedding_id` | INT | Foreign key to face_embeddings |
| `person_id` | INT | Foreign key to persons |
| `action` | ENUM | INSERT, UPDATE, or DELETE |
| `timestamp` | TIMESTAMP | When change occurred |
| `synced` | VARCHAR(10) | "true" or "false" |

**Key Points:**
- When embedding is stored, sync log entry is created with `synced="false"`
- Live feed fetches only entries where `synced="false"`
- After fetching, live feed marks entries as `synced="true"`

---

## Key Features

1. **Trigger-Based**: Only fetches when new embeddings exist (no continuous polling)
2. **Automatic**: Background service handles sync automatically
3. **Efficient**: Only unsynced embeddings are transferred
4. **Local Cache**: Embeddings stored locally for fast face comparison
5. **Metadata Included**: Person name, age, gender, notes included with embeddings
6. **Action Support**: Handles INSERT, UPDATE, DELETE operations

---

## Configuration

### Sync Interval
- Default: 5 seconds
- Configurable in `EmbeddingSyncService(sync_interval=5.0)`
- Lower interval = faster sync but more API calls
- Higher interval = slower sync but fewer API calls

### API Base URL
- Default: `http://localhost:8000`
- Set to your backend server URL for production

### Local Cache Directory
- Default: `data/local_embeddings`
- Change if needed: `EmbeddingSyncClient(local_cache_dir="custom/path")`

---

## Example: Complete Live Feed with Sync

```python
import time
from modules.recognition.embedding_sync_service import EmbeddingSyncService
from modules.detection.face_detection_live import live_face_detection

# Initialize and start sync service
sync_service = EmbeddingSyncService(
    api_base_url="http://192.168.1.100:8000",  # Your backend server
    sync_interval=5.0
)
sync_service.start()

print(f"[INFO] Local embeddings cached: {sync_service.get_embedding_count()}")

try:
    # Start live camera detection
    # Sync service runs in background
    live_face_detection(method="mtcnn", generate_embeddings=True)
except KeyboardInterrupt:
    print("\n[INFO] Stopping...")
finally:
    sync_service.stop()
    print("[INFO] Sync service stopped")
```

---

## Testing

### Test Sync Manually

```python
from modules.recognition.sync_embeddings import EmbeddingSyncClient

client = EmbeddingSyncClient(api_base_url="http://localhost:8000")
result = client.sync_new_embeddings()

print(f"Fetched: {result['fetched_count']}")
print(f"Stored: {result['stored_count']}")
print(f"Failed: {result['failed_count']}")

# Check local cache
embeddings = client.get_local_embeddings()
print(f"Total cached: {len(embeddings)}")
```

---

## Summary

This system provides:
- ✅ Automatic sync when new embeddings are added
- ✅ No continuous polling (only fetches when needed)
- ✅ Local caching for fast face comparison
- ✅ Complete person metadata included
- ✅ Background service for hands-off operation
- ✅ Efficient and scalable

The live feed system automatically stays in sync with the enrollment database without manual intervention!

