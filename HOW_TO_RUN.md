# How to Run the System

Complete step-by-step guide to run the face detection and embedding storage system.

---

## Prerequisites

- Python 3.11+
- PostgreSQL installed and running
- Virtual environment activated

---

## Initial Setup (One Time)

### 1. Activate Virtual Environment

```bash
cd /home/alpha/Desktop/FYP/faceSystem
source myenv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r req.txt
```

### 3. Create PostgreSQL Database

```bash
./create_postgres_db.sh
```

This creates the `face_system` database.

---

## Running the System

### Option A: Face Detection Only (No Database)

**Live Camera:**
```bash
./run_live.sh                    # MTCNN (fast)
./run_live_retinaface.sh         # RetinaFace (accurate)
```

**Static Image:**
```bash
./detect_image.sh data/input_images/img1.jpeg
./detect_image.sh data/input_images/img1.jpeg mtcnn --embed  # With embeddings
```

**Output:** Cropped faces saved to `data/cropped_faces/`

---

### Option B: Complete Workflow (Detection + Database Storage)

**Step 1: Start Backend API Server**

```bash
# Terminal 1
./run_backend.sh
```

Keep this terminal open. You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
[INFO] Database initialized
```

**Step 2: Process Image and Upload to Database**

```bash
# Terminal 2 (new terminal)
cd /home/alpha/Desktop/FYP/faceSystem
source myenv/bin/activate

python upload_embedding_example.py \
  --image data/input_images/img1.jpeg \
  --name "John Doe" \
  --method mtcnn \
  --age 35 \
  --gender M \
  --notes "Security guard"
```

**What happens:**
1. Detects face in image
2. Generates ArcFace embedding
3. Saves cropped face and preprocessed image
4. Uploads embedding + metadata to PostgreSQL

**Step 3: Verify Data in Database**

```bash
# View database contents
python view_database_postgres.py

# Or using psql
sudo -u postgres psql -d face_system -c "SELECT * FROM persons;"
```

---

## Quick Commands Reference

### Face Detection
```bash
# Live camera
./run_live.sh
./run_live_retinaface.sh

# Static image
./detect_image.sh <image_path> [method] [--embed]
```

### Database Operations
```bash
# Start backend
./run_backend.sh

# Process and upload
python upload_embedding_example.py --image <path> --name "<name>"

# View database
python view_database_postgres.py
sudo -u postgres psql -d face_system
```

### API Endpoints
- API Server: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: `curl http://localhost:8000`

---

## Workflow Examples

### Example 1: Simple Face Detection

```bash
# Just detect and save faces (no database)
./detect_image.sh data/input_images/img1.jpeg mtcnn
```

### Example 2: Detection with Embeddings

```bash
# Detect, generate embeddings, save files (no database)
./detect_image.sh data/input_images/img1.jpeg mtcnn --embed
```

### Example 3: Complete Workflow with Database

```bash
# Terminal 1: Start backend
./run_backend.sh

# Terminal 2: Process and store
python upload_embedding_example.py \
  --image data/input_images/img1.jpeg \
  --name "John Doe" \
  --method mtcnn
```

---

## Troubleshooting

### Backend won't start
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Install missing dependencies
pip install fastapi uvicorn sqlalchemy pydantic psycopg2-binary
```

### Database connection error
```bash
# Verify database exists
sudo -u postgres psql -c "\l face_system"

# Check password in backend/config.py
# Should be: POSTGRES_PASSWORD = "postgres"
```

### No faces detected
```bash
# Try different method
./detect_image.sh image.jpg retinaface

# Check image quality and lighting
```

---

## System Architecture

```
User Input
    │
    ├─> Processing Service (modules/)
    │   • Face Detection
    │   • Embedding Generation
    │
    └─> Backend API (backend/)
        • Database Storage
        • PostgreSQL
```

**Note:** Backend API is optional. Face detection works without it.

---

## Output Locations

- **Cropped Faces:** `data/cropped_faces/`
- **Embeddings:** `data/embeddings/*.npy`
- **Preprocessed Images:** `data/embeddings/preprocessed/`
- **Database:** PostgreSQL `face_system` database

---

## Next Steps

1. Process images and store embeddings
2. Query database for stored persons
3. Use embeddings for face recognition (future)

For detailed technical documentation, see `PHASE1.md` and `EMBEDDING_GENERATION.md`.

