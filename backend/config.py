# backend/config.py
"""
Configuration for Backend API
"""
import os
from pathlib import Path

# Database Configuration
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "postgresql")  # postgresql (default), mysql

# PostgreSQL Configuration (default)
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "face_system")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")  # Default password

# SQLite Configuration (deprecated - not used)
# SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "data/database/face_system.db")

# MySQL Configuration
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB = os.getenv("MYSQL_DB", "face_system")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_DEBUG = os.getenv("API_DEBUG", "False").lower() == "true"

# File Storage
UPLOAD_BASE_DIR = Path(os.getenv("UPLOAD_BASE_DIR", "data/uploads"))

# Create directories if they don't exist
UPLOAD_BASE_DIR.mkdir(parents=True, exist_ok=True)

