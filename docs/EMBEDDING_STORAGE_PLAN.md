# Embedding Storage + Sync Architecture - Planning Document

## Overview

This document outlines the architecture for storing face embeddings in a database and enabling synchronization with node devices for real-time face recognition.

**Current Phase:** User Upload Workflow (Backend API)  
**Future Phase:** Node Device Sync & Live Camera Comparison

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    TWO MAJOR WORKFLOWS                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  WORKFLOW A: User Upload (Current Focus)                        │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ 1. User uploads image + metadata (name, gender, etc.)   │ │
│  │ 2. Processing Service detects face                       │ │
│  │ 3. Processing Service preprocesses (ArcFace pipeline)   │ │
│  │ 4. Processing Service generates 512-dim embedding       │ │
│  │ 5. Backend API receives: embedding + metadata          │ │
│  │ 6. Backend API stores in database                        │ │
│  │ 7. Backend API logs to sync_log for node devices        │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ⚠️  IMPORTANT: Backend API does NOT do preprocessing/         │
│     embedding generation. It only receives and stores.        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  WORKFLOW B: Node Device Sync (Future)                          │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ 1. Node device polls /sync-embeddings                    │ │
│  │ 2. Backend returns incremental updates                   │ │
│  │ 3. Node updates local cache                               │ │
│  │ 4. Live camera compares with local cache                  │ │
│  │ 5. If match found → POST /alerts                         │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Database Schema Design

### Table 1: `persons`

Stores personal information for each registered person.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `person_id` | INT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier for person |
| `name` | VARCHAR(255) | NOT NULL | Person's full name |
| `age` | INT | NULL | Person's age (optional) |
| `gender` | VARCHAR(20) | NULL | Gender (optional: 'M', 'F', 'Other') |
| `notes` | TEXT | NULL | Additional description, remarks, or metadata |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE | Last update timestamp |

**Indexes:**
- PRIMARY KEY: `person_id`
- INDEX: `name` (for search)

**Example Data:**
```
person_id | name      | age | gender | notes              | created_at
----------|-----------|-----|--------|--------------------|-------------------
1         | John Doe  | 35  | M      | Security guard     | 2024-11-19 10:00:00
2         | Jane Smith| 28  | F      | VIP visitor        | 2024-11-19 10:05:00
```

---

### Table 2: `face_embeddings`

Stores 512-dimensional ArcFace embeddings generated from uploaded images.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `embedding_id` | INT | PRIMARY KEY, AUTO_INCREMENT | Unique identifier for embedding |
| `person_id` | INT | FOREIGN KEY → persons.person_id, NOT NULL | Links to person record |
| `embedding_vector` | VECTOR(512) / BLOB / JSON | NOT NULL | 512-dim ArcFace embedding |
| `source_image_url` | VARCHAR(500) | NULL | URL/path to original uploaded image |
| `preprocessed_image_url` | VARCHAR(500) | NULL | URL/path to 112×112 preprocessed image |
| `detection_method` | VARCHAR(20) | NULL | Detection method used ('mtcnn' or 'retinaface') |
| `confidence_score` | FLOAT | NULL | Detection confidence (0-1) |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Embedding creation timestamp |

**Indexes:**
- PRIMARY KEY: `embedding_id`
- FOREIGN KEY: `person_id` → `persons.person_id`
- INDEX: `person_id` (for person lookup)
- INDEX: `created_at` (for sync queries)

**Storage Options for `embedding_vector`:**
1. **PostgreSQL with pgvector** (Preferred):
   - Type: `VECTOR(512)`
   - Enables efficient similarity search
   - Supports cosine similarity queries

2. **MySQL/MariaDB**:
   - Type: `BLOB` or `JSON`
   - Store as binary or JSON array
   - Requires application-level similarity calculation

3. **SQLite**:
   - Type: `BLOB`
   - Store as NumPy array serialized (pickle/numpy format)

