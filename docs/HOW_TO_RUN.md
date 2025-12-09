# How to Run the System

Complete step-by-step guide to run the face detection, embedding storage, and recognition system.

---

## Prerequisites

- Python 3.11+
- PostgreSQL installed and running
- Virtual environment activated
- Webcam (for live camera feed)

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

## Complete System Workflow

### Step 1: Start Both API Servers

You need **TWO separate terminals**:

**Terminal 1 - Enrollment API (Port 8000):**
```bash
cd /home/alpha/Desktop/FYP/faceSystem
source myenv/bin/activate
./run_backend.sh
```

Keep this terminal open. You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
[INFO] Database initialized
```

**Terminal 2 - Sync API (Port 8001):**
```bash
cd /home/alpha/Desktop/FYP/faceSystem
source myenv/bin/activate
./run_sync_api.sh
```

Keep this terminal open. You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8001
[INFO] Automatic sync service started (checking every 3.0s)
```

---

### Step 2: Upload Images (Enrollment)

**Terminal 3 - Upload Images:**
```bash
cd /home/alpha/Desktop/FYP/faceSystem
source myenv/bin/activate

# Upload first person
python upload_embedding_example.py \
  --image data/input_images/img1.jpeg \
  --name "John Doe" \
  --method mtcnn \
  --age 35 \
  --gender M \
  --notes "Security guard"

# Upload more persons as needed
python upload_embedding_example.py \
  --image data/input_images/img2.png \
  --name "Jane Smith" \
  --method mtcnn \
  --age 28 \
  --gender F
```

**What happens:**
1. Face detected in image
2. ArcFace embedding generated (512-dim)
3. Stored in PostgreSQL database
4. Sync log entry created (`synced="false"`)
5. Sync API automatically fetches it (within 3 seconds)
6. Stored locally in `data/local_embeddings/`

**Watch Terminal 2** - you should see:
```
[SYNC] Fetched 1 new embedding(s), stored 1, failed 0
```

---

### Step 3: Run Live Camera with Recognition

**Terminal 4 - Live Camera Feed:**
```bash
cd /home/alpha/Desktop/FYP/faceSystem
source myenv/bin/activate

# Start live camera with recognition enabled
python main.py --mode live --method mtcnn --recognize --similarity-threshold 0.6
```

**What happens:**
- Camera opens and detects faces in real-time
- For each detected face:
  - Generates embedding immediately
  - Compares with all synced embeddings using cosine similarity
  - If match found (similarity ≥ 0.6):
    - **Red box** with **name** displayed on screen
    - Console: `[RECOGNIZED] ID-1: John Doe, Age: 35 (Similarity: 0.852)`
    - Log file: `data/recognition_logs/recognition_YYYYMMDD_HHMMSS.log`
  - If no match:
    - **Green box** with "NEW: ID-X"

**Press 'q' to quit**

---

## Quick Commands Reference

### Face Detection Only (No Database)

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

### Complete Workflow (Enrollment + Recognition)

**1. Start APIs:**
```bash
# Terminal 1
./run_backend.sh                 # Enrollment API (port 8000)

# Terminal 2
./run_sync_api.sh                # Sync API (port 8001)
```

**2. Upload Images:**
```bash
python upload_embedding_example.py \
  --image <path> \
  --name "<name>" \
  --method mtcnn \
  --age <age> \
  --gender <M/F>
```

**3. Run Live Recognition:**
```bash
python main.py --mode live --method mtcnn --recognize --similarity-threshold 0.6
```

### Database Operations
```bash
# View database contents
python view_database_postgres.py

# Using psql
sudo -u postgres psql -d face_system -c "SELECT * FROM persons;"
```

---

## API Endpoints

### Enrollment API (Port 8000)
- **Base URL:** http://localhost:8000
- **Docs:** http://localhost:8000/docs (Swagger UI)
- **Endpoints:**
  - `POST /api/persons/upload-embedding` - Upload embedding
  - `GET /api/persons/{person_id}` - Get person info
  - `GET /api/persons/{person_id}/embeddings` - Get person's embeddings
  - `GET /api/embeddings/{embedding_id}/vector` - Get embedding vector

