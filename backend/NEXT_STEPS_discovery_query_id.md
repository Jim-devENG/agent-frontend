# Next Steps: discovery_query_id Migration

## Current Status

✅ **Migration scripts created:**
- Alembic migration: `alembic/versions/556b79de2825_add_discovery_query_id_to_prospects_safe.py`
- SQL script: `add_discovery_query_id_column.sql`
- Migration guide: `MIGRATION_GUIDE_discovery_query_id.md`

✅ **Code already using it:**
- `backend/app/tasks/discovery.py` (line 376) - ✅ Sets `discovery_query_id`

⚠️ **Code that needs updating:**
- `worker/tasks/discovery.py` (line 133) - ❌ Doesn't set `discovery_query_id`

## Step 1: Run the Migration

### Option A: Using SQL Script (Recommended - Bypasses Alembic issues)

```bash
# Connect to your database and run the SQL script
psql -h your_host -U your_user -d your_database -f backend/add_discovery_query_id_column.sql
```

Or if using environment variables:
```bash
psql $DATABASE_URL -f backend/add_discovery_query_id_column.sql
```

### Option B: Fix Alembic and Run Migration

There's a syntax error in `alembic/env.py`. You can either:
1. Use the SQL script (Option A) - recommended
2. Or fix the Alembic async issue and run: `alembic upgrade head`

## Step 2: Verify Migration Worked

Run these queries to verify:

```sql
-- Check column exists
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'prospects' 
AND column_name = 'discovery_query_id';

-- Check index exists
SELECT indexname FROM pg_indexes 
WHERE tablename = 'prospects' 
AND indexname = 'ix_prospects_discovery_query_id';

-- Check foreign key exists
SELECT constraint_name 
FROM information_schema.table_constraints 
WHERE table_name = 'prospects' 
AND constraint_name = 'fk_prospects_discovery_query_id';
```

## Step 3: Update Worker Code

The worker code in `worker/tasks/discovery.py` needs to be updated to also set `discovery_query_id` when creating prospects. However, the worker code doesn't seem to have access to `discovery_query` objects.

**Decision needed:** 
- Does the worker need to track discovery queries?
- Or should we only set it in the backend task?

## Step 4: Test the Integration

After migration, test that:
1. New prospects created during discovery jobs have `discovery_query_id` set
2. Queries joining prospects with discovery_queries work
3. Existing queries still work (column is nullable)

## Quick Commands

```bash
# 1. Run migration (SQL)
psql $DATABASE_URL -f backend/add_discovery_query_id_column.sql

# 2. Verify in Python
python -c "
from app.db.database import engine
from sqlalchemy import inspect
inspector = inspect(engine)
cols = [c['name'] for c in inspector.get_columns('prospects')]
print('discovery_query_id' in cols)
"

# 3. Test query
psql $DATABASE_URL -c "
SELECT COUNT(*) as total, 
       COUNT(discovery_query_id) as with_query_id 
FROM prospects;
"
```

## What's Already Working

✅ Backend discovery task (`backend/app/tasks/discovery.py`) already sets `discovery_query_id` when creating prospects
✅ Model definition includes the column
✅ Relationship is defined in SQLAlchemy

## What Needs Attention

⚠️ Migration needs to be run (column doesn't exist in database yet)
⚠️ Worker code doesn't set `discovery_query_id` (may be intentional if worker doesn't track queries)

