#!/usr/bin/env python3
"""
Emergency script to apply the final_body migration immediately.
Run this if migrations aren't running automatically on startup.
"""
import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL
database_url = os.getenv("DATABASE_URL")
if not database_url:
    print("❌ DATABASE_URL not set!")
    sys.exit(1)

# Convert asyncpg URL to psycopg2 for direct connection
if database_url.startswith("postgresql+asyncpg://"):
    database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
elif database_url.startswith("postgresql://"):
    pass  # Already correct
else:
    print(f"❌ Unknown database URL format: {database_url}")
    sys.exit(1)

print(f"📊 Connecting to database...")
engine = create_engine(database_url)

with engine.connect() as conn:
    print("🔍 Checking for missing columns...")
    
    # Check final_body
    result = conn.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'prospects' 
        AND column_name = 'final_body'
    """))
    if not result.fetchone():
        print("⚠️  Adding final_body column...")
        conn.execute(text("ALTER TABLE prospects ADD COLUMN final_body TEXT"))
        conn.commit()
        print("✅ Added final_body column")
    else:
        print("✅ final_body column already exists")
    
    # Check thread_id
    result = conn.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'prospects' 
        AND column_name = 'thread_id'
    """))
    if not result.fetchone():
        print("⚠️  Adding thread_id column...")
        conn.execute(text("ALTER TABLE prospects ADD COLUMN thread_id UUID"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_prospects_thread_id ON prospects(thread_id)"))
        conn.commit()
        print("✅ Added thread_id column with index")
    else:
        print("✅ thread_id column already exists")
    
    # Check sequence_index
    result = conn.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'prospects' 
        AND column_name = 'sequence_index'
    """))
    if not result.fetchone():
        print("⚠️  Adding sequence_index column...")
        conn.execute(text("ALTER TABLE prospects ADD COLUMN sequence_index INTEGER"))
        conn.execute(text("UPDATE prospects SET sequence_index = 0 WHERE sequence_index IS NULL"))
        conn.execute(text("ALTER TABLE prospects ALTER COLUMN sequence_index SET NOT NULL"))
        conn.execute(text("ALTER TABLE prospects ALTER COLUMN sequence_index SET DEFAULT 0"))
        conn.commit()
        print("✅ Added sequence_index column")
    else:
        print("✅ sequence_index column already exists")
    
    print("\n✅ All columns verified/added!")
    print("🔄 Now restart the backend to uncomment final_body in the model.")