### Sync API (Port 8001)
- **Base URL:** http://localhost:8001
- **Docs:** http://localhost:8001/docs (Swagger UI)
- **Endpoints:**
  - `GET /api/sync-embeddings` - Get unsynced embeddings
  - `POST /api/sync-embeddings/mark-synced` - Mark as synced

---

## Workflow Examples

### Example 1: Simple Face Detection (No Database)
```bash
./detect_image.sh data/input_images/img1.jpeg mtcnn
```

### Example 2: Detection with Embeddings (No Database)
```bash
./detect_image.sh data/input_images/img1.jpeg mtcnn --embed
```

### Example 3: Complete Enrollment Workflow
```bash
# Terminal 1: Start enrollment API
./run_backend.sh

# Terminal 2: Upload image
python upload_embedding_example.py \
  --image data/input_images/img1.jpeg \
  --name "John Doe" \
  --method mtcnn
```

### Example 4: Complete Recognition Workflow
```bash
# Terminal 1: Enrollment API
./run_backend.sh

# Terminal 2: Sync API
./run_sync_api.sh

# Terminal 3: Upload images (wait for sync)
python upload_embedding_example.py --image img1.jpeg --name "John" --method mtcnn

# Terminal 4: Run live recognition
python main.py --mode live --method mtcnn --recognize
```

---

## Output Locations

- **Cropped Faces:** `data/cropped_faces/`
- **Embeddings (Static):** `data/embeddings/*.npy`
- **Preprocessed Images:** `data/embeddings/preprocessed/`
- **Synced Embeddings:** `data/local_embeddings/*.npy`
- **Recognition Logs:** `data/recognition_logs/*.log`
- **Database:** PostgreSQL `face_system` database

---

## Recognition Parameters

### Similarity Threshold
- **Default:** 0.6
- **Range:** 0.0 to 1.0
- **Higher (0.7-0.8):** Stricter matching, fewer false positives
- **Lower (0.5-0.6):** More lenient, may have false positives

**Example:**
```bash
# Stricter matching
python main.py --mode live --recognize --similarity-threshold 0.7

# More lenient matching
python main.py --mode live --recognize --similarity-threshold 0.5
```

---

## Troubleshooting

### APIs won't start
```bash
# Check if ports are in use
netstat -tuln | grep 8000
netstat -tuln | grep 8001

# Kill processes if needed
kill -9 $(lsof -t -i:8000)
kill -9 $(lsof -t -i:8001)
```

### Database connection error
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Verify database exists
sudo -u postgres psql -c "\l face_system"

# Check password in backend/config.py
```

### No recognition happening
```bash
# Check if embeddings are synced
ls -la data/local_embeddings/

# Check sync API logs (Terminal 2)
# Should see: [SYNC] Fetched X new embedding(s)

# Verify embeddings exist
cat data/local_embeddings/synced_embeddings.json
```

### Recognition too sensitive/not sensitive enough
```bash
# Adjust similarity threshold
python main.py --mode live --recognize --similarity-threshold 0.7  # Stricter
python main.py --mode live --recognize --similarity-threshold 0.5  # More lenient
```

---

## System Architecture

```
Enrollment Side (Static Images)
    ↓
Enrollment API (Port 8000)
    ↓
PostgreSQL Database
    ↓ (automatic sync)
Sync API (Port 8001)
    ↓
Local Cache (data/local_embeddings/)
    ↓
Live Camera Feed
    ↓
Face Recognition (Cosine Similarity)
    ↓
Display + Logging
```

---

## Next Steps

1. Upload multiple person images to build database
2. Run live camera feed with recognition
3. View recognition logs in `data/recognition_logs/`
4. Adjust similarity threshold for optimal performance

For detailed technical documentation, see other files in the `docs/` directory.
