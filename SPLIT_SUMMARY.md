# Project Split Summary

The project has been successfully split into two separate services:

## Directory Structure

```
faceSystem/
├── enrollment-service/      # Static image enrollment service
│   ├── backend/            # Enrollment API (port 8000)
│   ├── modules/            # Detection & recognition modules
│   ├── main.py            # CLI for image detection
│   ├── upload_embedding_example.py
│   └── run_backend.sh     # Start enrollment API
│
├── edge-recognition/       # Live camera feed recognition service
│   ├── backend/           # Sync API (port 8001)
│   ├── modules/           # Live detection & recognition modules
│   ├── main.py            # CLI for live detection
│   └── run_sync_api.sh    # Start sync API
│
└── docs/                   # Documentation
```

## Key Points

1. **Fully Separate**: Each service has its own copy of shared modules (MTCNN, RetinaFace, ArcFace, etc.)
2. **Same Database**: Both services connect to the same PostgreSQL database
3. **Independent Operation**: Each service can run independently
4. **No Shared Code**: No shared directory - all code is duplicated in each service

## Enrollment Service

- **Purpose**: Handle static image upload, face detection, embedding generation, storage
- **API Port**: 8000
- **Main Entry**: `main.py` (image detection CLI)
- **API Server**: `run_backend.sh`

## Edge Recognition Service

- **Purpose**: Live camera feed, face detection, embedding sync, real-time recognition
- **API Port**: 8001 (Sync API)
- **Main Entry**: `main.py` (live detection CLI)
- **API Server**: `run_sync_api.sh`

## How to Use

### Start Enrollment Service
```bash
cd enrollment-service
./run_backend.sh
```

### Start Edge Recognition Service
```bash
cd edge-recognition
./run_sync_api.sh  # Start sync API
python main.py --recognize  # Start live recognition
```

## Migration Notes

- All original files remain in root directory (can be removed if desired)
- Both services are fully functional and independent
- Database configuration is shared (same connection settings)
- Each service has its own README.md with usage instructions

