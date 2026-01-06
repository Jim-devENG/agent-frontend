"""
Utility script to fix alembic_version table.

This script:
1. Checks if alembic_version table exists
2. If multiple rows exist, keeps ONLY the latest revision
3. If table is missing or empty, inserts the latest revision hash manually
4. Ensures version_num = 'ensure_alembic_version_table' (or latest head)

Run this ONCE to fix corrupted Alembic history.
"""
import os
import sys
from sqlalchemy import create_engine, text
from alembic.script import ScriptDirectory
from alembic.config import Config

# Get database URL
database_url = os.getenv("DATABASE_URL")
if not database_url:
    print("❌ DATABASE_URL environment variable not set")
    sys.exit(1)

# Convert asyncpg URL to psycopg2 for sync operations
if database_url.startswith("postgresql+asyncpg://"):
    sync_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
elif database_url.startswith("postgresql://"):
    sync_url = database_url
else:
    sync_url = database_url.replace("postgres://", "postgresql://")

print(f"📊 Connecting to database...")
engine = create_engine(sync_url, pool_pre_ping=True)

try:
    with engine.connect() as conn:
        # Get latest head revision from Alembic
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        alembic_cfg = Config(os.path.join(backend_dir, "alembic.ini"))
        script = ScriptDirectory.from_config(alembic_cfg)
        heads = script.get_revision("heads")
        head_revision = heads.revision if heads else None
        
        if not head_revision:
            print("❌ Could not determine head revision from Alembic")
            sys.exit(1)
        
        print(f"📋 Latest head revision: {head_revision}")
        
        # Check if alembic_version table exists
        table_check = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'alembic_version'
            )
        """))
        table_exists = table_check.scalar()
        
        if not table_exists:
            print("⚠️  alembic_version table does not exist - creating it...")
            conn.execute(text("""
                CREATE TABLE alembic_version (
                    version_num VARCHAR(32) NOT NULL PRIMARY KEY
                )
            """))
            conn.commit()
            print("✅ Created alembic_version table")
        
        # Check current rows
        version_result = conn.execute(text("SELECT version_num FROM alembic_version"))
        versions = [row[0] for row in version_result.fetchall()]
        
        if len(versions) == 0:
            print("⚠️  alembic_version table is empty - inserting head revision...")
            conn.execute(text("INSERT INTO alembic_version (version_num) VALUES (:rev)"), {"rev": head_revision})
            conn.commit()
            print(f"✅ Inserted revision: {head_revision}")
        elif len(versions) > 1:
            print(f"⚠️  Multiple rows found in alembic_version: {versions}")
            print("⚠️  Removing all rows and inserting latest revision...")
            conn.execute(text("DELETE FROM alembic_version"))
            conn.execute(text("INSERT INTO alembic_version (version_num) VALUES (:rev)"), {"rev": head_revision})
            conn.commit()
            print(f"✅ Fixed: Now contains only revision: {head_revision}")
        elif versions[0] != head_revision:
            print(f"⚠️  Current revision ({versions[0]}) does not match head ({head_revision})")
            print("⚠️  Updating to head revision...")
            conn.execute(text("UPDATE alembic_version SET version_num = :rev"), {"rev": head_revision})
            conn.commit()
            print(f"✅ Updated to revision: {head_revision}")
        else:
            print(f"✅ alembic_version table is correct: {versions[0]}")
        
        # Verify
        verify_result = conn.execute(text("SELECT version_num FROM alembic_version"))
        final_version = verify_result.scalar()
        print("=" * 60)
        print(f"✅ FINAL STATE: alembic_version = '{final_version}'")
        print("=" * 60)
        
except Exception as e:
    print(f"❌ Error fixing alembic_version: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    engine.dispose()

print("✅ Done! Alembic version table is now fixed.")

