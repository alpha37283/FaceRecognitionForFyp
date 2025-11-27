# End-to-End Testing Guide

## Complete Testing Steps

This guide walks you through testing the entire system:
1. Static image upload → Embedding generation → Database storage
2. Automatic sync → Local storage on live feed device

---

## Prerequisites

1. PostgreSQL database is running and configured
2. Virtual environment is activated
3. All dependencies are installed

---

## Step-by-Step Testing

### Step 1: Start Both API Servers

You need **TWO separate terminal windows**:

#### Terminal 1: Enrollment API (Port 8000)
```bash
cd /home/alpha/Desktop/FYP/faceSystem
source myenv/bin/activate
./run_backend.sh
```

**Expected output:**
```
==========================================
  🚀 Starting Backend API Server
==========================================
[INFO] Database initialized
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Keep this terminal open!**

#### Terminal 2: Sync API (Port 8001)
```bash
cd /home/alpha/Desktop/FYP/faceSystem
source myenv/bin/activate
./run_sync_api.sh
```

**Expected output:**
```
==========================================
  Starting Sync API Server
  Port: 8001
  Purpose: Live Feed Device Synchronization
==========================================
[INFO] Sync API database initialized
INFO:     Uvicorn running on http://0.0.0.0:8001
```

**Keep this terminal open!**

---

### Step 2: Verify APIs Are Running

Open a **third terminal** and test:

```bash
# Test Enrollment API
curl http://localhost:8000/

# Test Sync API
curl http://localhost:8001/
```

**Expected responses:**
- Enrollment API: `{"message":"Face Embedding Storage API",...}`
- Sync API: `{"message":"Face Embedding Sync API",...}`

---

### Step 3: Upload Static Image and Generate Embedding

In a **new terminal** (or use the third one):

```bash
cd /home/alpha/Desktop/FYP/faceSystem
source myenv/bin/activate

# Upload an image and generate embedding
python upload_embedding_example.py \
  --image data/input_images/img1.jpeg \
  --name "John Doe" \
  --method mtcnn \
  --age 35 \
  --gender M \
  --notes "Test person for sync"
```

**Expected output:**
```
[INFO] Processing image: data/input_images/img1.jpeg
[INFO] Person: John Doe
[STEP 1] Detecting faces...
[+] Detected 1 face(s)
[STEP 2] Generating embeddings...
[+] Generated 1 embedding(s)
[STEP 3] Uploading to backend API...
[+] Uploaded embedding ID: 1
[+] Successfully uploaded 1 embedding(s) to backend
```

**What happened:**
- ✅ Face detected in image
- ✅ Embedding generated (512-dim vector)
- ✅ Stored in PostgreSQL database
- ✅ Sync log entry created with `synced="false"`

---

### Step 4: Test Automatic Sync

Now test if the sync system automatically fetches the new embedding:

```bash
# Run the test script
python test_sync_system.py
```

**Expected output:**
```
======================================================================
  END-TO-END SYNC SYSTEM TEST
======================================================================

STEP 1: Checking API servers...
[✓] Enrollment API is running at http://localhost:8000
[✓] Sync API is running at http://localhost:8001

STEP 2: Initializing sync client...
[INFO] Current local embeddings: 0

STEP 3: Checking for unsynced embeddings...
[INFO] Found 1 unsynced embedding(s) in database
[INFO] These embeddings will be synced automatically
  - Embedding ID 1: John Doe

STEP 4: Triggering sync...
[+] Synced embedding ID 1 for person: John Doe
[+] Marked 1 embedding(s) as synced on server
[INFO] Sync result:
  - Fetched: 1
  - Stored: 1
  - Failed: 0

[+] Successfully synced 1 embedding(s)!

STEP 5: Verifying local storage...
[INFO] Local embeddings after sync: 1
[+] Successfully stored 1 new embedding(s) locally
[INFO] Local cache contains 1 embedding(s):
  - ID 1: John Doe
    Age: 35, Gender: M
    Vector shape: (512,)