**Example Data:**
```
embedding_id | person_id | embedding_vector        | source_image_url                    | created_at
-------------|-----------|-------------------------|------------------------------------|-------------------
1            | 1         | [0.123, -0.456, ...]   | /uploads/persons/1/img1.jpg       | 2024-11-19 10:01:00
2            | 1         | [0.234, -0.567, ...]   | /uploads/persons/1/img2.jpg       | 2024-11-19 10:02:00
3            | 2         | [0.345, -0.678, ...]   | /uploads/persons/2/img1.jpg       | 2024-11-19 10:06:00
```

---

### Table 3: `embedding_sync_log`

Tracks all changes to embeddings for incremental synchronization with node devices.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `sync_id` | INT | PRIMARY KEY, AUTO_INCREMENT | Unique sync event identifier |
| `embedding_id` | INT | FOREIGN KEY → face_embeddings.embedding_id, NOT NULL | ID of affected embedding |
| `person_id` | INT | FOREIGN KEY → persons.person_id, NOT NULL | Person ID (denormalized for quick access) |
| `action` | ENUM('INSERT', 'UPDATE', 'DELETE') | NOT NULL | Type of change |
| `timestamp` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP, INDEX | When change occurred |
| `synced` | BOOLEAN | DEFAULT FALSE | Whether node devices have synced this change |

**Indexes:**
- PRIMARY KEY: `sync_id`
- FOREIGN KEY: `embedding_id` → `face_embeddings.embedding_id`
- FOREIGN KEY: `person_id` → `persons.person_id`
- INDEX: `timestamp` (for sync queries)
- INDEX: `synced` (for tracking sync status)
- COMPOSITE INDEX: `(timestamp, synced)` (for efficient sync queries)

**Example Data:**
```
sync_id | embedding_id | person_id | action | timestamp           | synced
--------|--------------|-----------|--------|---------------------|--------
1       | 1            | 1         | INSERT | 2024-11-19 10:01:00 | false
2       | 2            | 1         | INSERT | 2024-11-19 10:02:00 | false
3       | 3            | 2         | INSERT | 2024-11-19 10:06:00 | false
4       | 2            | 1         | DELETE | 2024-11-19 11:00:00 | false
```

---

## Database Choice Recommendations

### Option 1: PostgreSQL with pgvector (Recommended)
**Pros:**
- Native vector type support
- Efficient cosine similarity queries
- Excellent for face recognition workloads
- Mature and well-documented

**Cons:**
- Requires pgvector extension installation
- Slightly more complex setup

**Installation:**
```sql
CREATE EXTENSION vector;
```

### Option 2: MySQL/MariaDB
**Pros:**
- Widely used, familiar
- Good performance
- Easy setup

**Cons:**
- No native vector type
- Need to implement similarity in application code
- Less efficient for large-scale similarity search

### Option 3: SQLite
**Pros:**
- Zero configuration
- Good for development/testing
- File-based, portable

**Cons:**
- Not suitable for production scale
- No native vector support
- Limited concurrency

**Recommendation:** PostgreSQL with pgvector for production, SQLite for development.

---

## API Endpoints Design

### 1. Upload Embedding (Storage Only)

**Endpoint:** `POST /api/persons/upload-embedding`

**Purpose:** Store pre-generated embedding + person metadata in database

**⚠️ Important:** This endpoint does NOT do preprocessing or embedding generation. It only stores data.

**Request:**
```http
POST /api/persons/upload-embedding
Content-Type: application/json

{
  "person_data": {
    "name": "John Doe",
    "age": 35,
    "gender": "M",
    "notes": "Security guard"
  },
  "embedding_data": {
    "embedding_vector": [0.123, -0.456, 0.789, ...],  // 512 floats
    "source_image_url": "/uploads/persons/img_20241119_100100.jpg",
    "preprocessed_image_url": "/uploads/persons/preprocessed/img_20241119_100100_112x112.jpg",
    "detection_method": "mtcnn",
    "confidence_score": 0.95
  }
}
```

**Response (Success):**
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

