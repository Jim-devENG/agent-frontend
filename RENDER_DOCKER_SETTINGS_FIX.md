# Fix Render Docker Build Context Error

## Current Error
```
error: failed to calculate checksum of ref ... "/requirements.txt": not found
```

## Problem
The Dockerfile is found (`backend/Dockerfile`), but the **Docker Build Context Directory** is not set correctly. Docker is looking for `requirements.txt` in the root, but it's in `backend/`.

---

## Solution: Update Render Settings

### Step 1: Go to Render Dashboard

1. **Go to**: https://dashboard.render.com
2. **Click** your backend service

### Step 2: Update Build & Deploy Settings

1. **Go to**: Settings → Build & Deploy

2. **Set Dockerfile Path:**
   - **Dockerfile Path**: `backend/Dockerfile`
   - ✅ Should already be set (you fixed this)

3. **Set Docker Build Context Directory (IMPORTANT!):**
   - **Docker Build Context Directory**: `backend`
   - **This is critical!** Without this, Docker looks in the root directory

4. **Save Changes**
   - Click "Save Changes"
   - Render will automatically redeploy

---

## What This Does

When **Docker Build Context Directory** is set to `backend`:
- ✅ Docker builds from `backend/` directory
- ✅ `COPY requirements.txt .` will find `backend/requirements.txt`
- ✅ `COPY . .` will copy all files from `backend/` directory
- ✅ Everything works as expected

Without this setting:
- ❌ Docker builds from repo root
- ❌ `COPY requirements.txt .` looks in root (doesn't exist)
- ❌ Build fails

---

## After Fixing

Once you set "Docker Build Context Directory" to `backend`:

1. ✅ **Save changes** - Render will redeploy automatically
2. ✅ **Wait 2-5 minutes** for deployment
3. ✅ **Check logs** - Should see successful build
4. ✅ **Run migrations** - In Shell: `cd backend && alembic upgrade head`
5. ✅ **Test** - `https://agent-liquidcanvas.onrender.com/health/ready`

---

## Alternative: If You Can't Set Build Context Directory

If Render doesn't have a "Docker Build Context Directory" field, you need to update the Dockerfile to handle root context. But first, **check if the field exists** - it should be in Build & Deploy settings, sometimes called:
- "Docker Build Context"
- "Build Context Directory"
- "Docker Build Path"
- "Context Directory"

---

## Quick Checklist

- [ ] Dockerfile Path: `backend/Dockerfile` ✅ (already set)
- [ ] Docker Build Context Directory: `backend` ⚠️ **NEEDS TO BE SET**
- [ ] Save changes
- [ ] Wait for redeploy
- [ ] Check logs for successful build
- [ ] Run migrations
- [ ] Test endpoints

---

**Go to Render settings and set "Docker Build Context Directory" to `backend`!** This should fix the error. 🚀

