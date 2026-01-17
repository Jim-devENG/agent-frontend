# IMMEDIATE FIX: Restore Data Visibility

## Problem
- Pipeline status shows: 100+ websites, 83 emails (31 + 52)
- But UI tabs are empty (Websites, Leads, Scraped Emails)
- Root cause: `final_body` column doesn't exist, causing all SELECT queries to fail

## Solution Applied
1. ✅ Commented out `final_body` in ORM model (prevents SELECT errors)
2. ✅ Added automatic column creation on startup (will add columns on restart)
3. ✅ Added error handling to return empty arrays instead of 500 errors
4. ✅ Created migration to add columns properly

## IMMEDIATE ACTION REQUIRED

### Option 1: Restart Backend (RECOMMENDED)
**The backend will automatically add the missing columns on startup.**

1. Restart the backend server
2. Check logs for:
   - "✅ Manually added missing columns (final_body, thread_id, sequence_index)"
   - OR "✅ final_body column exists - schema is correct"
3. After restart, tabs should populate automatically

### Option 2: Manual SQL (If restart doesn't work)
Run these SQL commands directly on your database:

```sql
-- Add final_body column
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS final_body TEXT;

-- Add thread_id column
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS thread_id UUID;
CREATE INDEX IF NOT EXISTS ix_prospects_thread_id ON prospects(thread_id);

-- Add sequence_index column
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS sequence_index INTEGER;
UPDATE prospects SET sequence_index = 0 WHERE sequence_index IS NULL;
ALTER TABLE prospects ALTER COLUMN sequence_index SET NOT NULL;
ALTER TABLE prospects ALTER COLUMN sequence_index SET DEFAULT 0;
```

### Option 3: Use Migration Script
If you have SSH access to the server:
```bash
cd backend
python apply_migration_now.py
```

## After Columns Are Added

1. **Uncomment final_body in model:**
   - `backend/app/models/prospect.py`: Uncomment `final_body = Column(Text, nullable=True)`
   - `backend/app/schemas/prospect.py`: Uncomment `final_body: Optional[str] = None`

2. **Restart backend again**

3. **Verify:**
   - Websites tab shows 100+ websites
   - Leads tab shows 83 emails
   - Scraped Emails tab shows 83 emails
   - Overview shows correct counts

## Why This Happened

The `final_body` column was referenced in the ORM model but never added to the database. SQLAlchemy tries to SELECT all columns defined in the model, so when `final_body` doesn't exist, all queries fail.

## Prevention

- Always run migrations before deploying
- Ensure ORM models match database schema exactly
- Use defensive column existence checks for optional columns

