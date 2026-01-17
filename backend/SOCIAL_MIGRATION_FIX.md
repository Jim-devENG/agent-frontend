# Social Outreach Migration Fix - Production Ready

## Problem Summary

The `/api/social/discover` endpoint was crashing with:
- Error: "Social outreach tables do not exist"
- Root cause: Alembic migrations were not detecting social models
- Secondary issue: Runtime table creation was masking the real problem

## Fixes Applied

### 1. ✅ Added Social Models to Alembic Context

**File:** `backend/alembic/env.py`
- Added imports for all social models: `SocialProfile`, `SocialDiscoveryJob`, `SocialDraft`, `SocialMessage`
- Ensures Alembic can detect these models when generating/running migrations

**File:** `backend/app/models/__init__.py`
- Added social models to `__all__` export
- Ensures models are properly imported when Alembic runs

### 2. ✅ Fixed Migration Chain

**File:** `backend/alembic/versions/add_social_outreach_tables.py`
- Fixed `down_revision` from `'999_final_schema_repair'` to `'final_schema_repair'`
- Migration chain: `final_schema_repair` → `add_social_tables` → `ensure_critical_columns`

### 3. ✅ Removed Runtime Table Creation (FAIL FAST)

**File:** `backend/app/api/social.py`
- **`/api/social/discover` endpoint:** Removed all runtime table creation code
- **`/api/social/profiles` endpoint:** Removed all runtime table creation code
- Both endpoints now return **HTTP 503 (Service Unavailable)** with clear error message when tables don't exist
- Error message: "Social outreach tables do not exist. Database migrations have not been applied. Please run: alembic upgrade head"

**File:** `backend/app/main.py`
- Removed runtime table creation from startup code
- Now only logs error and continues (app starts, but social endpoints return 503)

### 4. ✅ Verified Migrations Run on Startup

**File:** `backend/app/main.py` (lines 185-191)
- Migrations run automatically on startup via `alembic upgrade head`
- This ensures tables are created in production deployments

## Migration Files

### Required Migration
- **File:** `backend/alembic/versions/add_social_outreach_tables.py`
- **Revision:** `add_social_tables`
- **Down Revision:** `final_schema_repair`
- **Creates:**
  - Enum types: `socialplatform`, `qualificationstatus`, `messagestatus`
  - Tables: `social_discovery_jobs`, `social_profiles`, `social_drafts`, `social_messages`
  - All indexes and foreign keys

## Production Deployment Steps

1. **Ensure migrations run on deploy:**
   - Backend startup automatically runs `alembic upgrade head` (line 188 in `main.py`)
   - This should create all tables including social tables

2. **If tables are still missing after deploy:**
   - Check backend logs for migration errors
   - Manually run: `alembic upgrade head` in production
   - Verify migration chain: `alembic history` should show `add_social_tables` after `final_schema_repair`

3. **Verify tables exist:**
   ```sql
   SELECT table_name 
   FROM information_schema.tables 
   WHERE table_schema = 'public' 
   AND table_name IN ('social_profiles', 'social_discovery_jobs', 'social_drafts', 'social_messages');
   ```

## Expected Behavior

### ✅ Success Case
- Migrations run on startup
- Social tables are created
- `/api/social/discover` works correctly
- `/api/social/profiles` returns data (or empty array if no profiles)

### ❌ Failure Case (Schema Not Ready)
- If tables don't exist, endpoints return **HTTP 503** with clear message
- No silent failures or fake table creation
- Error message directs to run migrations

## Testing

1. **Local:**
   ```bash
   cd backend
   alembic upgrade head
   # Verify tables exist
   # Test /api/social/discover endpoint
   ```

2. **Production:**
   - Deploy code
   - Check startup logs for "✅ Database migrations completed successfully"
   - Check startup logs for "✅ All social tables exist"
   - If missing, check logs for migration errors

## Files Changed

1. `backend/alembic/env.py` - Added social model imports
2. `backend/app/models/__init__.py` - Added social models to exports
3. `backend/alembic/versions/add_social_outreach_tables.py` - Fixed migration chain
4. `backend/app/api/social.py` - Removed runtime table creation, fail fast
5. `backend/app/main.py` - Removed runtime table creation, better error logging

## Migration Chain Verification

Current chain (from `alembic history`):
```
... → final_schema_repair → add_social_tables → ensure_critical_columns → ...
```

Ensure `add_social_tables` is in the chain and `down_revision` points to `final_schema_repair`.

