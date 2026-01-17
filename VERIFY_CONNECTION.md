# How to Verify Database Connection is Working

## Current Status
✅ **Deployment completed successfully!**
Now we need to verify the database connection is working.

---

## Step 1: Check Runtime Logs (Not Deployment Logs)

The logs you just showed are **deployment logs** (building Docker image, pushing to registry). We need to see **runtime logs** (application startup).

### On Render Dashboard:

1. **Go to**: https://dashboard.render.com
2. **Click** your backend service
3. **Click** the **"Logs"** tab
4. **Scroll down** to see the most recent logs

### What to Look For:

#### ✅ **Success Indicators** (Connection is Working):

You should see logs like this:
```
INFO:     Started server process [8]
INFO:     Waiting for application startup.
🚀 Server starting up...
📡 Server will listen on port 10000
ℹ️  Using connection pooler (port 6543) - skipping IPv4 resolution (pooler handles IPv4)
✅ Configured SSL for Supabase connection
🔗 Creating engine with connection target: db.wlsbtxwbyqdagvrbkebl.supabase.co
✅ Async engine created successfully
✅ Database connection test passed
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:10000
```

#### ❌ **Failure Indicators** (Connection is Not Working):

If you see errors like:
```
❌ Failed to connect to database: ...
OSError: [Errno 101] Network is unreachable
psycopg2.OperationalError: connection to server at ...
```

Then the connection string might need adjustment.

---

## Step 2: Test the Health Endpoint

### Option A: Visit in Browser
```
https://agent-liquidcanvas.onrender.com/health
```

**Expected Response** (if working):
```json
{
  "status": "healthy",
  "service": "art-outreach-api"
}
```

### Option B: Test Readiness Endpoint
```
https://agent-liquidcanvas.onrender.com/health/ready
```

**Expected Response** (if database is connected):
```json
{
  "status": "ready",
  "database": "connected"
}
```

**Expected Response** (if database connection failed):
```json
{
  "status": "ready",
  "database": "checking",
  "warning": "[error message]"
}
```

### Option C: Use curl (Command Line)
```bash
curl https://agent-liquidcanvas.onrender.com/health
curl https://agent-liquidcanvas.onrender.com/health/ready
```

---

## Step 3: Check Connection String Configuration

If the connection is still failing, verify your `DATABASE_URL` on Render:

1. **Go to**: Render Dashboard → Your Service → Environment tab
2. **Find** `DATABASE_URL`
3. **Verify** it looks like:
   ```
   postgresql+asyncpg://postgres:L1qu%21dcvnvs@db.wlsbtxwbyqdagvrbkebl.supabase.co:6543/postgres?pgbouncer=true
   ```
4. **Check**:
   - ✅ Port is `6543` (not 5432)
   - ✅ Has `?pgbouncer=true` parameter
   - ✅ Has `+asyncpg` after `postgresql`
   - ✅ Password is URL-encoded: `L1qu%21dcvnvs`

---

## Step 4: Check for Connection Pooler Message

In the logs, you should see this message if using the pooler:
```
ℹ️  Using connection pooler (port 6543) - skipping IPv4 resolution (pooler handles IPv4)
```

If you **DON'T** see this message, the code might not be detecting the pooler correctly. In that case:
- Make sure the URL contains `:6543` or `pgbouncer=true`
- Check that the latest code is deployed (commit `9f529a7`)

---

## Troubleshooting

### Problem: Logs show connection errors

**Possible Causes:**
1. Wrong port (still using 5432 instead of 6543)
2. Missing `pgbouncer=true` parameter
3. Incorrect password encoding
4. Pooler hostname might be different

**Solution:**
1. Double-check `DATABASE_URL` in Render environment variables
2. Make sure you copied the connection string correctly from Supabase dashboard
3. Try the exact connection string format from Supabase (they might use a different hostname for pooler)

### Problem: No startup logs visible

**Solution:**
- Make sure you're looking at **Runtime Logs**, not **Build Logs**
- Click "Logs" tab (not "Events" or "Build Logs")
- Scroll to the bottom to see most recent logs
- Refresh the page if logs seem stuck

### Problem: Health endpoint returns error

**Solution:**
- Check if the service is actually running (should show "Live" status)
- Wait a few minutes - startup can take 30-60 seconds
- Check logs for any startup errors

---

## Quick Verification Checklist

- [ ] Checked Runtime Logs (not deployment logs)
- [ ] Saw "Using connection pooler" message
- [ ] Saw "Async engine created successfully"
- [ ] Saw "Database connection test passed" (if startup test runs)
- [ ] Health endpoint `/health` returns 200 OK
- [ ] Readiness endpoint `/health/ready` shows "database": "connected"
- [ ] Verified `DATABASE_URL` uses port 6543
- [ ] Verified `DATABASE_URL` has `pgbouncer=true`

---

## Next Steps After Verification

Once you confirm the connection is working:

1. ✅ Test your API endpoints that query the database
2. ✅ Monitor logs for any connection errors
3. ✅ If everything works, you're done! 🎉

If the connection is still failing:
- Check the exact error message in logs
- Verify the connection string format matches Supabase's pooler format
- Consider trying the alternative pooler hostname format if Supabase provides it

---

**Please check your Runtime Logs now and let me know what you see!**

