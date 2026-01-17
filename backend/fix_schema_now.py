#!/usr/bin/env python3
"""
Emergency schema fix script - adds missing social columns to prospects table.

This script:
1. Connects to the exact database the app uses
2. Checks current schema
3. Adds missing columns if needed
4. Verifies the fix

Run: python fix_schema_now.py
"""
import os
import sys
import asyncio
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Get database URL from environment (same as app uses)
database_url = os.getenv("DATABASE_URL")
if not database_url:
    print("❌ ERROR: DATABASE_URL environment variable not set")
    sys.exit(1)

print("=" * 80)
print("🔍 STEP 1: Identifying Database Connection")
print("=" * 80)
print(f"📊 Database URL: {database_url[:50]}...")  # Don't print full URL with password

# Convert asyncpg URL to sync for schema inspection
sync_url = database_url
if database_url.startswith("postgresql+asyncpg://"):
    sync_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    print("✅ Converted asyncpg URL to sync format for schema operations")

# Create sync engine for schema operations
sync_engine = create_engine(sync_url, pool_pre_ping=True)

print("\n" + "=" * 80)
print("🔍 STEP 2: Inspecting Live Database Schema")
print("=" * 80)

with sync_engine.connect() as conn:
    # Get database name and host
    db_info = conn.execute(text("SELECT current_database(), inet_server_addr(), inet_server_port()")).fetchone()
    db_name = db_info[0]
    db_host = db_info[1] or "localhost"
    db_port = db_info[2] or "5432"
    
    print(f"✅ Database Name: {db_name}")
    print(f"✅ Database Host: {db_host}:{db_port}")
    print(f"✅ Schema: public (default)")
    
    # Get current columns
    columns_result = conn.execute(text("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'prospects'
        ORDER BY ordinal_position
    """))
    
    existing_columns = {}
    for row in columns_result:
        existing_columns[row[0]] = {
            'type': row[1],
            'nullable': row[2] == 'YES',
            'default': row[3]
        }
    
    print(f"\n📋 Current prospects table has {len(existing_columns)} columns")
    
    # Check for required social columns
    required_columns = {
        'source_type': 'VARCHAR',
        'source_platform': 'VARCHAR',
        'profile_url': 'TEXT',
        'username': 'VARCHAR',
        'display_name': 'VARCHAR',
        'follower_count': 'INTEGER',
        'engagement_rate': 'NUMERIC'
    }
    
    missing_columns = []
    for col_name, col_type in required_columns.items():
        if col_name not in existing_columns:
            missing_columns.append((col_name, col_type))
            print(f"❌ MISSING: {col_name} ({col_type})")
        else:
            print(f"✅ EXISTS: {col_name} ({existing_columns[col_name]['type']})")
    
    if not missing_columns:
        print("\n✅ All required columns already exist. No fix needed.")
        sys.exit(0)
    
    print(f"\n⚠️  Found {len(missing_columns)} missing columns")
    print("=" * 80)
    print("🔧 STEP 3: Applying Schema Fix")
    print("=" * 80)
    
    # Build ALTER TABLE statement
    alter_statements = []
    for col_name, col_type in missing_columns:
        if col_type == 'NUMERIC':
            # engagement_rate needs precision
            alter_statements.append(f"ADD COLUMN {col_name} NUMERIC(5, 2)")
        elif col_type == 'VARCHAR':
            alter_statements.append(f"ADD COLUMN {col_name} VARCHAR")
        elif col_type == 'TEXT':
            alter_statements.append(f"ADD COLUMN {col_name} TEXT")
        elif col_type == 'INTEGER':
            alter_statements.append(f"ADD COLUMN {col_name} INTEGER")
    
    alter_sql = f"ALTER TABLE prospects {', '.join(alter_statements)}"
    
    print(f"📝 SQL to execute:")
    print(f"   {alter_sql}")
    print()
    
    try:
        # Execute in a transaction
        with conn.begin():
            conn.execute(text(alter_sql))
        print("✅ Schema fix applied successfully")
    except Exception as e:
        print(f"❌ ERROR applying schema fix: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)
    
    print("=" * 80)
    print("✅ STEP 4: Immediate Verification")
    print("=" * 80)
    
    # Verify columns exist
    verify_result = conn.execute(text("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'prospects'
        AND column_name IN ('source_type', 'source_platform', 'profile_url', 'username', 'display_name', 'follower_count', 'engagement_rate')
        ORDER BY column_name
    """))
    
    verified_columns = {row[0]: row[1] for row in verify_result}
    
    all_present = True
    for col_name in required_columns.keys():
        if col_name in verified_columns:
            print(f"✅ VERIFIED: {col_name} ({verified_columns[col_name]})")
        else:
            print(f"❌ MISSING: {col_name} (verification failed)")
            all_present = False
    
    if not all_present:
        print("\n❌ Verification failed - columns still missing")
        sys.exit(1)
    
    # Test SELECT query
    try:
        test_result = conn.execute(text("SELECT source_type, source_platform FROM prospects LIMIT 1"))
        row = test_result.fetchone()
        print(f"\n✅ SELECT query succeeded (returned {1 if row else 0} row(s))")
    except Exception as e:
        print(f"\n❌ SELECT query failed: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 80)
    print("✅ SCHEMA FIX COMPLETE")
    print("=" * 80)
    print(f"✅ Database: {db_name} on {db_host}:{db_port}")
    print(f"✅ Added {len(missing_columns)} columns to prospects table")
    print(f"✅ All columns verified")
    print(f"✅ SELECT query test passed")
    print("\n📝 Next steps:")
    print("   1. Restart the backend server")
    print("   2. Test GET /api/prospects (should not return UndefinedColumnError)")
    print("   3. Run a discovery job (should save prospects successfully)")
    print("=" * 80)

