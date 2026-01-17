# 🚨 URGENT FIX - Run Migration NOW

## The Problem
You're still getting 503 errors because the migration hasn't run in production.

## IMMEDIATE FIX (2 minutes)

### Step 1: Open Render Shell

1. Go to https://dashboard.render.com
2. Click on your backend service (agent-liquidcanvas)
3. Click the **"Shell"** tab at the top
4. This opens a terminal connected to your production server

### Step 2: Run Migration

In the Render shell, type these commands one by one:

```bash
# Check where you are
pwd

# Navigate to backend directory
cd backend

# OR if that doesn't work, try:
cd /opt/render/project/src/backend

# Check if alembic.ini exists
ls -la alembic.ini

# Run the migration
alembic upgrade head
```

### Step 3: Verify Success

You should see output like:
```
INFO  [alembic.runtime.migration] Running upgrade final_schema_repair -> add_social_tables, add social outreach tables
```

### Step 4: Test

After migration completes, refresh your browser and try the social discovery again. It should work!

## Alternative: If Shell Doesn't Work

### Option A: Use Render's Database Dashboard

1. Go to your PostgreSQL database in Render
2. Click "Connect" → "External Connection"
3. Use any PostgreSQL client (pgAdmin, DBeaver, etc.)
4. Run this SQL to check if tables exist:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE 'social_%';
```

If no tables are returned, the migration hasn't run.

### Option B: Configure Prestart in Render Dashboard

1. Go to Render Dashboard → Your Service → **Settings**
2. Scroll down to **"Prestart Command"**
3. Add: `cd backend && bash prestart.sh`
4. **Save Changes**
5. Click **"Manual Deploy"** → **"Deploy latest commit"**
6. Watch the logs - you should see migration output

## Why This Happened

The `prestart.sh` script exists in the code, but Render may not be auto-detecting it. This can happen if:
- The root directory setting doesn't match
- Render needs explicit prestart command configuration
- The script needs to be in a specific location

## After Fix

Once migration runs successfully:
- ✅ `/api/social/discover` will return 200 (not 503)
- ✅ `/api/social/profiles` will work
- ✅ All 4 social tables will exist: `social_profiles`, `social_discovery_jobs`, `social_drafts`, `social_messages`

## Prevention

After fixing, configure the prestart command in Render dashboard so migrations run automatically on every deployment.

