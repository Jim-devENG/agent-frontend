#!/bin/bash
# Prestart script for Render deployment
# Runs database migrations before the application starts
# Render automatically executes this script before starting the app

set -e  # Exit on any error - if migrations fail, deployment fails

echo "=========================================="
echo "🚀 Running database migrations..."
echo "=========================================="

# Get current directory
CURRENT_DIR=$(pwd)
echo "📁 Current directory: $CURRENT_DIR"

# Try to find alembic.ini in common locations
if [ -f "alembic.ini" ]; then
    echo "✅ Found alembic.ini in current directory"
    ALEMBIC_DIR="."
elif [ -f "backend/alembic.ini" ]; then
    echo "✅ Found alembic.ini in backend/ directory"
    cd backend
    ALEMBIC_DIR="."
elif [ -f "/app/alembic.ini" ]; then
    echo "✅ Found alembic.ini in /app"
    cd /app
    ALEMBIC_DIR="."
elif [ -f "/app/backend/alembic.ini" ]; then
    echo "✅ Found alembic.ini in /app/backend"
    cd /app/backend
    ALEMBIC_DIR="."
else
    echo "❌ ERROR: Could not find alembic.ini"
    echo "Current directory: $(pwd)"
    echo "Listing files:"
    ls -la
    echo "Trying to find alembic.ini:"
    find . -name "alembic.ini" 2>/dev/null || echo "No alembic.ini found"
    exit 1
fi

echo "📁 Working directory: $(pwd)"
echo "📝 Executing: alembic upgrade head"

# Run migrations with explicit error handling
if alembic upgrade head; then
    echo "=========================================="
    echo "✅ Database migrations completed successfully"
    echo "=========================================="
else
    echo "=========================================="
    echo "❌ Database migrations failed"
    echo "=========================================="
    exit 1
fi
