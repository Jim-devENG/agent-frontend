# Migration Endpoint - Quick Fix

## The Issue

The migration endpoint might not be available yet because:
1. Code needs to be deployed to Render
2. `MIGRATION_TOKEN` needs to be set in Render environment variables

## Step 1: Set MIGRATION_TOKEN in Render

1. Go to Render Dashboard → Your Backend Service
2. Go to **Environment** tab
3. Add environment variable:
   - **Key**: `MIGRATION_TOKEN`
   - **Value**: `migrate-2026-secret-token-xyz110556`
4. Click **Save Changes**
5. Wait for service to redeploy (1-2 minutes)

## Step 2: Wait for Deployment

After pushing code changes, wait for Render to:
1. Build the new code
2. Deploy the service
3. Start accepting requests

Check Render logs to see when deployment completes.

## Step 3: Try the Endpoint Again

Once deployed, try:

```powershell
curl.exe -X POST https://agent-liquidcanvas.onrender.com/health/migrate -H "X-Migration-Token: migrate-2026-secret-token-xyz110556"
```

## Alternative: Use the Better Solution

**Instead of the HTTP endpoint, configure Render Start Command:**

1. Render Dashboard → Your Service → **Settings**
2. Find **"Start Command"** field
3. Set to:
   ```bash
   bash prestart.sh && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
4. Save and redeploy

This will run migrations automatically on every deployment - no manual steps needed!

