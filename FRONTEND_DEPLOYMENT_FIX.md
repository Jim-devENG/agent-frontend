# Frontend Deployment Fix - API Endpoint Errors

## Problem

The frontend is showing 404 errors for endpoints like:
- `/api/v1/automation/status` 
- `/api/v1/jobs/latest`
- `/api/v1/stats`
- `/api/v1/activity`
- `/api/v1/discovery/status`

## Root Cause

1. **Environment Variable Issue**: The `NEXT_PUBLIC_API_BASE_URL` in Vercel might be set to include `/v1`
2. **Cached Build**: Vercel might be serving an old build with old API calls
3. **API Path Mismatch**: New backend uses `/api` not `/api/v1`

## Solution

### Step 1: Update Vercel Environment Variable

1. Go to **Vercel Dashboard** → **Your Project** → **Settings** → **Environment Variables**
2. Find `NEXT_PUBLIC_API_BASE_URL`
3. **Current (wrong)**: `https://agent-liquidcanvas.onrender.com/api/v1`
4. **Change to**: `https://agent-liquidcanvas.onrender.com/api` (remove `/v1`)
5. Click **Save**

### Step 2: Redeploy Frontend

1. Go to **Vercel Dashboard** → **Your Project** → **Deployments**
2. Click **Redeploy** on the latest deployment
3. Or push a new commit to trigger auto-deploy

### Step 3: Clear Browser Cache

1. Open browser DevTools (F12)
2. Right-click the refresh button
3. Select **"Empty Cache and Hard Reload"**
4. Or use `Ctrl+Shift+R` (Windows) / `Cmd+Shift+R` (Mac)

## Code Fix Applied

The code has been updated to automatically remove `/v1` from the API base URL:

```typescript
const envBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api'
const API_BASE = envBase.replace('/api/v1', '/api').replace('/v1', '')
```

## Missing Endpoints

The new backend doesn't have these endpoints (they're from the old system):
- `/api/v1/automation/status` - Not needed (automation is handled via jobs)
- `/api/v1/jobs/latest` - Use `/api/jobs` instead
- `/api/v1/stats` - Stats are calculated client-side from prospects/jobs
- `/api/v1/activity` - Not implemented yet (ActivityFeed uses mock data)
- `/api/v1/discovery/status` - Use `/api/jobs` with filter for discovery jobs

## After Fix

Once you update the environment variable and redeploy, the frontend should:
- ✅ Connect to the correct backend endpoints
- ✅ Stop showing 404 errors
- ✅ Display data correctly

## Verify

After redeploying, check the browser console. You should see:
- ✅ Successful API calls to `/api/jobs`, `/api/prospects`
- ❌ No more 404 errors for `/api/v1/*` endpoints

