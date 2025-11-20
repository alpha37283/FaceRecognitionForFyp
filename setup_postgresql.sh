#!/bin/bash

# PostgreSQL Database Setup Script

echo "=========================================="
echo "  🐘 PostgreSQL Database Setup"
echo "=========================================="
echo ""

# Check if running as root or with sudo
if [ "$EUID" -eq 0 ]; then
    SUDO=""
else
    SUDO="sudo"
fi

# Database configuration
DB_NAME="face_system"
DB_USER="postgres"

echo "[INFO] Creating database: $DB_NAME"
echo "[INFO] Using user: $DB_USER"
echo ""

# Create database
$SUDO -u postgres psql <<EOF
-- Check if database exists
SELECT 1 FROM pg_database WHERE datname = '$DB_NAME' \gexec

-- Create database if it doesn't exist
CREATE DATABASE $DB_NAME;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- List databases
\l
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Database '$DB_NAME' created successfully!"
    echo ""
    echo "[INFO] Database connection details:"
    echo "  Host: localhost"
    echo "  Port: 5432"
    echo "  Database: $DB_NAME"
    echo "  User: $DB_USER"
    echo ""
    echo "[INFO] Next steps:"
    echo "  1. Install Python driver: pip install psycopg2-binary"
    echo "  2. Start backend: ./run_backend.sh"
    echo "  3. Tables will be created automatically"
else
    echo ""
    echo "[-] Error creating database"
    echo "[INFO] Database might already exist (this is OK)"
fi

echo "=========================================="

