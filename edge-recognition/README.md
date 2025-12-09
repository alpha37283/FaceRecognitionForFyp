# Edge Recognition Service

This service handles live camera feed face detection, embedding generation, synchronization with the enrollment database, and real-time face recognition.

## Structure

```
edge-recognition/
├── backend/              # FastAPI backend (Sync API)
│   ├── sync_api.py      # Sync API endpoints for embedding sync
│   ├── models.py        # Database models (shared with enrollment)
│   ├── database.py      # Database connection
│   ├── config.py        # Configuration
│   ├── schemas.py       # Pydantic schemas
│   └── services.py      # Sync-related business logic
├── modules/
│   ├── detection/       # Live camera face detection
│   ├── detectors/       # MTCNN, RetinaFace detectors
│   └── recognition/     # Embedding generation, sync, matching
│       ├── arcface_embedding.py      # ArcFace embedding generator
│       ├── live_embedding.py         # Live feed embedding generation
│       ├── sync_embeddings.py        # Embedding sync client
│       ├── embedding_sync_service.py # Background sync service
│       └── face_matcher.py           # Face recognition matcher
├── main.py              # CLI entry point for live detection
├── run_sync_api.sh      # Start sync API server
├── run_live.sh          # Run live detection (MTCNN)
└── run_live_retinaface.sh # Run live detection (RetinaFace)
```

## Quick Start

### 1. Start Sync API Server

```bash
cd edge-recognition
./run_sync_api.sh
```

Sync API will be available at `http://localhost:8001`
The sync service automatically fetches new embeddings from the enrollment database every 3 seconds.

### 2. Run Live Face Detection

**Basic detection (no recognition):**
```bash
./run_live.sh
```

**With face recognition:**
```bash
python main.py --method mtcnn --recognize --similarity-threshold 0.6
```

**With RetinaFace:**
```bash
./run_live_retinaface.sh
```

**Full options:**
```bash
python main.py \
    --method mtcnn \
    --recognize \
    --similarity-threshold 0.6 \
    --detection-interval 60 \
    --iou-threshold 0.5
```

## How It Works

1. **Sync API** runs on port 8001 and automatically fetches new embeddings from the enrollment database
2. **Local Cache** stores synced embeddings in `data/local_embeddings/`
3. **Live Detection** captures frames from camera, detects faces, generates embeddings
4. **Face Recognition** compares live embeddings with cached embeddings using cosine similarity
5. **Results** are displayed on screen overlay and logged to `data/recognition_logs/`

## Environment Variables

- `SYNC_API_PORT`: Sync API port (default: `8001`)
- `SYNC_INTERVAL`: Sync check interval in seconds (default: `3.0`)
- `LOCAL_CACHE_DIR`: Local embedding cache directory (default: `data/local_embeddings`)
- Database config (same as enrollment-service)

## Recognition Features

- **Real-time matching**: Every detected face is immediately compared
- **Screen overlay**: Displays recognized person name
- **Console logging**: Logs name + age to console
- **File logging**: Saves recognition events to log files
- **Configurable threshold**: Adjust similarity threshold (default: 0.6)

## API Endpoints

- `GET /api/sync-embeddings` - Get unsynced embeddings (called by sync service)
- `POST /api/sync-embeddings/mark-synced` - Mark embeddings as synced

