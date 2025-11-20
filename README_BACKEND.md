# Backend API Documentation

## Overview

The backend API is a **storage layer** that receives pre-generated embeddings and stores them in a database. It does NOT do image processing, face detection, or embedding generation.

**Architecture:**
- **Processing Service** (existing): Detects faces, generates embeddings
- **Backend API** (new): Stores embeddings and metadata in database

---

## Directory Structure

```
faceSystem/
├── backend/                    # Backend API (storage layer)
│   ├── __init__.py
│   ├── config.py              # Configuration
│   ├── database.py            # Database connection
│   ├── models.py              # Database models
│   ├── schemas.py             # Pydantic schemas
│   ├── services.py            # Business logic
│   ├── api.py                 # FastAPI application
│   └── integration.py        # API client for processing service
│
├── modules/                    # Processing service (existing)
│   ├── detection/             # Face detection
│   ├── detectors/             # Detection algorithms
│   └── recognition/           # Embedding generation
│       └── upload_to_backend.py  # Helper to upload embeddings
│
└── upload_embedding_example.py  # Example usage script
```

---

## Setup

### 1. Install Dependencies

```bash
cd /home/alpha/Desktop/FYP/faceSystem
source myenv/bin/activate
pip install fastapi uvicorn sqlalchemy pydantic requests
```

Or install from requirements:
```bash
pip install -r req.txt
```

### 2. Start Backend API Server

```bash
./run_backend.sh
```

The API will be available at:
- **API:** http://localhost:8000
- **Docs:** http://localhost:8000/docs
- **Alternative docs:** http://localhost:8000/redoc

### 3. Database

By default, the system uses **SQLite** (no setup required). The database file will be created at:
```
data/database/face_system.db
```

For PostgreSQL or MySQL, update `backend/config.py` or set environment variables.

---

## API Endpoints

### 1. Upload Embedding

**Endpoint:** `POST /api/persons/upload-embedding`

**Purpose:** Store pre-generated embedding + person metadata

**Request:**
```json
{
  "person_data": {
    "name": "John Doe",
    "age": 35,
    "gender": "M",
    "notes": "Security guard"
  },
  "embedding_data": {
    "embedding_vector": [0.123, -0.456, ...],  // 512 floats
    "source_image_url": "/path/to/image.jpg",
    "preprocessed_image_url": "/path/to/preprocessed_112x112.jpg",
    "detection_method": "mtcnn",
    "confidence_score": 0.95
  }
}
```

**Response:**
```json
{
  "success": true,
  "embedding_id": 123,
  "person_id": 1,
  "message": "Embedding stored successfully",
  "data": {
    "embedding_id": 123,
    "person_id": 1,
    "name": "John Doe",
    "created_at": "2024-11-19T10:01:00Z"
  }
}
```

### 2. Get Person

**Endpoint:** `GET /api/persons/{person_id}`

**Response:**
```json
{
  "person_id": 1,
  "name": "John Doe",
  "age": 35,
  "gender": "M",
  "notes": "Security guard",
  "created_at": "2024-11-19T10:00:00Z",
  "updated_at": "2024-11-19T10:00:00Z"
}
```

### 3. Get Person Embeddings

**Endpoint:** `GET /api/persons/{person_id}/embeddings`

**Response:**
```json
[
  {
    "embedding_id": 1,
    "person_id": 1,
    "source_image_url": "/path/to/image.jpg",
    "preprocessed_image_url": "/path/to/preprocessed_112x112.jpg",
    "detection_method": "mtcnn",
    "confidence_score": 0.95,
    "created_at": "2024-11-19T10:01:00Z"
  }
]
```

### 4. Get Embedding Vector

**Endpoint:** `GET /api/embeddings/{embedding_id}/vector`

**Response:**
```json
{
  "success": true,
  "embedding_id": 1,
  "person_id": 1,
  "name": "John Doe",
  "vector": [0.123, -0.456, ...]  // 512 floats
}
```

---

## Usage Examples

### Example 1: Using the Helper Script

```bash
# Start backend API first
./run_backend.sh

# In another terminal, process and upload
python upload_embedding_example.py \
  --image data/input_images/img1.jpeg \
  --name "John Doe" \
  --method mtcnn \
  --age 35 \
  --gender M \
  --notes "Security guard"
```

### Example 2: Programmatic Usage

```python
from modules.detection.face_detection_image import detect_faces_from_image
from modules.recognition.arcface_embedding import generate_embeddings_for_cropped_faces
from modules.recognition.upload_to_backend import upload_embedding

# Step 1: Detect faces
cropped_paths = detect_faces_from_image("image.jpg", method="mtcnn")

# Step 2: Generate embeddings
results = generate_embeddings_for_cropped_faces(cropped_paths)

# Step 3: Upload to backend
for face_path, data in results.items():
    upload_embedding(
        person_name="John Doe",
        embedding_vector=data['embedding'].tolist(),
        age=35,
        gender="M",
        source_image_url=face_path,
        preprocessed_image_url=data['preprocessed_path']
    )
```

### Example 3: Direct API Call

```python
import requests

payload = {
    "person_data": {
        "name": "John Doe",
        "age": 35,
        "gender": "M"
    },
    "embedding_data": {
        "embedding_vector": [0.123, -0.456, ...],  # 512 floats
        "detection_method": "mtcnn"
    }
}

response = requests.post(
    "http://localhost:8000/api/persons/upload-embedding",
    json=payload
)
print(response.json())
```

---

## Database Schema

### Tables

1. **persons**: Person information
2. **face_embeddings**: Embedding vectors
3. **embedding_sync_log**: Change tracking (for future node sync)

See `EMBEDDING_STORAGE_PLAN.md` for detailed schema.

---

## Configuration

Edit `backend/config.py` or set environment variables:

```bash
# Database type
export DATABASE_TYPE=sqlite  # or postgresql, mysql

# SQLite (default)
export SQLITE_DB_PATH=data/database/face_system.db

# PostgreSQL
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=face_system
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=password

# API
export API_HOST=0.0.0.0
export API_PORT=8000
export BACKEND_API_URL=http://localhost:8000
```

---

## Important Notes

1. **Backend API is storage-only**: It does NOT process images or generate embeddings
2. **Processing happens first**: Use existing modules to generate embeddings
3. **Modular design**: Backend and processing are separate
4. **Existing code unchanged**: All existing functionality still works

---

## Troubleshooting

### Backend API not starting
```bash
# Check if port 8000 is in use
lsof -i :8000

# Install dependencies
pip install fastapi uvicorn sqlalchemy pydantic
```

### Database errors
```bash
# Check database file exists
ls -la data/database/face_system.db

# Delete and recreate (WARNING: deletes all data)
rm data/database/face_system.db
# Restart backend - it will recreate the database
```

### Connection errors
```bash
# Check if backend is running
curl http://localhost:8000

# Check API docs
curl http://localhost:8000/docs
```

---

## Next Steps

1. Start backend API: `./run_backend.sh`
2. Process and upload image: `python upload_embedding_example.py --image <path> --name <name>`
3. View API docs: http://localhost:8000/docs
4. Query database to verify storage

---

**Status:** ✅ Backend API implemented and ready for use

