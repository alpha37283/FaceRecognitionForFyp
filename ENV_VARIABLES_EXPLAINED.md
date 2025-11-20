# Environment Variables Explained

## How `os.getenv()` Works

`os.getenv("VARIABLE_NAME", "default_value")` reads from **system environment variables**, not from a file.

### Example:
```python
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
```

This means:
1. **First**: Check if environment variable `POSTGRES_PASSWORD` exists
2. **If exists**: Use that value
3. **If not exists**: Use default value `"postgres"`

---

## Ways to Set Environment Variables

### Option 1: Set in Current Terminal Session (Temporary)

```bash
export POSTGRES_PASSWORD=postgres
```

**Note:** This only works for the current terminal session. When you close the terminal, it's gone.

### Option 2: Set in Config File (Permanent - What We Did)

Edit `backend/config.py`:
```python
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
```

This means:
- If you set `export POSTGRES_PASSWORD=something`, it uses that
- Otherwise, it defaults to `"postgres"`

### Option 3: Create `.env` File (Advanced)

If you want to use a `.env` file, you need to install `python-dotenv`:

```bash
pip install python-dotenv
```

Then in `backend/config.py`:
```python
from dotenv import load_dotenv
load_dotenv()  # Loads .env file

POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
```

Create `.env` file:
```
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
```

---

## Current Setup (What We Have Now)

**In `backend/config.py`:**
```python
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
```

This means:
- ✅ **Default password is "postgres"** (what you set)
- ✅ Works without setting environment variable
- ✅ You can override by setting `export POSTGRES_PASSWORD=other_password`

---

## Summary

**No `.env` file needed!** The config file has the default password hardcoded now.

The system will use:
- `POSTGRES_PASSWORD = "postgres"` (default)
- Unless you set `export POSTGRES_PASSWORD=something` in terminal

---

## Test It

```bash
# Start backend (will use password "postgres" from config)
./run_backend.sh
```

It should connect successfully now!

