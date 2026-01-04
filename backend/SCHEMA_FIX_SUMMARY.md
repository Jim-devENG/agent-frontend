# Schema Fix Summary: Missing Social Columns in Prospects Table

## Root Cause (1-2 sentences)

The SQLAlchemy `Prospect` model includes 7 social outreach columns (`source_type`, `source_platform`, `profile_url`, `username`, `display_name`, `follower_count`, `engagement_rate`), but these columns do not exist in the PostgreSQL `prospects` table. The migration `add_social_columns_to_prospects.py` exists but either hasn't been applied or has a type mismatch (`Float()` vs `Numeric(5,2)` for `engagement_rate`).

## Exact Fix

**Migration File**: `backend/alembic/versions/add_social_columns_to_prospects.py`

**Change Applied**: Fixed `engagement_rate` column type from `sa.Float()` to `sa.Numeric(5, 2)` to match the ORM model.

**To Apply**:
```bash
alembic upgrade head
```

**Or manually run the migration** (if Alembic has issues):
```sql
-- Check existing columns first
SELECT column_name FROM information_schema.columns WHERE table_name = 'prospects';

-- Add missing columns (idempotent - safe to run multiple times)
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS source_type VARCHAR DEFAULT 'website' NOT NULL;
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS source_platform VARCHAR;
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS profile_url TEXT;
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS username VARCHAR;
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS display_name VARCHAR;
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS follower_count INTEGER;
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS engagement_rate NUMERIC(5, 2);

-- Set default for existing rows
UPDATE prospects SET source_type = 'website' WHERE source_type IS NULL;

-- Create indexes
CREATE INDEX IF NOT EXISTS ix_prospects_source_type ON prospects(source_type);
CREATE INDEX IF NOT EXISTS ix_prospects_source_platform ON prospects(source_platform);
CREATE INDEX IF NOT EXISTS ix_prospects_profile_url ON prospects(profile_url);
CREATE INDEX IF NOT EXISTS ix_prospects_username ON prospects(username);

-- Add constraints
ALTER TABLE prospects DROP CONSTRAINT IF EXISTS check_source_type;
ALTER TABLE prospects ADD CONSTRAINT check_source_type CHECK (source_type IN ('website', 'social'));

ALTER TABLE prospects DROP CONSTRAINT IF EXISTS check_source_platform;
ALTER TABLE prospects ADD CONSTRAINT check_source_platform CHECK (source_platform IS NULL OR source_platform IN ('linkedin', 'instagram', 'facebook', 'tiktok'));
```

## Why This Fix is Safe

1. **Idempotent**: Migration checks for column existence before adding
2. **Additive Only**: No drops, no renames, no data loss
3. **Nullable Fields**: All new columns except `source_type` are nullable (won't break existing data)
4. **Default Values**: `source_type` has `server_default='website'` (existing rows get default)
5. **Backward Compatible**: Website outreach continues working (all existing rows get `source_type='website'`)
6. **No Breaking Changes**: Existing queries continue to work
7. **Reversible**: Migration has `downgrade()` function (though not recommended in production)

## What to Verify After Applying

1. **Columns Exist**:
   ```sql
   SELECT column_name, data_type, is_nullable, column_default
   FROM information_schema.columns 
   WHERE table_name = 'prospects' 
   AND column_name IN ('source_type', 'source_platform', 'profile_url', 'username', 'display_name', 'follower_count', 'engagement_rate');
   ```
   Expected: All 7 columns should exist

2. **Default Values**:
   ```sql
   SELECT COUNT(*) FROM prospects WHERE source_type IS NULL;
   ```
   Expected: 0 (all existing rows should have `source_type='website'`)

3. **Deduplication SELECT Works**:
   - Run a discovery job
   - Check logs for `UndefinedColumnError` - should be gone
   - Verify: `SELECT ... FROM prospects WHERE prospects.domain = $1` succeeds

4. **Inserts Work**:
   - Run discovery: "Art Gallery usa"
   - Check job result: `prospects_saved > 0` (not 0)
   - Verify: New prospects are saved with `source_type='website'`

5. **Website Outreach Unaffected**:
   - Existing prospects still visible
   - Pipeline status queries work
   - No errors in website discovery

## Expected Outcome

**Before Fix**:
- Discovery finds 53 websites
- All fail to save: `UndefinedColumnError: column prospects.source_type does not exist`
- Results: "Results Found: 53, Prospects Saved: 0"

**After Fix**:
- Discovery finds 53 websites
- All save successfully
- Results: "Results Found: 53, Prospects Saved: 53" (or close to it, accounting for duplicates)

