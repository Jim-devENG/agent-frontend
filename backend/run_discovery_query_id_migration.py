"""
Run migration to add discovery_query_id column to prospects table
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text, inspect
import os

# Try to load .env, but continue if it fails
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception as e:
    print(f"Note: Could not load .env file: {e}")
    print("Using environment variables directly...")

# Get database URL and convert to sync version
db_url = os.getenv('DATABASE_URL', 'postgresql://art_outreach:art_outreach@localhost:5432/art_outreach')
# Convert asyncpg URL to psycopg2 for sync operations
if db_url.startswith('postgresql+asyncpg://'):
    db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
elif db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://')

print(f"Connecting to database...")
engine = create_engine(db_url)
conn = engine.connect()

try:
    # Check if column exists
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('prospects')]
    
    if 'discovery_query_id' in columns:
        print("✅ Column 'discovery_query_id' already exists!")
    else:
        print("Adding discovery_query_id column...")
        
        # Add column
        conn.execute(text("ALTER TABLE prospects ADD COLUMN discovery_query_id UUID"))
        conn.commit()
        print("✅ Added discovery_query_id column")
    
    # Check if index exists
    indexes = [idx['name'] for idx in inspector.get_indexes('prospects')]
    if 'ix_prospects_discovery_query_id' not in indexes:
        print("Creating index...")
        conn.execute(text("CREATE INDEX ix_prospects_discovery_query_id ON prospects(discovery_query_id)"))
        conn.commit()
        print("✅ Created index")
    else:
        print("✅ Index already exists")
    
    # Check if discovery_queries table exists and add foreign key
    tables = inspector.get_table_names()
    if 'discovery_queries' in tables:
        fk_constraints = [fk['name'] for fk in inspector.get_foreign_keys('prospects')]
        if 'fk_prospects_discovery_query_id' not in fk_constraints:
            print("Creating foreign key constraint...")
            conn.execute(text("""
                ALTER TABLE prospects
                ADD CONSTRAINT fk_prospects_discovery_query_id
                FOREIGN KEY (discovery_query_id)
                REFERENCES discovery_queries(id)
                ON DELETE SET NULL
            """))
            conn.commit()
            print("✅ Created foreign key constraint")
        else:
            print("✅ Foreign key constraint already exists")
    else:
        print("⚠️  discovery_queries table does not exist, skipping foreign key")
    
    # Verify
    print("\n✅ Migration complete! Verifying...")
    columns = [col['name'] for col in inspector.get_columns('prospects')]
    if 'discovery_query_id' in columns:
        col_info = next(col for col in inspector.get_columns('prospects') if col['name'] == 'discovery_query_id')
        print(f"   Column type: {col_info['type']}")
        print(f"   Nullable: {col_info['nullable']}")
    else:
        print("❌ Column not found after migration!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    conn.close()
    engine.dispose()

