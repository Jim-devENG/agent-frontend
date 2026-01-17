#!/bin/bash
# Standalone script to run migrations immediately
# Can be executed manually or via Render shell

set -e

echo "=========================================="
echo "🚀 Running database migrations NOW..."
echo "=========================================="

# Find alembic.ini
if [ -f "alembic.ini" ]; then
    ALEMBIC_DIR="."
elif [ -f "backend/alembic.ini" ]; then
    cd backend
    ALEMBIC_DIR="."
elif [ -f "/app/alembic.ini" ]; then
    cd /app
    ALEMBIC_DIR="."
elif [ -f "/app/backend/alembic.ini" ]; then
    cd /app/backend
    ALEMBIC_DIR="."
else
    echo "❌ ERROR: Could not find alembic.ini"
    echo "Current directory: $(pwd)"
    find . -name "alembic.ini" 2>/dev/null || echo "No alembic.ini found"
    exit 1
fi

echo "📁 Working directory: $(pwd)"
echo "📝 Executing: alembic upgrade head"

alembic upgrade head

echo "=========================================="
echo "✅ Migration completed!"
echo "=========================================="