**Response (Error):**
```json
{
  "success": false,
  "error": "Invalid embedding vector dimension",
  "code": "INVALID_EMBEDDING"
}
```

**Workflow:**
1. Receive embedding vector + person metadata
2. Validate embedding (check dimension = 512)
3. Check if person exists (by name or create new)
4. Insert into `persons` table (if new person)
5. Insert into `face_embeddings` table
6. Insert into `embedding_sync_log` (action: INSERT)
7. Return response

**Note:** Embedding generation happens BEFORE this API call (using existing system).

---

### 2. Create Person

**Endpoint:** `POST /api/persons`

**Purpose:** Create a new person record

**Request:**
```http
POST /api/persons
Content-Type: application/json

{
  "name": "John Doe",
  "age": 35,
  "gender": "M",
  "notes": "Security guard"
}
```

**Response:**
```json
{
  "success": true,
  "person_id": 1,
  "data": {
    "person_id": 1,
    "name": "John Doe",
    "age": 35,
    "gender": "M",
    "notes": "Security guard",
    "created_at": "2024-11-19T10:00:00Z"
  }
}
```

---

### 3. Get Person Embeddings

**Endpoint:** `GET /api/persons/{person_id}/embeddings`

**Purpose:** Retrieve all embeddings for a person

**Response:**
```json
{
  "success": true,
  "person_id": 1,
  "count": 2,
  "embeddings": [
    {
      "embedding_id": 1,
      "source_image_url": "/uploads/persons/1/img1.jpg",
      "preprocessed_image_url": "/uploads/persons/1/preprocessed/img1_112x112.jpg",
      "created_at": "2024-11-19T10:01:00Z"
    },
    {
      "embedding_id": 2,
      "source_image_url": "/uploads/persons/1/img2.jpg",
      "preprocessed_image_url": "/uploads/persons/1/preprocessed/img2_112x112.jpg",
      "created_at": "2024-11-19T10:02:00Z"
    }
  ]
}
```

**Note:** Embedding vectors are NOT returned (too large). Use specific endpoint if needed.

---

### 4. Get Embedding Vector (For Comparison)

**Endpoint:** `GET /api/embeddings/{embedding_id}/vector`

**Purpose:** Get actual embedding vector for comparison

**Response:**
```json
{
  "success": true,
  "embedding_id": 1,
  "person_id": 1,
  "vector": [0.123, -0.456, 0.789, ...],  // 512 floats
  "name": "John Doe"
}
```

---

### 5. Sync Embeddings (For Node Devices - Future)

**Endpoint:** `GET /api/sync-embeddings?after={timestamp}`

**Purpose:** Get incremental updates since last sync

**Request:**
```http
GET /api/sync-embeddings?after=2024-11-19T10:00:00Z
```

**Response:**
```json
{
  "success": true,
  "server_time": "2024-11-19T11:00:00Z",
  "updates": [
    {
      "embedding_id": 123,
      "action": "INSERT",
      "person_id": 1,
      "name": "John Doe",
      "vector": [0.123, -0.456, ...],  // 512 floats
      "timestamp": "2024-11-19T10:01:00Z"
    },
    {
      "embedding_id": 124,
      "action": "INSERT",
      "person_id": 2,
      "name": "Jane Smith",
      "vector": [0.234, -0.567, ...],
      "timestamp": "2024-11-19T10:06:00Z"
    },
    {
      "embedding_id": 125,
      "action": "DELETE",
      "person_id": 1,
      "timestamp": "2024-11-19T11:00:00Z"
    }
  ]
}
```

**Query Logic:**
```sql
SELECT 
  e.embedding_id,
  e.person_id,
  p.name,
  e.embedding_vector as vector,
  s.action,
  s.timestamp
FROM embedding_sync_log s
JOIN face_embeddings e ON s.embedding_id = e.embedding_id
JOIN persons p ON e.person_id = p.person_id
WHERE s.timestamp > :after_timestamp
  AND s.synced = false
ORDER BY s.timestamp ASC;
```

---

## Integration with Existing System

