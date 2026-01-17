#!/usr/bin/env python3
"""
Quick script to add discovery_query_id column if missing.
Run this from Render Shell: python add_discovery_query_id.py
"""
import os
import sys
from sqlalchemy import create_engine, text

# Get database URL from environment
database_url = os.getenv("DATABASE_URL")
if not database_url:
    print("❌ DATABASE_URL not set")
    sys.exit(1)

# Convert asyncpg URL to psycopg2 for sync operations
if database_url.startswith("postgresql+asyncpg://"):
    sync_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    # Remove pgbouncer parameter if present
    if "?" in sync_url:
        base_url, query_string = sync_url.split("?", 1)
        query_params = [p for p in query_string.split("&") 
                      if not p.lower().startswith("pgbouncer=")]
        sync_url = f"{base_url}?{'&'.join(query_params)}" if query_params else base_url
else:
    sync_url = database_url

print(f"🔗 Connecting to database...")
engine = create_engine(sync_url)

try:
    with engine.connect() as conn:
        # Check if column exists
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'prospects' 
            AND column_name = 'discovery_query_id'
            AND table_schema = 'public'
        """))
        
        if result.fetchone():
            print("✅ Column discovery_query_id already exists")
        else:
            print("⚠️  Column discovery_query_id missing - adding it...")
            
            # Add column
            conn.execute(text("""
                ALTER TABLE prospects 
                ADD COLUMN discovery_query_id UUID
            """))
            
            # Create index
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_prospects_discovery_query_id 
                ON prospects(discovery_query_id)
            """))
            
            conn.commit()
            print("✅ Successfully added discovery_query_id column and index")
        
        # Verify
        result = conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'prospects' 
            AND column_name = 'discovery_query_id'
            AND table_schema = 'public'
        """))
        row = result.fetchone()
        if row:
            print(f"✅ Verification: Column exists with type {row[1]}")
        else:
            print("❌ Verification failed - column still missing")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("✅ Done!")

