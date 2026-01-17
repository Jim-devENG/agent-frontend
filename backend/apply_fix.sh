#!/bin/bash
# Emergency fix for missing discovery_query_id column

if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL not set"
    exit 1
fi

echo "🔧 Applying emergency fix..."
psql "$DATABASE_URL" -f fix_discovery_query_id.sql

echo ""
echo "✅ Fix applied. Verifying..."
psql "$DATABASE_URL" -c "SELECT column_name FROM information_schema.columns WHERE table_name = 'prospects' AND column_name = 'discovery_query_id';"

