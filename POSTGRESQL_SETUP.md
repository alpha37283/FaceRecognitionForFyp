# PostgreSQL Setup Guide

## ✅ System Converted to PostgreSQL

The system has been converted from SQLite to PostgreSQL. Follow these steps to complete setup.

---

## Step 1: Create PostgreSQL Database

Run the setup script:

```bash
cd /home/alpha/Desktop/FYP/faceSystem
./create_postgres_db.sh
```

**Or manually:**
```bash
sudo -u postgres psql -c "CREATE DATABASE face_system;"
```

**Verify database exists:**
```bash
sudo -u postgres psql -c "\l face_system"
```

---

## Step 2: Install PostgreSQL Driver

```bash
cd /home/alpha/Desktop/FYP/faceSystem
source myenv/bin/activate
pip install psycopg2-binary
```

---

## Step 3: Configure Backend (Already Done)

The backend is already configured to use PostgreSQL by default:
- **Database:** `face_system`
- **User:** `postgres`
- **Host:** `localhost`
- **Port:** `5432`

If you need to change these, edit `backend/config.py` or set environment variables:
```bash
export POSTGRES_DB=face_system
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=your_password  # If you set a password
```

---

## Step 4: Start Backend API

```bash
./run_backend.sh
```

The backend will:
1. Connect to PostgreSQL
2. Create all tables automatically
3. Start the API server

**Expected output:**
```
[INFO] Database initialized
INFO:     Application startup complete.
```

---

## Step 5: Verify PostgreSQL Connection

**Test connection:**
```bash
psql -U postgres -d face_system -c "\dt"
```

**View tables:**
```bash
psql -U postgres -d face_system
```

Inside psql:
```sql
\dt                    -- List tables
SELECT * FROM persons; -- View persons
\q                     -- Exit
```

---

## Step 6: Test the System

**Process and upload an image:**
```bash
python upload_embedding_example.py \
  --image data/input_images/img1.jpeg \
  --name "John Doe" \
  --method mtcnn
```

**Verify data in PostgreSQL:**
```bash
psql -U postgres -d face_system -c "SELECT * FROM persons;"
psql -U postgres -d face_system -c "SELECT embedding_id, person_id FROM face_embeddings;"
```

---

## Configuration Summary

### Current Settings (in `backend/config.py`):
- **DATABASE_TYPE:** `postgresql` (default)
- **POSTGRES_HOST:** `localhost`
- **POSTGRES_PORT:** `5432`
- **POSTGRES_DB:** `face_system`
- **POSTGRES_USER:** `postgres`
- **POSTGRES_PASSWORD:** `` (empty - uses trust authentication)

### If PostgreSQL Requires Password:

1. **Set password in environment:**
   ```bash
   export POSTGRES_PASSWORD=your_password
   ```

2. **Or edit `backend/config.py`:**
   ```python
   POSTGRES_PASSWORD = "your_password"
   ```

---

## Troubleshooting

### Error: "database does not exist"
```bash
# Create database
sudo -u postgres psql -c "CREATE DATABASE face_system;"
```

### Error: "psycopg2 not found"
```bash
pip install psycopg2-binary
```

### Error: "connection refused"
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Start if needed
sudo systemctl start postgresql
```

### Error: "password authentication failed"
- If you set a password, make sure `POSTGRES_PASSWORD` is set correctly
- Or use trust authentication (default for local PostgreSQL)

---

## Migration from SQLite

**Note:** If you had data in SQLite (`data/database/face_system.db`), you'll need to migrate it manually or start fresh with PostgreSQL.

The old SQLite file is still there but **not used anymore**. The system now uses PostgreSQL exclusively.

---

## Quick Commands

```bash
# Create database
./create_postgres_db.sh

# Install driver
pip install psycopg2-binary

# Start backend
./run_backend.sh

# View database
psql -U postgres -d face_system
```

---

**Status:** ✅ System converted to PostgreSQL  
**Next:** Follow steps above to complete setup

