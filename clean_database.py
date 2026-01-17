"""
Clean Database Script - Remove all fake/test data and start fresh
This will delete all prospects, jobs, email logs, discovery queries, and scraper history
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

def get_table_counts(cur):
    """Get row counts for all tables"""
    tables = [
        'prospects',
        'jobs',
        'email_logs',
        'discovery_queries',
        'scraper_history',
        'settings'
    ]
    
    counts = {}
    for table in tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table};")
            counts[table] = cur.fetchone()[0]
        except Exception:
            counts[table] = 0
    
    return counts

def clean_database():
    """Clean all data from the database"""
    print("=" * 60)
    print("Database Cleanup Script")
    print("=" * 60)
    print()
    print("⚠️  WARNING: This will DELETE ALL DATA from:")
    print("   - prospects (websites and emails)")
    print("   - jobs (all job history)")
    print("   - email_logs (all email sending history)")
    print("   - discovery_queries (all search queries)")
    print("   - scraper_history (all scraper runs)")
    print()
    print("✅ Will KEEP:")
    print("   - settings (your configuration)")
    print("   - Table structure (tables will remain)")
    print()
    
    # Confirmation
    response = input("Type 'DELETE ALL DATA' to confirm: ")
    if response != "DELETE ALL DATA":
        print("❌ Cancelled. Nothing was deleted.")
        return
    
    print()
    print("🔌 Connecting to database...")
    
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cur = conn.cursor()
        
        print("✅ Connected successfully!")
        print()
        
        # Show current counts
        print("📊 Current data counts:")
        counts_before = get_table_counts(cur)
        for table, count in counts_before.items():
            print(f"   {table}: {count:,} rows")
        print()
        
        # Delete data from each table (in correct order due to foreign keys)
        print("🗑️  Deleting data...")
        
        # Delete in order to respect foreign key constraints
        tables_to_clean = [
            ('email_logs', 'Email logs'),
            ('prospects', 'Prospects'),
            ('discovery_queries', 'Discovery queries'),
            ('jobs', 'Jobs'),
            ('scraper_history', 'Scraper history'),
        ]
        
        for table, name in tables_to_clean:
            try:
                cur.execute(f"DELETE FROM {table};")
                deleted = cur.rowcount
                print(f"   ✅ {name}: Deleted {deleted:,} rows")
            except Exception as e:
                print(f"   ⚠️  {name}: Error - {e}")
        
        print()
        
        # Show new counts
        print("📊 New data counts:")
        counts_after = get_table_counts(cur)
        for table, count in counts_after.items():
            before = counts_before.get(table, 0)
            after = count
            if before > 0:
                print(f"   {table}: {before:,} → {after:,} rows")
            else:
                print(f"   {table}: {after:,} rows")
        
        # Verify cleanup
        total_deleted = sum(counts_before.values()) - sum(counts_after.values())
        print()
        print(f"✅ Cleanup complete! Deleted {total_deleted:,} total rows")
        print()
        print("🎉 Database is now clean and ready for fresh data with Snov.io!")
        
        cur.close()
        conn.close()
        
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
    clean_database()
    
    print()
    print("=" * 60)
    print("✅ Done!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Run a new discovery job to find fresh websites")
    print("2. The new data will use Snov.io for email enrichment")
    print("3. All data will be clean and real!")