### Current System Flow (What We Have Now)

```
User Input Image
    │
    ├─> detect_faces_from_image()
    │   • Detects faces
    │   • Saves cropped faces
    │   • Generates embeddings (if --embed)
    │
    └─> Returns: saved_paths (list of cropped face paths)
```

**Current Capabilities:**
- ✅ Face detection (MTCNN/RetinaFace)
- ✅ Embedding generation (ArcFace)
- ✅ Preprocessed image saving
- ❌ Database storage (not implemented yet)
- ❌ Person metadata handling (not implemented yet)

### New System Flow (Planned)

```
User Upload Image + Metadata
    │
    ├─> Processing Service (Existing System)
    │   • detect_faces_from_image()
    │   • Generates embeddings (ArcFace)
    │   • Returns: embedding vector + metadata
    │
    ├─> API Endpoint: POST /api/persons/upload-embedding
    │   • Receives: embedding vector + person metadata
    │   • Does NOT do preprocessing/embedding generation
    │
    ├─> Database Operations:
    │   • INSERT into persons (if new person)
    │   • INSERT into face_embeddings
    │   • INSERT into embedding_sync_log (action: INSERT)
    │
    └─> Return: embedding_id, person_id
```

**Key Point:** Backend API is a **storage layer only**. It receives pre-generated embeddings and stores them.

### Integration Points

1. **Processing Service (Existing System):**
   - `modules/detection/face_detection_image.py` - Face detection
   - `modules/detectors/mtcnn_detector.py` - MTCNN detector
   - `modules/detectors/retinaface_detector.py` - RetinaFace detector
   - `modules/recognition/arcface_embedding.py` - Embedding generation
   - `ArcFaceEmbeddingGenerator` class
   - **Role:** Generates embeddings from images

2. **Backend API (New - Storage Layer Only):**
   - Database connection module
   - API server (Flask/FastAPI)
   - Database models/ORM
   - **Role:** Receives embeddings + metadata, stores in database
   - **Does NOT:** Process images, detect faces, generate embeddings

3. **Data Flow:**
   ```
   Processing Service → Embedding + Metadata → Backend API → Database
   ```

---

## File Storage Structure

```
uploads/
├── persons/
│   ├── 1/                          # person_id = 1
│   │   ├── img_20241119_100100.jpg # Original uploaded image
│   │   ├── img_20241119_100200.jpg
│   │   └── preprocessed/
│   │       ├── img_20241119_100100_112x112.jpg
│   │       └── img_20241119_100200_112x112.jpg
│   │
│   ├── 2/                          # person_id = 2
│   │   ├── img_20241119_100600.jpg
│   │   └── preprocessed/
│   │       └── img_20241119_100600_112x112.jpg
│   │
│   └── ...
│
└── cropped_faces/                  # Temporary (from detection)
    └── ...
```

---

## Workflow Diagrams

### User Upload Workflow