```

**What happened:**
- ✅ Sync client checked for unsynced embeddings
- ✅ Found the new embedding (John Doe)
- ✅ Fetched embedding vector and person metadata
- ✅ Stored locally in `data/local_embeddings/`
- ✅ Marked as synced in database

---

### Step 5: Verify Local Storage

Check the local storage:

```bash
# Check local embeddings directory
ls -la data/local_embeddings/

# View cache metadata
cat data/local_embeddings/synced_embeddings.json
```

**Expected files:**
- `synced_embeddings.json` - Metadata cache
- `embedding_1.npy` - Embedding vector (512-dim)

---

### Step 6: Test Background Sync Service

Test the automatic background sync service:

```bash
python -c "
from modules.recognition.embedding_sync_service import EmbeddingSyncService
import time

# Start sync service
sync_service = EmbeddingSyncService(
    api_base_url='http://localhost:8001',
    sync_interval=3.0  # Check every 3 seconds
)
sync_service.start()

print('[INFO] Sync service started. Checking every 3 seconds...')
print('[INFO] Upload a new image in another terminal to test automatic sync')
print('Press Ctrl+C to stop')

try:
    while True:
        time.sleep(1)
        count = sync_service.get_embedding_count()
        print(f'[INFO] Local embeddings: {count}', end='\r')
except KeyboardInterrupt:
    print('\n[INFO] Stopping sync service...')
    sync_service.stop()
"
```

**In another terminal, upload another image:**
```bash
python upload_embedding_example.py \
  --image data/input_images/img2.png \
  --name "Jane Smith" \
  --method mtcnn \
  --age 28 \
  --gender F
```

**Watch the sync service terminal** - it should automatically detect and sync the new embedding within 3 seconds!

---

## Complete Test Flow

### Terminal 1: Enrollment API
```bash
./run_backend.sh
```

### Terminal 2: Sync API
```bash
./run_sync_api.sh
```

### Terminal 3: Upload Image
```bash
python upload_embedding_example.py \
  --image data/input_images/img1.jpeg \
  --name "Test Person" \
  --method mtcnn
```

### Terminal 4: Test Sync
```bash
python test_sync_system.py
```

---

## Verification Checklist

After running the tests, verify:

- [ ] Enrollment API is running on port 8000
- [ ] Sync API is running on port 8001
- [ ] Image uploaded successfully
- [ ] Embedding stored in database
- [ ] Sync log entry created with `synced="false"`
- [ ] Sync client fetched the embedding
- [ ] Embedding stored locally in `data/local_embeddings/`
- [ ] Sync log updated to `synced="true"`
- [ ] Local cache contains person metadata (name, age, gender)

---

## Troubleshooting

### APIs not starting
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
```

### No embeddings found
```bash
# Check database directly
python view_database_postgres.py

# Check sync log
sudo -u postgres psql -d face_system -c "SELECT * FROM embedding_sync_log;"
```

### Sync not working
```bash
# Test sync endpoint directly
curl http://localhost:8001/api/sync-embeddings

# Check sync client
python -c "
from modules.recognition.sync_embeddings import EmbeddingSyncClient
client = EmbeddingSyncClient(api_base_url='http://localhost:8001')
result = client.sync_new_embeddings()
print(result)
"
```

---

## Expected Results

After complete test:

1. **Enrollment API**: Running, ready to accept uploads
2. **Sync API**: Running, ready to serve sync requests
3. **Database**: Contains embedding with sync log entry
4. **Local Storage**: Contains synced embedding with metadata
5. **Sync Status**: Embedding marked as `synced="true"`

---

## Next Steps

Once testing is successful:

1. Integrate sync service into live camera feed
2. Use local embeddings for face recognition comparison
3. Set up automatic background sync on Jetson Nano
4. Configure production API URLs

---

## Summary

✅ **Two separate APIs** running on different ports
✅ **Static image upload** → Database storage
✅ **Automatic sync** → Local storage
✅ **Trigger-based** - only fetches when new embeddings exist
✅ **Complete metadata** - person info included with embeddings

The system is working end-to-end! 🎉

