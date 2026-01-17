# Migration Application Guide - discovery_query_id Column

## Overview

This guide ensures the `discovery_query_id` column is safely added to the `prospects` table in production.

## Current Status

✅ **Model Definition**: `discovery_query_id` is defined in `backend/app/models/prospect.py` (line 31)
✅ **Migration Created**: `556b79de2825_add_discovery_query_id_to_prospects_safe.py` (idempotent)
✅ **Transaction Handling**: Fixed with `safe_commit()` and `safe_flush()` helpers

## Migration Chain

```
4b9608290b5d (settings table)
  ↓
add_discovery_query (discovery_queries table + discovery_query_id column)
  ↓
556b79de2825 (safe add discovery_query_id - idempotent)
```

## Verification Steps

### 1. Check Current Database State

```bash
# Connect to production database
psql $DATABASE_URL -c "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'prospects' AND column_name = 'discovery_query_id';"
```

**Expected Results:**
- **If column exists**: Returns row with `discovery_query_id | uuid`
- **If column missing**: Returns no rows

### 2. Check Alembic Migration Status

```bash
cd backend
alembic current
```

**Expected Output:**
- Shows current revision (should be `556b79de2825` or later if column exists)

### 3. Check Migration History

```bash
cd backend
alembic history
```

**Expected Chain:**
```
556b79de2825 -> add_discovery_query -> 4b9608290b5d -> <base>
```

## Applying Migration

### Option A: Automatic (Render Startup)

The backend automatically runs migrations on startup (see `backend/app/main.py` lines 131-164).

**Status**: ✅ Already configured

### Option B: Manual Application

If automatic migration fails, apply manually:

```bash
cd backend
alembic upgrade head
```

**Safety**: The migration is idempotent - safe to run multiple times.

## Migration Details

### Column Specification
- **Name**: `discovery_query_id`
- **Type**: `UUID` (PostgreSQL)
- **Nullable**: `True`
- **Default**: `None`
- **Foreign Key**: References `discovery_queries.id`
- **Index**: `ix_prospects_discovery_query_id`

### Idempotency

The migration checks for:
1. Column existence before adding
2. Index existence before creating
3. Foreign key existence before creating

**Result**: Safe to run multiple times without errors.

## Transaction Safety

All database operations now use:
- `safe_commit()` - Handles `PendingRollbackError` automatically
- `safe_flush()` - Handles transaction errors automatically

**Location**: `backend/app/db/transaction_helpers.py`

## Testing

### 1. Verify Column Exists

```sql
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'prospects' 
AND column_name = 'discovery_query_id';
```

### 2. Test Insert with discovery_query_id

```sql
-- Create a test discovery_query first
INSERT INTO discovery_queries (id, job_id, keyword, location, status)
VALUES (gen_random_uuid(), 'your-job-uuid', 'test', 'usa', 'pending')
RETURNING id;

-- Then test prospect insert (replace with actual UUIDs)
INSERT INTO prospects (id, domain, discovery_query_id, outreach_status)
VALUES (gen_random_uuid(), 'test.com', 'discovery-query-uuid-from-above', 'pending')
RETURNING id, domain, discovery_query_id;
```

### 3. Verify Foreign Key Works

```sql
-- Should fail if discovery_query_id doesn't exist in discovery_queries
INSERT INTO prospects (id, domain, discovery_query_id, outreach_status)
VALUES (gen_random_uuid(), 'test2.com', '00000000-0000-0000-0000-000000000000', 'pending');
-- Expected: Foreign key violation error (proves FK is working)
```

## Rollback (If Needed)

```bash
cd backend
alembic downgrade -1
```

**Note**: Only rollback if absolutely necessary. The column is nullable and safe to keep.

## Production Deployment Checklist

- [ ] Verify current database state (column may already exist)
- [ ] Check Alembic current revision
- [ ] Review migration file: `556b79de2825_add_discovery_query_id_to_prospects_safe.py`
- [ ] Deploy backend code (migrations run automatically on startup)
- [ ] Verify column exists after deployment
- [ ] Test discovery job to ensure column is populated
- [ ] Monitor logs for transaction errors (should be none)

## Troubleshooting

### Issue: "Column already exists" error

**Solution**: Migration is idempotent - this shouldn't happen. If it does, the migration will skip adding the column.

### Issue: PendingRollbackError

**Solution**: Fixed in code with `safe_commit()`. If still occurring, check:
1. All `await db.commit()` calls use `safe_commit()`
2. All `await db.flush()` calls use `safe_flush()`

### Issue: Migration not running on Render

**Solution**: Check `backend/app/main.py` startup event. Migrations run automatically.

## Files Modified

1. ✅ `backend/app/models/prospect.py` - Column defined (no changes needed)
2. ✅ `backend/alembic/versions/add_discovery_query_table.py` - Made idempotent
3. ✅ `backend/alembic/versions/556b79de2825_add_discovery_query_id_to_prospects_safe.py` - Already idempotent
4. ✅ `backend/app/db/transaction_helpers.py` - NEW: Safe transaction helpers
5. ✅ `backend/app/tasks/discovery.py` - Uses safe transaction helpers, defensive enrichment guards

