#!/bin/bash
# Complete Database Reset Script
# WARNING: This will DELETE ALL DATA

set -e

echo "⚠️  WARNING: This script will DELETE ALL DATA from the database!"
echo "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
sleep 5

# Get database URL from environment
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL environment variable is not set"
    exit 1
fi

echo "📊 Current database state:"
psql "$DATABASE_URL" -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE' ORDER BY table_name;"

echo ""
echo "🗑️  Dropping all tables..."
psql "$DATABASE_URL" -c "DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public;"

echo ""
echo "🔄 Running migrations from scratch..."
cd "$(dirname "$0")" || exit 1
alembic upgrade head

echo ""
echo "✅ Database reset complete!"
echo ""
echo "📊 New database state:"
psql "$DATABASE_URL" -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE' ORDER BY table_name;"

echo ""
echo "🔍 Verifying migration version:"
psql "$DATABASE_URL" -c "SELECT * FROM alembic_version;"

echo ""
echo "✅ Reset complete! All tables created successfully."

