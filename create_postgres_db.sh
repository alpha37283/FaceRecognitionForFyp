#!/bin/bash

# Create PostgreSQL database for face_system

echo "=========================================="
echo "  Creating PostgreSQL Database"
echo "=========================================="
echo ""

sudo -u postgres psql <<EOF
-- Create database if it doesn't exist
SELECT 'CREATE DATABASE face_system'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'face_system')\gexec

-- Verify creation
\l face_system
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Database 'face_system' created successfully!"
    echo ""
    echo "[INFO] Database details:"
    echo "  Database: face_system"
    echo "  User: postgres"
    echo "  Host: localhost"
    echo "  Port: 5432"
else
    echo ""
    echo "[-] Error or database already exists"
fi

echo "=========================================="

