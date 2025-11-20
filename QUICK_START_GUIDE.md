# Quick Start Guide - Step by Step

## Complete System Setup and Usage

This guide walks you through running the entire system from start to finish.

---

## Prerequisites

- Python 3.11+ installed
- Virtual environment activated (`myenv`)
- Project located at `/home/alpha/Desktop/FYP/faceSystem`

---

## Step 1: Install Dependencies

### 1.1 Activate Virtual Environment

```bash
cd /home/alpha/Desktop/FYP/faceSystem
source myenv/bin/activate
```

You should see `(myenv)` in your terminal prompt.

### 1.2 Install Backend Dependencies

```bash
pip install fastapi uvicorn sqlalchemy pydantic requests
```

**Expected output:**
```
Successfully installed fastapi-0.104.x uvicorn-0.24.x sqlalchemy-2.0.x pydantic-2.0.x requests-2.31.x
```

**Note:** If you already have these installed, it will say "Requirement already satisfied".

---

## Step 2: Verify Existing System Works

### 2.1 Test Face Detection (Without Backend)

```bash
# Test basic detection
python main.py --mode image --input data/input_images/img1.jpeg --method mtcnn
```

**Expected output:**
```
[INFO] Running face detection on image: data/input_images/img1.jpeg
[+] Saved 1 face(s) to data/cropped_faces/
    - img1_20241119_XXXXXX_face1.jpg
```

### 2.2 Test Embedding Generation

```bash
# Test detection + embedding generation
python main.py --mode image --input data/input_images/img1.jpeg --method mtcnn --embed
```

**Expected output:**
```
[INFO] Running face detection on image: data/input_images/img1.jpeg
[+] Saved 1 face(s) to data/cropped_faces/
[INFO] Generating ArcFace embeddings...
[+] Generated 1 embedding(s)
[+] Embeddings saved to: data/embeddings/
```

**Verify files created:**
```bash
ls data/embeddings/*.npy
ls data/embeddings/preprocessed/*.jpg
```

If this works, your existing system is functioning correctly! ✅

---

## Step 3: Start Backend API Server

### 3.1 Start the Server

**Option A: Using the script (Recommended)**
```bash
./run_backend.sh
```

**Option B: Manual start**
```bash
cd /home/alpha/Desktop/FYP/faceSystem
source myenv/bin/activate
uvicorn backend.api:app --host 0.0.0.0 --port 8000 --reload
```

**Expected output:**
```
==========================================
  🚀 Starting Backend API Server
==========================================

[INFO] Starting API server on http://localhost:8000
[INFO] API docs available at http://localhost:8000/docs

INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
[INFO] Database initialized
INFO:     Application startup complete.
```

**Keep this terminal open!** The server must be running.

### 3.2 Verify Backend is Running

Open a **new terminal** and test:

```bash
curl http://localhost:8000
```

**Expected output:**
```json
{"message":"Face Embedding Storage API","version":"1.0.0","status":"running"}
```

Or open in browser: http://localhost:8000

### 3.3 View API Documentation

Open in browser: http://localhost:8000/docs

You should see the interactive API documentation (Swagger UI).

---

## Step 4: Process Image and Upload to Backend

### 4.1 Using the Example Script (Easiest)

**In a new terminal** (keep backend server running in first terminal):

```bash
cd /home/alpha/Desktop/FYP/faceSystem
source myenv/bin/activate

# Process image and upload embedding
python upload_embedding_example.py \
  --image data/input_images/img1.jpeg \
  --name "John Doe" \
  --method mtcnn \
  --age 35 \
  --gender M \
  --notes "Security guard"
```

**Expected output:**
```
[INFO] Processing image: data/input_images/img1.jpeg
[INFO] Person: John Doe
[INFO] Detection method: mtcnn

[STEP 1] Detecting faces...
[+] Detected 1 face(s)

[STEP 2] Generating embeddings...
[INFO] Initializing ArcFace embedding generator...
[+] Generated 1 embedding(s)

[STEP 3] Uploading to backend API...
[+] Uploaded embedding ID: 1
[+] Successfully uploaded 1 embedding(s) to backend
```

### 4.2 Verify Data Stored in Database

**Check via API:**

```bash
# Get person info
curl http://localhost:8000/api/persons/1

# Get person embeddings
curl http://localhost:8000/api/persons/1/embeddings
```

