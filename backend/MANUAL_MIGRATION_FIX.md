# Manual Migration Fix - Immediate Solution

## Problem
Social outreach tables don't exist in production, causing 503 errors.

## Quick Fix: Run Migration Manually

Since the prestart script may not be running automatically, you can run the migration manually via Render's shell.

### Step 1: Access Render Shell

1. Go to your Render dashboard
2. Select your backend service
3. Click on "Shell" tab (or use "Manual Deploy" → "Run Shell")
4. This opens a terminal connected to your production environment

### Step 2: Run Migration

In the Render shell, run:

```bash
cd /opt/render/project/src/backend
# OR if that doesn't work:
cd backend
# OR if that doesn't work:
pwd  # Check current directory, then navigate to backend

# Run migration
alembic upgrade head
```

### Step 3: Verify Tables Created

```bash
# Connect to your database (if you have psql access)
# Or check via your database dashboard

# Expected output should show:
# INFO  [alembic.runtime.migration] Running upgrade final_schema_repair -> add_social_tables, add social outreach tables
```

### Step 4: Test Endpoints

After migration completes, test:
- `POST /api/social/discover` - Should no longer return 503
- `GET /api/social/profiles` - Should return empty array (not 503)

## Alternative: Configure Prestart in Render Dashboard

If you want automatic migrations on every deploy:

1. Go to Render dashboard → Your backend service → Settings
2. Scroll to "Prestart Command"
3. Add: `cd backend && bash prestart.sh`
4. Or if root directory is already `backend/`: `bash prestart.sh`
5. Save and redeploy

## Verify Migration Ran

Check Render logs for:
```
🚀 Running database migrations...
📝 Executing: alembic upgrade head
✅ Database migrations completed successfully
```

If you don't see this, the prestart script isn't running and you need to:
1. Configure it manually in Render dashboard, OR
2. Run migration manually via shell (as above)

