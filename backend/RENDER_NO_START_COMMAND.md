# Render Configuration - No Start Command Field

If you don't see a "Start Command" field in Render, here are the alternatives:

## Option 1: Use Build Command (If Available)

Some Render services have a "Build Command" field instead:

1. Go to Render Dashboard → Your Service → **Settings**
2. Look for **"Build Command"** or **"Build"** section
3. If available, you can add migrations there (though this is less ideal)

## Option 2: Automatic Migrations on Startup (Already Implemented)

**Good news:** Your app already runs migrations automatically on startup!

The code in `backend/app/main.py` runs `alembic upgrade head` every time the app starts. This should work, but if it's not working, we can:

1. **Use the HTTP endpoint** (one-time fix):
   - Set `MIGRATION_TOKEN` in Render environment variables
   - Call the endpoint once to create tables
   - After that, startup migrations should maintain them

2. **Check Render logs** to see if migrations are running:
   - Go to Render Dashboard → Your Service → **Logs**
   - Look for: "🔄 Running database migrations on startup"
   - If you see errors, they'll be logged there

## Option 3: Check Other Render Settings

Render's UI varies. Look for:
- **"Command"** field
- **"Run Command"** field  
- **"Deploy"** section
- **"Build & Deploy"** section

## Current Status

Your app has:
- ✅ Automatic migrations on startup (in `main.py`)
- ✅ HTTP migration endpoint (`/health/migrate`) as fallback
- ✅ Robust error handling and logging

**The startup migrations should work automatically.** If they're not, check the Render logs to see what's happening.

## Quick Fix: Use HTTP Endpoint

Since startup migrations might not be working, use the HTTP endpoint:

1. **Set MIGRATION_TOKEN in Render:**
   - Environment tab → Add `MIGRATION_TOKEN` = `migrate-2026-secret-token-xyz110556`

2. **Wait for deployment** (1-2 minutes)

3. **Run migration:**
   ```powershell
   curl.exe -X POST https://agent-liquidcanvas.onrender.com/health/migrate -H "X-Migration-Token: migrate-2026-secret-token-xyz110556"
   ```

After this one-time fix, the tables will exist and the app will work normally.

