# Enrollment Service

This service handles static image upload, face detection, embedding generation, and storage in PostgreSQL database.

## Structure

```
enrollment-service/
├── backend/              # FastAPI backend (Enrollment API)
│   ├── api.py           # Main enrollment API endpoints
│   ├── models.py        # Database models
│   ├── database.py      # Database connection
│   ├── config.py        # Configuration
│   ├── schemas.py       # Pydantic schemas
│   ├── services.py      # Business logic
│   └── integration.py   # Integration helpers
├── modules/
│   ├── detection/       # Static image face detection
│   ├── detectors/       # MTCNN, RetinaFace detectors
│   └── recognition/     # ArcFace embedding generation
├── main.py              # CLI entry point for image detection
├── upload_embedding_example.py  # Example: upload image with metadata
├── view_database_postgres.py    # Database viewer utility
├── run_backend.sh       # Start enrollment API server
├── detect_image.sh      # Run face detection on image
└── create_postgres_db.sh # Database setup script
```

## Quick Start

### 1. Start Enrollment API Server

```bash
cd enrollment-service
./run_backend.sh
```

API will be available at `http://localhost:8000`
API docs: `http://localhost:8000/docs`

### 2. Upload Image with Metadata

```bash
python upload_embedding_example.py \
    --image path/to/image.jpg \
    --name "John Doe" \
    --age 25 \
    --gender "M" \
    --api-url http://localhost:8000
```

### 3. Detect Faces in Image (without upload)

```bash
./detect_image.sh path/to/image.jpg mtcnn --embed
```

## Environment Variables

- `DATABASE_TYPE`: Database type (default: `postgresql`)
- `POSTGRES_HOST`: PostgreSQL host (default: `localhost`)
- `POSTGRES_PORT`: PostgreSQL port (default: `5432`)
- `POSTGRES_DB`: Database name (default: `face_system`)
- `POSTGRES_USER`: Database user (default: `postgres`)
- `POSTGRES_PASSWORD`: Database password (default: `postgres`)
- `API_PORT`: API server port (default: `8000`)

## API Endpoints

- `POST /api/upload-embedding` - Upload face embedding with person metadata
- `GET /api/persons/{person_id}` - Get person details
- `GET /api/persons/{person_id}/embeddings` - Get person's embeddings
- `GET /api/embeddings/{embedding_id}` - Get embedding details

See API docs at `/docs` for full details.