```
┌──────────────┐
│   User       │
│  (Browser/   │
│   Client)    │
└──────┬───────┘
       │
       │ Upload: Image + Metadata (name, gender, age, notes)
       ▼
┌─────────────────────────────────────────────────────────────┐
│          PROCESSING SERVICE (Existing System)                │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ 1. Receive Image & Metadata                         │ │
│  │    • Validate image format                           │ │
│  │    • Extract metadata                                │ │
│  └────────────────────┬───────────────────────────────────┘ │
│                       │                                     │
│                       ▼                                     │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ 2. Face Detection                                     │ │
│  │    • Call: detect_faces_from_image()                 │ │
│  │    • Method: MTCNN or RetinaFace                      │ │
│  │    • Returns: List of cropped faces                  │ │
│  └────────────────────┬───────────────────────────────────┘ │
│                       │                                     │
│                       ▼                                     │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ 3. Embedding Generation                               │ │
│  │    • Call: generate_embeddings_for_cropped_faces()    │ │
│  │    • ArcFace preprocessing pipeline                    │ │
│  │    • Returns: 512-dim embedding vector                │ │
│  │    • Returns: preprocessed 112×112 image              │ │
│  └────────────────────┬───────────────────────────────────┘ │
│                       │                                     │
│                       ▼                                     │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ 4. Prepare Data for Backend                           │ │
│  │    • Combine: embedding + metadata                   │ │
│  │    • Format: JSON payload                             │ │
│  └────────────────────┬───────────────────────────────────┘ │
└───────────────────────┼─────────────────────────────────────┘
                        │
                        │ POST /api/persons/upload-embedding
                        │ { person_data, embedding_data }
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND API SERVER                        │
│              (Storage Layer - No Processing)                │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ 1. Receive Embedding + Metadata                      │ │
│  │    • Validate embedding vector (512 dim)             │ │
│  │    • Validate person metadata                        │ │
│  └────────────────────┬───────────────────────────────────┘ │
│                       │                                     │
│                       ▼                                     │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ 2. Check/Create Person                                │ │
│  │    • Check if person exists (by name)                │ │
│  │    • If new: INSERT INTO persons                     │ │
│  │    • Get person_id                                    │ │
│  └────────────────────┬───────────────────────────────────┘ │
│                       │                                     │
│                       ▼                                     │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ 3. Store Embedding                                    │ │
│  │    ┌──────────────────────────────────────────────┐ │ │
│  │    │ INSERT INTO face_embeddings                  │ │ │
│  │    │   (person_id, embedding_vector,              │ │ │
│  │    │    source_image_url, preprocessed_image_url) │ │ │
│  │    └──────────────────────────────────────────────┘ │ │
│  └────────────────────┬───────────────────────────────────┘ │
│                       │                                     │
│                       ▼                                     │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ 4. Log Sync Event                                     │ │
│  │    ┌──────────────────────────────────────────────┐ │ │
│  │    │ INSERT INTO embedding_sync_log               │ │ │
│  │    │   (embedding_id, person_id, action='INSERT')│ │ │
│  │    └──────────────────────────────────────────────┘ │ │
│  └────────────────────┬───────────────────────────────────┘ │
│                       │                                     │
│                       ▼                                     │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ 5. Return Response                                    │ │
│  │    • embedding_id                                    │ │
│  │    • person_id                                       │ │
│  │    • Success message                                 │ │
│  └────────────────────┬───────────────────────────────────┘ │
└───────────────────────┼─────────────────────────────────────┘
                        │
                        ▼
                ┌──────────────┐
                │   Response    │
                │  to Client    │
                └──────────────┘
```

**Key Architecture Points:**
- **Processing Service:** Handles detection + embedding generation (existing system)
- **Backend API:** Storage layer only - receives pre-generated embeddings
- **Separation of Concerns:** Processing and storage are separate

---

## Processing Service to Backend API Interface

### Data Contract

**What Processing Service Sends:**
```python
{
    "person_data": {
        "name": "John Doe",           # Required
        "age": 35,                    # Optional
        "gender": "M",                 # Optional: 'M', 'F', 'Other'
        "notes": "Security guard"      # Optional
    },
    "embedding_data": {
        "embedding_vector": [0.123, -0.456, ...],  # Required: 512 floats
        "source_image_url": "/path/to/original.jpg",  # Optional
        "preprocessed_image_url": "/path/to/preprocessed_112x112.jpg",  # Optional
        "detection_method": "mtcnn",   # Optional: 'mtcnn' or 'retinaface'
        "confidence_score": 0.95       # Optional: 0.0 to 1.0
    }
}
```

**What Backend API Returns:**
```python
{
    "success": True,
    "embedding_id": 123,
    "person_id": 1,
    "message": "Embedding stored successfully"
}
```

### Integration Code Example

