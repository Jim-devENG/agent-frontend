# Frontend 404 Errors - Fix Guide

## Problem

The deployed frontend on Vercel is showing 404 errors for these endpoints:
- `/api/stats` 
- `/api/jobs/latest`
- `/api/automation/status`
- `/api/discovery/status`
- `/api/discovery/locations`
- `/api/discovery/categories`
- `/api/activity`

## Root Cause

The deployed frontend is using **old JavaScript bundles** that call endpoints from the previous architecture. The current source code is correct and uses the new API endpoints.

## Solution

### Step 1: Verify Code is Pushed

The latest code has been pushed to GitHub. Verify:
```bash
git log --oneline -5
```

You should see commits with:
- "Add authentication endpoint and fix frontend API calls"

### Step 2: Trigger Vercel Redeploy

**Option A: Automatic (if connected to GitHub)**
- Vercel should auto-deploy when you push to the main branch
- Check Vercel dashboard: https://vercel.com/dashboard
- Look for a new deployment after your latest push

**Option B: Manual Redeploy**
1. Go to Vercel Dashboard: https://vercel.com/dashboard
2. Find your project: `agent-frontend` or `agent.liquidcanvas.art`
3. Click on the project
4. Go to "Deployments" tab
5. Click "..." on the latest deployment
6. Select "Redeploy"

### Step 3: Verify Vercel Settings

Make sure Vercel is configured correctly:

1. **Root Directory**: Should be `frontend/`
2. **Framework**: Next.js (auto-detected)
3. **Build Command**: `npm run build` (default)
4. **Environment Variables**:
   ```
   NEXT_PUBLIC_API_BASE_URL=https://agent-liquidcanvas.onrender.com/api
   ```
   ⚠️ **Important**: Remove `/v1` from the URL - the new backend uses `/api` directly

### Step 4: Clear Browser Cache

After Vercel redeploys:
1. **Hard refresh**: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
2. Or **clear browser cache** completely
3. Or use **Incognito/Private mode** to test

### Step 5: Verify Fix

After redeploy and cache clear, check:
1. Open browser DevTools (F12)
2. Go to Network tab
3. Refresh the page
4. Look for API calls - they should be:
   - ✅ `/api/jobs` (not `/api/jobs/latest`)
   - ✅ `/api/prospects` (not `/api/stats`)
   - ✅ No calls to `/api/automation/status`
   - ✅ No calls to `/api/discovery/*`

## Current API Endpoints (New Architecture)

The frontend should be calling:
- ✅ `GET /api/jobs` - List jobs
- ✅ `GET /api/prospects` - List prospects  
- ✅ `POST /api/jobs/discover` - Create discovery job
- ✅ `POST /api/auth/login` - Login
- ✅ `GET /api/jobs/{id}/status` - Get job status

## Troubleshooting

### Still seeing 404s after redeploy?

1. **Check Vercel build logs**:
   - Go to Vercel → Your Project → Deployments
   - Click on the latest deployment
   - Check "Build Logs" for errors

2. **Verify environment variable**:
   - Go to Vercel → Your Project → Settings → Environment Variables
   - Ensure `NEXT_PUBLIC_API_BASE_URL` is set correctly
   - Should be: `https://agent-liquidcanvas.onrender.com/api` (no `/v1`)

3. **Check if frontend is in separate repo**:
   - If frontend is in `Jim-devENG/agent-frontend`, make sure you push there too
   - If frontend is in monorepo, ensure Vercel root directory is `frontend/`

4. **Wait for CDN propagation**:
   - Vercel uses a CDN that may take 1-2 minutes to update
   - Try again after a few minutes

## Summary

✅ **Code is correct** - The source code uses the right endpoints  
⏳ **Waiting for Vercel** - Need to redeploy to update JavaScript bundles  
🔄 **Action needed** - Trigger Vercel redeploy and clear browser cache

