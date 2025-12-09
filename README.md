# Face Recognition System

Complete face detection, embedding generation, and recognition system with PostgreSQL database integration.

## Quick Start

### 1. Setup
```bash
source myenv/bin/activate
pip install -r req.txt
./create_postgres_db.sh
```

### 2. Start APIs
```bash
# Terminal 1: Enrollment API
./run_backend.sh

# Terminal 2: Sync API
./run_sync_api.sh
```

### 3. Upload Images
```bash
python upload_embedding_example.py \
  --image data/input_images/img1.jpeg \
  --name "John Doe" \
  --method mtcnn \
  --age 35 \
  --gender M
```

### 4. Run Live Recognition
```bash
python main.py --mode live --method mtcnn --recognize --similarity-threshold 0.6
```

## Documentation

All documentation is in the `docs/` directory:
- **HOW_TO_RUN.md** - Complete usage guide
- **PROJECT_STATUS.md** - System status and capabilities
- **EMBEDDING_GENERATION.md** - Technical details
- **EMBEDDING_SYNC_SYSTEM.md** - Sync system documentation
- **API_SEPARATION.md** - API architecture

## System Components

- **Enrollment API** (Port 8000) - Static image upload and storage
- **Sync API** (Port 8001) - Automatic embedding synchronization
- **Live Camera Feed** - Real-time face detection and recognition
- **PostgreSQL Database** - Person and embedding storage

## Features

- ✅ Face detection (MTCNN/RetinaFace)
- ✅ ArcFace embedding generation
- ✅ Automatic embedding sync
- ✅ Real-time face recognition
- ✅ Cosine similarity matching
- ✅ Recognition logging

For detailed information, see `docs/HOW_TO_RUN.md`.