**Or check database file:**
```bash
# SQLite database location
ls -lh data/database/face_system.db
```

---

## Step 5: Complete Workflow Example

### 5.1 Process Multiple Images

```bash
# Image 1
python upload_embedding_example.py \
  --image data/input_images/img1.jpeg \
  --name "John Doe" \
  --method mtcnn \
  --age 35 \
  --gender M

# Image 2 (same person - will update existing person)
python upload_embedding_example.py \
  --image data/input_images/img2.png \
  --name "John Doe" \
  --method retinaface \
  --age 35 \
  --gender M

# Different person
python upload_embedding_example.py \
  --image data/input_images/img2.png \
  --name "Jane Smith" \
  --method mtcnn \
  --age 28 \
  --gender F \
  --notes "VIP visitor"
```

### 5.2 View All Persons

```bash
# Note: This endpoint needs to be added, but you can check via API docs
# Or query database directly
```

---

## Step 6: Programmatic Usage

### 6.1 Python Script Example

Create a file `my_upload_script.py`:

```python
#!/usr/bin/env python3
import sys
import os

# Add project root
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from modules.detection.face_detection_image import detect_faces_from_image
from modules.recognition.arcface_embedding import generate_embeddings_for_cropped_faces
from modules.recognition.upload_to_backend import upload_embedding

# Step 1: Detect faces
image_path = "data/input_images/img1.jpeg"
cropped_paths = detect_faces_from_image(image_path, method="mtcnn")

# Step 2: Generate embeddings
results = generate_embeddings_for_cropped_faces(
    cropped_paths,
    output_dir="data/embeddings",
    save_preprocessed=True
)

# Step 3: Upload to backend
for face_path, data in results.items():
    result = upload_embedding(
        person_name="John Doe",
        embedding_vector=data['embedding'].tolist(),
        age=35,
        gender="M",
        source_image_url=face_path,
        preprocessed_image_url=data['preprocessed_path'],
        detection_method="mtcnn"
    )
    print(f"Uploaded: {result['embedding_id']}")
```

Run it:
```bash
python my_upload_script.py
```

---

## Troubleshooting

### Problem: Backend won't start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
source myenv/bin/activate
pip install fastapi uvicorn sqlalchemy pydantic requests
```

### Problem: Port 8000 already in use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use different port
uvicorn backend.api:app --host 0.0.0.0 --port 8001
```

### Problem: Database errors

**Error:** `OperationalError: unable to open database file`

**Solution:**
```bash
# Create directory
mkdir -p data/database

# Check permissions
ls -la data/database/
```

### Problem: Backend API not reachable

**Error:** `Connection refused` or `Failed to upload`

**Solution:**
1. Check if backend is running: `curl http://localhost:8000`
2. Check firewall settings
3. Verify API URL: `echo $BACKEND_API_URL` (should be empty or `http://localhost:8000`)

### Problem: No face detected

**Error:** `No faces detected`

**Solution:**
- Try different image
- Try different detection method: `--method retinaface`
- Check image quality and lighting

---

## Quick Reference Commands

### Start Backend
```bash
./run_backend.sh
```

### Process & Upload Image
```bash
python upload_embedding_example.py \
  --image <path> \
  --name "<name>" \
  --method mtcnn
```

### Test Detection Only (No Backend)
```bash
python main.py --mode image --input <path> --method mtcnn --embed
```

### View API Docs
Open browser: http://localhost:8000/docs

### Check Database
```bash
ls -lh data/database/face_system.db
```

---

## Complete Workflow Summary

```
1. Install dependencies
   └─> pip install fastapi uvicorn sqlalchemy pydantic requests

2. Start backend API (Terminal 1)
   └─> ./run_backend.sh

3. Process & upload image (Terminal 2)
   └─> python upload_embedding_example.py --image <path> --name "<name>"

4. Verify in database
   └─> curl http://localhost:8000/api/persons/1
```

---

## Next Steps

1. ✅ System is running
2. ✅ Can process images
3. ✅ Can store embeddings in database
4. 🔄 Next: Query database, build frontend, or extend API

---

**Need Help?** Check:
- `README_BACKEND.md` - Detailed backend documentation
- `BACKEND_IMPLEMENTATION_SUMMARY.md` - Implementation details
- API Docs: http://localhost:8000/docs

