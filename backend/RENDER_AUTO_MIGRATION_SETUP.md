# Automatic Migrations on Render (Best Solution)

## The Problem

Migrations need to run automatically on every deployment, but they're not running reliably.

## The Best Solution: Configure Prestart Script in Render

### Step 1: Configure Start Command in Render Dashboard

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Select your backend service
3. Go to **Settings** tab
4. Find **"Start Command"** field
5. Set it to:

```bash
bash prestart.sh && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**OR if your structure is different:**

```bash
cd backend && bash prestart.sh && cd .. && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

6. Click **Save Changes**
7. Render will automatically redeploy

### How This Works

1. **`bash prestart.sh`** - Runs migrations FIRST (before app starts)
2. **`&&`** - Only starts app if migrations succeed
3. **`uvicorn ...`** - Starts the FastAPI app

### Why This is Better

✅ **Automatic** - Runs on every deployment  
✅ **Fail-fast** - If migrations fail, deployment fails (prevents broken state)  
✅ **No manual steps** - No HTTP calls, no shell access needed  
✅ **Reliable** - Render guarantees prestart runs before app starts  

## Alternative: If Prestart Doesn't Work

If the prestart script approach doesn't work, the app will still try to run migrations on startup (in `main.py`). However, this is less reliable because:

- App might accept requests before migrations complete
- Errors might be logged but not block startup

## Fallback: HTTP Migration Endpoint

If automatic migrations fail, you can still use the HTTP endpoint:

```bash
curl -X POST https://agent-liquidcanvas.onrender.com/api/health/migrate \
     -H "X-Migration-Token: migrate-2026-secret-token-xyz110556"
```

But this should only be needed as a one-time fix or emergency fallback.

## Verify It's Working

After configuring the start command and redeploying:

1. Check Render logs during deployment
2. You should see:
   ```
   ==========================================
   🚀 Running database migrations...
   ==========================================
   ✅ Database migrations completed successfully
   ==========================================
   ```
3. Then the app will start normally

## Current Status

Your app already has:
- ✅ `prestart.sh` script (ready to use)
- ✅ Startup migration code in `main.py` (backup)
- ✅ HTTP migration endpoint (fallback)

**You just need to configure the Start Command in Render Dashboard!**