**In Processing Service (After embedding generation):**
```python
# After generating embedding
embedding, preprocessed_img, landmarks = generator.generate_embedding(face_image)

# Prepare data for backend API
payload = {
    "person_data": {
        "name": user_provided_name,
        "age": user_provided_age,
        "gender": user_provided_gender,
        "notes": user_provided_notes
    },
    "embedding_data": {
        "embedding_vector": embedding.tolist(),  # Convert numpy to list
        "source_image_url": saved_image_path,
        "preprocessed_image_url": saved_preprocessed_path,
        "detection_method": "mtcnn",
        "confidence_score": detection_confidence
    }
}

# Send to backend API
response = requests.post(
    "http://backend-api/api/persons/upload-embedding",
    json=payload
)
```

---

## Database Connection Architecture

### Option 1: Direct SQL (Simple)

```python
# db_connection.py
import psycopg2  # or mysql.connector, sqlite3
from config import DB_CONFIG

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def insert_embedding(person_id, embedding_vector, source_image_url, ...):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO face_embeddings (person_id, embedding_vector, ...) VALUES (%s, %s, ...)",
        (person_id, embedding_vector, ...)
    )
    conn.commit()
    return cursor.lastrowid
```

### Option 2: ORM (Recommended for Scalability)

```python
# models.py (using SQLAlchemy)
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Person(Base):
    __tablename__ = 'persons'
    person_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    age = Column(Integer)
    gender = Column(String(20))
    notes = Column(Text)
    created_at = Column(DateTime)
    embeddings = relationship("FaceEmbedding", back_populates="person")

class FaceEmbedding(Base):
    __tablename__ = 'face_embeddings'
    embedding_id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('persons.person_id'))
    embedding_vector = Column(Vector(512))  # or BLOB/JSON
    source_image_url = Column(String(500))
    # ... other fields
    person = relationship("Person", back_populates="embeddings")
```

---

## API Server Framework Choice

### Option 1: Flask (Simple, Flexible)
**Pros:**
- Lightweight
- Easy to learn
- Good for small to medium APIs
- Large ecosystem

**Cons:**
- Less structured
- Manual async support

### Option 2: FastAPI (Recommended)
**Pros:**
- Modern, fast
- Automatic API documentation
- Built-in async support
- Type hints
- Excellent for Python APIs

**Cons:**
- Newer framework (but mature)

**Recommendation:** FastAPI for better structure and automatic docs.

---

## Error Handling Strategy

### Common Error Scenarios

1. **No Face Detected**
   - Status: 400 Bad Request
   - Response: `{"error": "No face detected in image", "code": "NO_FACE_DETECTED"}`

2. **Multiple Faces Detected**
   - Status: 400 Bad Request
   - Response: `{"error": "Multiple faces detected. Please upload image with single face", "code": "MULTIPLE_FACES"}`

3. **Invalid Person ID**
   - Status: 404 Not Found
   - Response: `{"error": "Person not found", "code": "PERSON_NOT_FOUND"}`

4. **Database Error**
   - Status: 500 Internal Server Error
   - Response: `{"error": "Database operation failed", "code": "DB_ERROR"}`

5. **Invalid Image Format**
   - Status: 400 Bad Request
   - Response: `{"error": "Invalid image format. Supported: jpg, png", "code": "INVALID_FORMAT"}`

---

## Security Considerations

1. **Image Upload Validation**
   - File type validation (whitelist: jpg, png, jpeg)
   - File size limits (e.g., max 10MB)
   - Malware scanning (optional)

2. **Authentication & Authorization**
   - API key or JWT tokens
   - Role-based access control
   - Rate limiting

3. **Data Privacy**
   - Encrypt sensitive data
   - Secure storage of images
   - GDPR compliance considerations

---

## Future Considerations (Node Device Sync)

### Node Device Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Node Device                               │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Local Cache:                                          │ │
│  │   last_sync_timestamp = "2024-11-19T10:00:00Z"       │ │
│  │   embeddings = {                                     │ │
│  │     1: [0.123, -0.456, ...],  # person_id: vector    │ │
│  │     2: [0.234, -0.567, ...],                         │ │
│  │   }                                                   │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Periodic Sync (every 5 minutes):                     │ │
│  │   GET /api/sync-embeddings?after={last_sync}         │ │
│  │   Update local cache                                  │ │
│  │   Update last_sync_timestamp                         │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Live Camera Comparison:                               │ │
│  │   1. Detect face in frame                            │ │
│  │   2. Generate embedding                              │ │
│  │   3. Compare with local cache (cosine similarity)     │ │
│  │   4. If match > threshold → POST /api/alerts        │ │
│  └──────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Alert Endpoint (Future)

