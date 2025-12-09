# Local Embedding Storage Location

## Storage Directory

**Location:** `data/local_embeddings/`

This directory is automatically created when the sync system runs for the first time.

---

## Directory Structure

```
data/
├── cropped_faces/          # Cropped faces from detection
├── database/               # SQLite database (if used)
├── embeddings/             # Embeddings from static images (enrollment side)
│   ├── *.npy              # Embedding vectors
│   └── preprocessed/       # Preprocessed 112×112 images
├── input_images/          # Input images for processing
├── uploads/               # Uploaded images
└── local_embeddings/      # ← SYNCED EMBEDDINGS STORED HERE
    ├── synced_embeddings.json    # Metadata cache
    ├── embedding_1.npy           # Embedding vector (512-dim)
    ├── embedding_2.npy           # Embedding vector (512-dim)
    └── ...
```

---

## Files Stored

### 1. `synced_embeddings.json`
Metadata cache containing person information and embedding paths.

**Example:**
```json
{
  "last_sync": "2024-11-27T12:00:00Z",
  "embeddings": {
    "1": {
      "embedding_id": 1,
      "person_id": 1,
      "person_name": "John Doe",
      "person_age": 35,
      "person_gender": "M",
      "person_notes": "Security guard",
      "embedding_path": "data/local_embeddings/embedding_1.npy",
      "action": "INSERT",
      "timestamp": "2024-11-27T11:00:00Z",
      "synced_at": "2024-11-27T12:00:00Z"
    }
  }
}
```

### 2. `embedding_{id}.npy`
NumPy array files containing 512-dimensional embedding vectors.

**Format:**
- File: `embedding_1.npy`
- Content: NumPy array of shape `(512,)`
- Type: `float32`
- Usage: Load with `np.load('data/local_embeddings/embedding_1.npy')`

---

## How to Check

### View Directory
```bash
ls -la data/local_embeddings/
```

### View Metadata
```bash
cat data/local_embeddings/synced_embeddings.json
```

### Count Embeddings
```bash
ls -1 data/local_embeddings/*.npy | wc -l
```

### Load Embedding in Python
```python
import numpy as np

# Load embedding vector
embedding = np.load('data/local_embeddings/embedding_1.npy')
print(f"Shape: {embedding.shape}")  # Should be (512,)
print(f"Type: {embedding.dtype}")   # Should be float32
```

---

## Default Path

The default storage path is: **`data/local_embeddings/`**

You can change it when initializing the sync client:

```python
from modules.recognition.sync_embeddings import EmbeddingSyncClient

# Custom location
client = EmbeddingSyncClient(
    api_base_url="http://localhost:8001",
    local_cache_dir="custom/path/to/embeddings"  # Change here
)
```

---

## Automatic Creation

The directory is **automatically created** when:
1. `EmbeddingSyncClient` is initialized
2. First sync operation runs
3. `EmbeddingSyncService` starts

**No manual setup required!**

---

## Summary

- **Location**: `data/local_embeddings/`
- **Metadata**: `synced_embeddings.json`
- **Vectors**: `embedding_{id}.npy` files
- **Auto-created**: Yes, on first use
- **Purpose**: Local cache for face recognition comparison

