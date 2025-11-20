# PostgreSQL Authentication Fix

## Issue
PostgreSQL is using **peer authentication** which requires the system user to match the database user, or you need to use `sudo -u postgres`.

## Solutions

### Option 1: Use sudo (Easiest for viewing)

```bash
# View database
sudo -u postgres psql -d face_system

# Or run Python script as postgres user
sudo -u postgres python view_database_postgres.py
```

### Option 2: Set PostgreSQL Password

**Set password for postgres user:**
```bash
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'your_password';"
```

**Then set environment variable:**
```bash
export POSTGRES_PASSWORD=your_password
```

**Or edit `backend/config.py`:**
```python
POSTGRES_PASSWORD = "your_password"
```

### Option 3: Create Database User Matching Your System User

```bash
# Get your username
whoami

# Create PostgreSQL user with same name
sudo -u postgres createuser -s $(whoami)

# Update config to use your username
export POSTGRES_USER=$(whoami)
```

### Option 4: Configure PostgreSQL for Password Authentication

Edit PostgreSQL config:
```bash
sudo nano /etc/postgresql/16/main/pg_hba.conf
```

Change this line:
```
local   all             all                                     peer
```

To:
```
local   all             all                                     md5
```

Then restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

---

## Quick Fix (Recommended)

**For now, use sudo for database access:**

```bash
# View database
sudo -u postgres psql -d face_system -c "\dt"

# The backend API should work fine as it uses SQLAlchemy
# which handles authentication differently
```

**The backend API will work because SQLAlchemy handles the connection properly.**

---

## Test Backend Connection

```bash
# Start backend
./run_backend.sh

# It should connect successfully and create tables
```

If backend fails, set a password:
```bash
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"
export POSTGRES_PASSWORD=postgres
```

