# Render Deployment Fix - Automatic Migrations

## Problem

Production API returns 503 errors:
- `POST /api/social/discover`
- `GET /api/social/profiles`

Error: "Social outreach tables do not exist. Database migrations have not been applied."

## Root Cause

**Alembic migrations are not running automatically on Render deployment.**

Even though `main.py` has migration code in the startup event, Render may start accepting requests before migrations complete, or the migration code may not execute properly in the Render environment.

## Solution: Prestart Script

**Chosen approach: Add `prestart.sh` script**

### Why Prestart Script?

1. **Runs BEFORE the application starts** - Guarantees migrations complete before any requests
2. **Render automatically executes it** - No manual configuration needed
3. **Fails fast** - If migrations fail, deployment fails (prevents broken state)
4. **Explicit and visible** - Clear in logs when migrations run

### Alternative Approaches Considered

- ❌ **Start command modification**: Less reliable, harder to debug
- ❌ **One-time migration job**: Requires manual intervention, not automatic
- ✅ **Prestart script**: Best practice for Render, automatic, reliable

## Implementation

### 1. Created `backend/prestart.sh`

```bash
#!/bin/bash
# Runs alembic upgrade head before application starts
alembic upgrade head
```

### 2. Verify Models in Alembic

✅ **`backend/alembic/env.py`** - Social models imported:
```python
from app.models.social import SocialProfile, SocialDiscoveryJob, SocialDraft, SocialMessage
```

✅ **`backend/app/models/__init__.py`** - Social models exported

### 3. Verify Migration Exists

✅ **`backend/alembic/versions/add_social_outreach_tables.py`**
- Creates: `social_profiles`, `social_discovery_jobs`, `social_drafts`, `social_messages`
- Idempotent (safe to run multiple times)
- Chain: `final_schema_repair` → `add_social_tables`

### 4. Fail-Fast Endpoints

✅ **`backend/app/api/social.py`**
- Returns HTTP 503 with clear error message
- No runtime table creation
- No silent failures

## Render Configuration

### Option 1: Automatic (Recommended)

Render automatically detects and runs `prestart.sh` if it exists in the root directory.

**No additional configuration needed!**

### Option 2: Manual (If needed)

If Render doesn't auto-detect, add to Render dashboard:
- **Build Command**: (leave as default)
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Prestart Command**: `cd backend && bash prestart.sh`

## Verification Steps

1. **Deploy to Render**
2. **Check logs** for:
   ```
   🚀 Running database migrations...
   📝 Executing: alembic upgrade head
   ✅ Database migrations completed
   ```

3. **Test endpoints**:
   ```bash
   curl -X POST https://your-app.onrender.com/api/social/discover
   curl https://your-app.onrender.com/api/social/profiles
   ```

4. **Verify tables exist**:
   ```sql
   SELECT table_name 
   FROM information_schema.tables 
   WHERE table_schema = 'public' 
   AND table_name LIKE 'social_%';
   ```

## Expected Behavior

### ✅ Success
- Prestart script runs migrations
- Tables created: `social_profiles`, `social_discovery_jobs`, `social_drafts`, `social_messages`
- Endpoints return 200 (or appropriate status, not 503)
- No "tables do not exist" errors

### ❌ Failure (If migrations fail)
- Deployment fails (prestart script exits with error)
- Clear error message in logs
- No broken state deployed

## Files Changed

1. ✅ `backend/prestart.sh` - Created (NEW)
2. ✅ `backend/alembic/env.py` - Already has social models
3. ✅ `backend/alembic/versions/add_social_outreach_tables.py` - Migration exists
4. ✅ `backend/app/api/social.py` - Already fails fast

## Prevention

Going forward:
- ✅ All new models must be added to `alembic/env.py`
- ✅ All migrations must be idempotent
- ✅ Prestart script ensures migrations run on every deploy
- ✅ Fail-fast endpoints prevent silent failures

## Testing Locally

Test the prestart script locally:
```bash
cd backend
bash prestart.sh
```

Should output:
```
🚀 Running database migrations...
📝 Executing: alembic upgrade head
✅ Database migrations completed
```