**Endpoint:** `POST /api/alerts`

**Purpose:** Node device sends alert when person is recognized

**Request:**
```json
{
  "person_id": 1,
  "similarity_score": 0.95,
  "frame_snapshot": "<base64_encoded_image>",
  "timestamp": "2024-11-19T12:00:00Z",
  "node_device_id": "node_001"
}
```

---

## Implementation Checklist

### Phase 1: Database Setup
- [ ] Choose database (PostgreSQL recommended)
- [ ] Install pgvector extension (if PostgreSQL)
- [ ] Create database schema
- [ ] Create tables: `persons`, `face_embeddings`, `embedding_sync_log`
- [ ] Set up indexes
- [ ] Test database connections

### Phase 2: API Server Setup
- [ ] Choose framework (FastAPI recommended)
- [ ] Set up project structure
- [ ] Create database connection module
- [ ] Create ORM models (or direct SQL)
- [ ] Set up image storage handler
- [ ] Create API endpoints

### Phase 3: Integration
- [ ] Integrate with existing detection module
- [ ] Integrate with existing embedding module
- [ ] Create upload endpoint handler
- [ ] Implement database insert logic
- [ ] Implement sync log insertion
- [ ] Add error handling

### Phase 4: Testing
- [ ] Test image upload
- [ ] Test face detection integration
- [ ] Test embedding generation
- [ ] Test database storage
- [ ] Test API responses
- [ ] Test error cases

### Phase 5: Documentation
- [ ] API documentation (Swagger/OpenAPI)
- [ ] Database schema documentation
- [ ] Integration guide
- [ ] Deployment guide

---

## Complete Workflow Summary

### Step-by-Step Process

1. **User Uploads Image + Metadata**
   - Image file (jpg, png, etc.)
   - Person metadata: name, age, gender, notes

2. **Processing Service (Existing System)**
   - Receives image
   - Runs face detection (MTCNN/RetinaFace)
   - Generates embedding (ArcFace pipeline)
   - Returns: embedding vector (512-dim) + preprocessed image

3. **Backend API (Storage Layer)**
   - Receives: embedding vector + person metadata
   - **Does NOT process images or generate embeddings**
   - Creates/updates person record
   - Stores embedding in database
   - Logs sync event

4. **Database Storage**
   - `persons` table: Person information
   - `face_embeddings` table: Embedding vectors
   - `embedding_sync_log` table: Change tracking

### Key Architecture Principle

**Separation of Concerns:**
- **Processing Service:** Image processing, face detection, embedding generation
- **Backend API:** Data storage, database operations, sync management
- **Clear Interface:** JSON API between processing and storage

---

## Summary

This planning document outlines:

1. **Database Schema:** Three tables (persons, face_embeddings, embedding_sync_log)
2. **API Endpoints:** RESTful API for storing pre-generated embeddings
3. **Architecture:** Separation between processing (existing) and storage (new)
4. **Workflow:** User upload → Processing Service → Backend API → Database
5. **Future:** Node device sync architecture (for later implementation)

**Key Points:**
- ✅ Backend API is **storage layer only** - no processing
- ✅ Processing happens in existing system (before API call)
- ✅ Clean separation: Processing Service ↔ Backend API
- ✅ Backend receives embeddings + metadata, stores in database

**Next Steps:**
- Review and approve this plan
- Set up database
- Implement Backend API (storage layer)
- Create interface between Processing Service and Backend API
- Test end-to-end workflow

---

**Document Version:** 1.0  
**Status:** Planning Phase  
**Last Updated:** November 2024

