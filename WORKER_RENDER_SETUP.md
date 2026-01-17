# Worker Service Setup on Render (Free Tier)

## Problem
All discovery jobs are failing with "Worker service not available" because the worker service is not running on Render.

## Solution: Deploy Worker as Background Worker

### Step 1: Create Background Worker on Render

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click "New +"** → **"Background Worker"**
3. **Connect GitHub Repository**: Select your `agent.liquidcanvas` repository
4. **Configure Service**:
   - **Name**: `art-outreach-worker` (or any name you prefer)
   - **Root Directory**: `worker`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python worker.py`

### Step 2: Add Environment Variables

Add the **same environment variables** as your backend service:

**Required:**
- `DATABASE_URL` - Same PostgreSQL URL as backend
- `REDIS_URL` - Same Redis URL as backend

**API Keys (same as backend):**
- `DATAFORSEO_LOGIN` - Your DataForSEO email
- `DATAFORSEO_PASSWORD` - Your DataForSEO password
- `HUNTER_IO_API_KEY` - Your Hunter.io API key
- `GEMINI_API_KEY` - Your Google Gemini API key
- `GMAIL_CLIENT_ID` - Your Gmail OAuth client ID
- `GMAIL_CLIENT_SECRET` - Your Gmail OAuth client secret
- `GMAIL_REFRESH_TOKEN` - Your Gmail refresh token

**Optional (not needed for worker):**
- `JWT_SECRET_KEY` - Not needed (worker doesn't handle auth)
- `ADMIN_USERNAME` - Not needed
- `ADMIN_PASSWORD` - Not needed

### Step 3: Deploy

1. Click **"Create Background Worker"**
2. Wait for deployment to complete
3. Check logs to verify worker started successfully

### Step 4: Verify Worker is Running

1. **Check Worker Logs** in Render dashboard
2. You should see:
   ```
   ✅ Connected to Redis: ...
   Starting RQ worker...
   Listening to queues: discovery, enrichment, scoring, send, followup
   ```

3. **Test Discovery Job**:
   - Go to your frontend
   - Use Manual Scrape to create a discovery job
   - Check the Jobs tab - it should show "running" then "completed" instead of "failed"

## Troubleshooting

### Worker fails to start

**Check logs for:**
- `ModuleNotFoundError` - Missing dependencies, check `requirements.txt`
- `Redis connection failed` - Check `REDIS_URL` environment variable
- `Database connection failed` - Check `DATABASE_URL` environment variable

### Jobs still failing

1. **Check Redis connection**:
   - Worker logs should show "✅ Connected to Redis"
   - If not, verify `REDIS_URL` is correct

2. **Check worker is listening**:
   - Logs should show "Listening to queues: discovery, ..."
   - If not, worker may have crashed

3. **Check backend can queue jobs**:
   - Backend logs should show "Discovery job {id} queued successfully"
   - If it shows "Redis not available", backend can't connect to Redis

### Worker keeps restarting

- Check memory usage (free tier has limits)
- Check for infinite loops in worker code
- Check database connection pool settings

## Quick Checklist

- [ ] Background Worker created on Render
- [ ] Root Directory set to `worker`
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `python worker.py`
- [ ] `DATABASE_URL` environment variable set
- [ ] `REDIS_URL` environment variable set
- [ ] All API keys set (DataForSEO, Hunter, Gemini, Gmail)
- [ ] Worker service shows "Live" status
- [ ] Worker logs show "Connected to Redis"
- [ ] Test discovery job completes successfully

## After Setup

Once the worker is running:
- ✅ Discovery jobs will process automatically
- ✅ Jobs will show "running" then "completed" status
- ✅ Websites will be discovered and saved to database
- ✅ You can see results in the "Websites" tab

