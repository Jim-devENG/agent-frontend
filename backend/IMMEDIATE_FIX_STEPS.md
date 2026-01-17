# IMMEDIATE FIX - Run Migration Now

## The Problem
You're getting 503 errors because social outreach tables don't exist.

## The Solution (Choose One)

### Option 1: Manual Migration via Render Shell (FASTEST - 2 minutes)

1. **Open Render Dashboard**
   - Go to https://dashboard.render.com
   - Select your backend service

2. **Open Shell**
   - Click "Shell" tab (or "Manual Deploy" → "Run Shell")

3. **Run Migration**
   ```bash
   cd backend
   alembic upgrade head
   ```

4. **Verify**
   - Check output for: "Running upgrade ... -> add_social_tables"
   - Test your endpoints - they should work now!

### Option 2: Configure Prestart in Render Dashboard

1. **Go to Settings**
   - Render Dashboard → Your Service → Settings

2. **Add Prestart Command**
   - Find "Prestart Command" field
   - Add: `bash prestart.sh`
   - (If root directory is not `backend/`, use: `cd backend && bash prestart.sh`)

3. **Save and Redeploy**
   - Click "Save Changes"
   - Trigger a new deployment
   - Check logs for migration output

### Option 3: Use Render's Database Dashboard

If you have direct database access:

1. Go to your PostgreSQL database in Render
2. Click "Connect" → "External Connection"
3. Use any PostgreSQL client to run:
   ```sql
   -- Check if tables exist
   SELECT table_name 
   FROM information_schema.tables 
   WHERE table_schema = 'public' 
   AND table_name LIKE 'social_%';
   
   -- If they don't exist, the migration hasn't run
   ```

## Why This Happened

The `prestart.sh` script exists but Render may not be auto-detecting it. This can happen if:
- Root directory configuration doesn't match script location
- Render service needs explicit prestart command configuration
- Script permissions or path issues

## After Fix

Once migration runs, you should see:
- ✅ No more 503 errors
- ✅ `/api/social/discover` works
- ✅ `/api/social/profiles` returns data (or empty array)

## Prevention

After fixing, ensure prestart is configured in Render dashboard so this doesn't happen again on future deployments.

