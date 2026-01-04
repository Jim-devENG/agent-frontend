# Schema Fix Execution Plan

## Root Cause
The `prospects` table is missing 7 social outreach columns that the SQLAlchemy model expects:
- `source_type`
- `source_platform`
- `profile_url`
- `username`
- `display_name`
- `follower_count`
- `engagement_rate`

This causes `UndefinedColumnError` on any SELECT query against `prospects`.

## STEP 1: Identify Database Connection

**Database URL Source**: `backend/app/db/database.py` reads from `DATABASE_URL` environment variable.

**To confirm the exact database**, the app logs this on startup (see `backend/app/main.py` lines 285-293):
```python
SELECT current_database(), inet_server_addr()
```

**Expected Output**:
- Database name: (from Render or local)
- Host: Render PostgreSQL host or localhost

## STEP 2: Inspect Live Schema

**Method 1: Run the fix script** (recommended)
```bash
cd backend
python fix_schema_now.py
```

The script will:
1. Connect to the database using `DATABASE_URL`
2. Query `SELECT current_database(), inet_server_addr()`
3. List all columns in `prospects` table
4. Identify missing columns
5. Apply the fix
6. Verify immediately

**Method 2: Manual SQL** (if script fails)
```sql
-- Connect to the database first, then run:
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'prospects'
ORDER BY ordinal_position;
```

## STEP 3: Apply Schema Fix

**Method 1: Automated Script** (safest)
```bash
cd backend
python fix_schema_now.py
```

**Method 2: Direct SQL** (if script unavailable)
```sql
ALTER TABLE prospects
ADD COLUMN source_type VARCHAR,
ADD COLUMN source_platform VARCHAR,
ADD COLUMN profile_url TEXT,
ADD COLUMN username VARCHAR,
ADD COLUMN display_name VARCHAR,
ADD COLUMN follower_count INTEGER,
ADD COLUMN engagement_rate NUMERIC(5, 2);
```

**Rules Applied**:
- ✅ No defaults (columns are nullable)
- ✅ No NOT NULL constraints
- ✅ No drops or renames
- ✅ No backfills
- ✅ Additive only

## STEP 4: Immediate Verification

**The script automatically verifies**, or run manually:
```sql
-- Verify columns exist
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'prospects'
AND column_name IN ('source_type', 'source_platform', 'profile_url', 'username', 'display_name', 'follower_count', 'engagement_rate')
ORDER BY column_name;

-- Test SELECT query
SELECT source_type, source_platform
FROM prospects
LIMIT 1;
```

**Expected Result**: Query succeeds (returns 0 or more rows, no error)

## STEP 5: Runtime Confirmation

**After schema fix**:

1. **Restart backend server** (if running)
   - Migrations will run automatically on startup
   - Check logs for: `✅ All social columns verified`

2. **Test GET /api/prospects**
   ```bash
   curl https://agent-liquidcanvas.onrender.com/api/prospects?skip=0&limit=10
   ```
   **Expected**: Returns 200 OK with data or empty list (no `UndefinedColumnError`)

3. **Run discovery job**
   - Submit a discovery request
   - Check job results
   **Expected**: `prospects_saved > 0` (not 0)

## Failure Conditions

**If `source_type` still missing after fix**:
- Database connection is wrong (different database than app uses)
- Schema fix was applied to wrong database
- Permissions issue (user can't ALTER TABLE)
- Transaction rolled back

**Evidence needed**:
- Database name from `SELECT current_database()`
- Host from `SELECT inet_server_addr()`
- Column list from `information_schema.columns`
- Error message from ALTER TABLE (if any)

## Output Format

After running `fix_schema_now.py`, you'll see:

```
================================================================================
🔍 STEP 1: Identifying Database Connection
================================================================================
📊 Database URL: postgresql://user:****@host:port/dbname...
✅ Converted asyncpg URL to sync format for schema operations

================================================================================
🔍 STEP 2: Inspecting Live Database Schema
================================================================================
✅ Database Name: [database_name]
✅ Database Host: [host]:[port]
✅ Schema: public (default)

📋 Current prospects table has [N] columns
❌ MISSING: source_type (VARCHAR)
❌ MISSING: source_platform (VARCHAR)
...

================================================================================
🔧 STEP 3: Applying Schema Fix
================================================================================
📝 SQL to execute:
   ALTER TABLE prospects ADD COLUMN source_type VARCHAR, ...
✅ Schema fix applied successfully

================================================================================
✅ STEP 4: Immediate Verification
================================================================================
✅ VERIFIED: source_type (character varying)
✅ VERIFIED: source_platform (character varying)
...
✅ SELECT query succeeded (returned 1 row(s))

================================================================================
✅ SCHEMA FIX COMPLETE
================================================================================
✅ Database: [name] on [host]:[port]
✅ Added 7 columns to prospects table
✅ All columns verified
✅ SELECT query test passed
```

## Next Steps After Fix

1. ✅ Restart backend (migrations run automatically)
2. ✅ Test `/api/prospects` endpoint
3. ✅ Run discovery job
4. ✅ Confirm `prospects_saved > 0`

