# Railway Backend Deployment Guide

Railway is the easiest way to deploy your FastAPI backend and works great with Supabase.

## Why Railway?

- ✅ **Easy FastAPI deployment** - Auto-detects and deploys
- ✅ **Great Supabase integration** - Works seamlessly
- ✅ **Simple pricing** - Pay as you go
- ✅ **GitHub integration** - Auto-deploys on push
- ✅ **Environment variables** - Easy to manage
- ✅ **No code changes needed** - Your existing code works

## Step 1: Sign Up for Railway

1. Go to https://railway.app
2. Click **"Start a New Project"**
3. Sign up with GitHub (recommended)
4. Authorize Railway to access your repositories

## Step 2: Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose repository: `liquidcanvasvideos/agent.liquidcanvas`
4. Click **"Deploy Now"**

## Step 3: Configure Project

Railway will auto-detect it's a Python project. Configure:

### Settings:
- **Root Directory**: `backend`
- **Build Command**: (auto-detected, usually `pip install -r requirements.txt`)
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Environment Variables:
Click **"Variables"** tab and add:

```
DATABASE_URL=postgresql://postgres:L1qu!dcvnvs@db.wlsbtxwbyqdagvrbkebl.supabase.co:5432/postgres
PORT=8000
AUTO_MIGRATE=true
```

Add any other environment variables your backend needs (API keys, etc.)

## Step 4: Deploy

1. Railway will automatically:
   - Install dependencies
   - Run migrations (if AUTO_MIGRATE=true)
   - Start the server

2. **Check deployment logs** for:
   - ✅ `Database connectivity verified`
   - ✅ `Database migrations completed successfully`
   - ✅ `Server starting up...`

## Step 5: Get Your Backend URL

1. Railway will generate a URL like: `https://your-app.railway.app`
2. You can also add a custom domain in **Settings → Domains**

## Step 6: Update Frontend API URL

Update your frontend to point to the new Railway backend:

1. **In Vercel** (or wherever frontend is hosted):
   - Go to **Environment Variables**
   - Update `NEXT_PUBLIC_API_BASE_URL`:
     ```
     NEXT_PUBLIC_API_BASE_URL=https://your-app.railway.app/api
     ```

2. **Redeploy frontend**

## Step 7: Test Everything

1. **Backend Health**:
   ```bash
   curl https://your-app.railway.app/api/health
   ```

2. **Database Connection**:
   - Check Railway logs for "Database connectivity verified"
   - Check Supabase Table Editor for tables

3. **API Endpoints**:
   ```bash
   curl https://your-app.railway.app/api/prospects
   ```

## Railway vs Render

| Feature | Railway | Render |
|--------|---------|--------|
| FastAPI Support | ✅ Auto-detects | ✅ Manual config |
| Supabase Integration | ✅ Excellent | ✅ Works |
| Pricing | Pay as you go | Free tier then $7/mo |
| Deployment Speed | Fast | Medium |
| Ease of Use | Very Easy | Easy |

## Troubleshooting

### Build Fails
- Check `requirements.txt` is in `backend/` directory
- Check Python version (Railway auto-detects)

### Database Connection Fails
- Verify `DATABASE_URL` is correct
- Check Supabase project is running
- Check Railway logs for specific error

### Migrations Don't Run
- Set `AUTO_MIGRATE=true` in environment variables
- Or run manually: `railway run alembic upgrade head`

## Cost Estimate

**Railway Free Tier**:
- $5 credit per month
- Usually enough for small-medium apps
- Pay only for what you use

**Railway Pricing**:
- ~$0.000463 per GB-hour of RAM
- ~$0.000231 per GB-hour of CPU
- Very affordable for most apps

## Next Steps After Deployment

1. ✅ Backend deployed on Railway
2. ✅ Connected to Supabase database
3. ✅ Migrations applied
4. ✅ Update frontend API URL
5. ✅ Test all endpoints
6. ✅ (Optional) Delete Render backend to save costs

## Benefits of Railway + Supabase

- ✅ **Database**: Supabase (free tier, 500MB)
- ✅ **Backend**: Railway (pay as you go, very affordable)
- ✅ **Frontend**: Vercel (free tier)
- ✅ **Total Cost**: ~$0-5/month (vs $7+/month on Render)

Your backend is now on Railway, database on Supabase! 🎉

