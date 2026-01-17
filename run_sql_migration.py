"""
Run SQL migration to rename hunter_payload to snov_payload
No PostgreSQL installation needed - uses Python psycopg2
"""
import os
import sys

# Database connection string
DATABASE_URL = "postgresql://art_outreach:SxFYWnrwhu8WmSjq6IR9iMdk3qFuts8S@dpg-d4lcklbe5dus73fn1rh0-a.oregon-postgres.render.com/art_outreach"

try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print("Installing psycopg2...")
    os.system(f"{sys.executable} -m pip install psycopg2-binary --quiet")
    import psycopg2
    from psycopg2 import sql

def run_migration():
    """Run the SQL migration"""
    print("🔌 Connecting to database...")
    
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True  # Enable autocommit for DDL statements
        cur = conn.cursor()
        
        print("✅ Connected successfully!")
        
        # Check if column exists
        print("\n🔍 Checking if hunter_payload column exists...")
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'prospects' 
            AND column_name = 'hunter_payload';
        """)
        
        if cur.fetchone():
            print("✅ Found hunter_payload column")
            
            # Check if snov_payload already exists
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'prospects' 
                AND column_name = 'snov_payload';
            """)
            
            if cur.fetchone():
                print("⚠️  snov_payload already exists! Column may have already been renamed.")
                response = input("Do you want to continue anyway? (y/n): ")
                if response.lower() != 'y':
                    print("❌ Migration cancelled")
                    return
            
            # Run migration
            print("\n[RUNNING] Running migration: hunter_payload -> snov_payload")
            cur.execute("ALTER TABLE prospects RENAME COLUMN hunter_payload TO snov_payload;")
            print("✅ Migration completed successfully!")
            
        else:
            print("⚠️  hunter_payload column not found")
            
            # Check if snov_payload exists
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'prospects' 
                AND column_name = 'snov_payload';
            """)
            
            if cur.fetchone():
                print("✅ snov_payload already exists - migration may have already been run")
            else:
                print("❌ Neither hunter_payload nor snov_payload found")
                print("   The prospects table may not exist yet, or column names are different")
        
        # Verify
        print("\n🔍 Verifying migration...")
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'prospects' 
            AND column_name IN ('hunter_payload', 'snov_payload')
            ORDER BY column_name;
        """)
        
        results = cur.fetchall()
        if results:
            print("\n📊 Current columns:")
            for col_name, col_type in results:
                print(f"   - {col_name} ({col_type})")
        else:
            print("⚠️  No payload columns found")
        
        # Check for data
        print("\n📊 Checking for existing data...")
        cur.execute("SELECT COUNT(*) FROM prospects;")
        total = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM prospects WHERE snov_payload IS NOT NULL;")
        with_data = cur.fetchone()[0]
        
        print(f"   Total prospects: {total}")
        print(f"   Prospects with snov_payload data: {with_data}")
        
        cur.close()
        conn.close()
        
        print("\n✅ Migration verification complete!")
        
    except psycopg2.OperationalError as e:
        print(f"❌ Connection error: {e}")
        print("\nPlease check:")
        print("   - Database URL is correct")
        print("   - Database is accessible from your network")
        print("   - IP restrictions allow your connection")
        sys.exit(1)
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 60)
    print("SQL Migration: hunter_payload -> snov_payload")
    print("=" * 60)
    print()
    
    run_migration()
    
    print("\n" + "=" * 60)
    print("✅ Done!")
    print("=" * 60)

