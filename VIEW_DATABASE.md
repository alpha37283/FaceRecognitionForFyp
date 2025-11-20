# How to View Database Contents

## Understanding SQLite vs PostgreSQL

### SQLite (Current Default)
- **File-based database**: The `.db` file IS the database
- **No server needed**: Everything in one file
- **Location**: `data/database/face_system.db`
- **Good for**: Development, small projects, single-user

### PostgreSQL (Server-based)
- **Server database**: Requires PostgreSQL server running
- **Multiple databases**: Can have many databases on one server
- **Better for**: Production, multiple users, large scale

---

## Viewing SQLite Database Contents

### Method 1: Using SQLite Command Line

```bash
cd /home/alpha/Desktop/FYP/faceSystem

# Open SQLite database
sqlite3 data/database/face_system.db
```

**Inside SQLite prompt:**
```sql
-- View all tables
.tables

-- View persons table
SELECT * FROM persons;

-- View face_embeddings table (without vector - too long)
SELECT embedding_id, person_id, source_image_url, created_at FROM face_embeddings;

-- View sync log
SELECT * FROM embedding_sync_log;

-- Count records
SELECT COUNT(*) FROM persons;
SELECT COUNT(*) FROM face_embeddings;

-- Exit
.quit
```

### Method 2: Using Python Script

Create a file `view_database.py`:

```python
#!/usr/bin/env python3
import sqlite3
import json

db_path = "data/database/face_system.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# View persons
print("=" * 50)
print("PERSONS TABLE")
print("=" * 50)
cursor.execute("SELECT * FROM persons")
persons = cursor.fetchall()
for person in persons:
    print(f"ID: {person[0]}, Name: {person[1]}, Age: {person[2]}, Gender: {person[3]}")

# View embeddings (without vector)
print("\n" + "=" * 50)
print("FACE_EMBEDDINGS TABLE")
print("=" * 50)
cursor.execute("""
    SELECT embedding_id, person_id, source_image_url, 
           detection_method, confidence_score, created_at 
    FROM face_embeddings
""")
embeddings = cursor.fetchall()
for emb in embeddings:
    print(f"Embedding ID: {emb[0]}, Person ID: {emb[1]}, Image: {emb[2]}")

# View sync log
print("\n" + "=" * 50)
print("SYNC LOG TABLE")
print("=" * 50)
cursor.execute("SELECT * FROM embedding_sync_log")
logs = cursor.fetchall()
for log in logs:
    print(f"Sync ID: {log[0]}, Embedding ID: {log[1]}, Action: {log[3]}")

conn.close()
```

Run it:
```bash
python view_database.py
```

### Method 3: Using DB Browser (GUI Tool)

**Install DB Browser for SQLite:**
```bash
# Ubuntu/Debian
sudo apt-get install sqlitebrowser

# Or download from: https://sqlitebrowser.org/
```

**Open database:**
1. Open DB Browser
2. File → Open Database
3. Navigate to: `/home/alpha/Desktop/FYP/faceSystem/data/database/face_system.db`
4. Browse tables and data

---

## Switching to PostgreSQL

### Step 1: Create PostgreSQL Database

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database
CREATE DATABASE face_system;

# Create user (optional)
CREATE USER face_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE face_system TO face_user;

# Exit
\q
```

### Step 2: Install PostgreSQL Driver

```bash
source myenv/bin/activate
pip install psycopg2-binary
```

### Step 3: Configure Backend

**Option A: Environment Variables**
```bash
export DATABASE_TYPE=postgresql
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=face_system
export POSTGRES_USER=face_user
export POSTGRES_PASSWORD=your_password
```

**Option B: Edit `backend/config.py`**
```python
DATABASE_TYPE = "postgresql"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"
POSTGRES_DB = "face_system"
POSTGRES_USER = "face_user"
POSTGRES_PASSWORD = "your_password"
```

### Step 4: Restart Backend

```bash
./run_backend.sh
```

The tables will be created automatically in PostgreSQL.

### Step 5: View PostgreSQL Database

```bash
# Connect to PostgreSQL
psql -U face_user -d face_system

# View tables
\dt

# View persons
SELECT * FROM persons;

# View embeddings
SELECT embedding_id, person_id, source_image_url FROM face_embeddings;

# Exit
\q
```

---

## Quick Commands Reference

### SQLite
```bash
# View database
sqlite3 data/database/face_system.db

# Quick query
sqlite3 data/database/face_system.db "SELECT * FROM persons;"
```

### PostgreSQL
```bash
# Connect
psql -U face_user -d face_system

# Or as postgres user
sudo -u postgres psql -d face_system
```

---

## Which Should You Use?

**Use SQLite if:**
- ✅ Development/testing
- ✅ Single user
- ✅ Small to medium data
- ✅ No server setup needed

**Use PostgreSQL if:**
- ✅ Production deployment
- ✅ Multiple users/applications
- ✅ Large scale data
- ✅ Need advanced features
- ✅ Already have PostgreSQL installed

---

## Current Status

Your system is using **SQLite** (file: `data/database/face_system.db`)

To view it:
```bash
sqlite3 data/database/face_system.db
.tables
SELECT * FROM persons;
```

