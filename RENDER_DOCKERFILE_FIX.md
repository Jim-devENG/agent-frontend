# Fix: Dockerfile Not Found Error

## Problem

Render error: `failed to read dockerfile: open Dockerfile: no such file or directory`

## Solution

The Dockerfile exists at `backend/Dockerfile`, but Render settings need to be updated.

## Fix Steps

### Option 1: Update Dockerfile Path in Render (Recommended)

1. Go to **Render Dashboard** → **Backend Service** → **Settings**
2. Scroll to **Build & Deploy**
3. Find **Dockerfile Path**
4. **Current**: Probably empty or `./Dockerfile`
5. **Change to**: `backend/Dockerfile`
6. Click **Save Changes**
7. Go to **Manual Deploy** → **Deploy latest commit**

### Option 2: Switch to Python Build (No Docker)

If you prefer not to use Docker:

1. Go to **Settings** → **Build & Deploy**
2. Change **Environment** from "Docker" to **"Python 3"**
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Remove/clear **Dockerfile Path** and **Docker Build Context** fields
6. Click **Save Changes**
7. Deploy

## Current Status

✅ Dockerfile exists at: `backend/Dockerfile`  
✅ Code pushed to GitHub  
⚠️ Render settings need Dockerfile path updated

## After Fix

Once you update the Dockerfile path to `backend/Dockerfile` and redeploy, it should work!

