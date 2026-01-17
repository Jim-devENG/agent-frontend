# Deploy Backend to Railway (Free Credits)

Step-by-step guide to deploy your FastAPI backend to Railway with free monthly credits.

## Prerequisites

- ✅ Railway account: https://railway.app
- ✅ GitHub repository with your code
- ✅ Code pushed to GitHub

## Step 1: Create Railway Account

1. Go to https://railway.app
2. Click **"Start a New Project"**
3. Sign up with GitHub (recommended)

## Step 2: Create New Project

1. **Dashboard** → Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. **Authorize Railway** (if first time)
4. **Select your repository**

## Step 3: Configure Service

Railway will auto-detect Python, but we'll configure it:

### Settings:
- **Root Directory**: `/` (or leave empty if backend is in root)
- **Build Command**: 
  ```bash
  pip install -r requirements.txt && playwright install chromium
  ```
- **Start Command**:
  ```bash
  uvicorn main:app --host 0.0.0.0 --port $PORT
  ```

### Environment Variables:
Click **"Variables"** tab and add:

```
DEBUG=False
HOST=0.0.0.0
PORT=$PORT
CORS_ORIGINS=["https://agent.liquidcanvas.art","https://www.liquidcanvas.art"]
DATABASE_URL=sqlite:///./art_outreach.db
GEMINI_API_KEY=your_key_here
# ... add all other variables
```

**Note**: `$PORT` is automatically set by Railway.

## Step 4: Deploy

1. Railway will automatically:
   - Clone your repo
   - Install dependencies
   - Build your app
   - Start the service

2. **Watch the logs** for deployment progress

## Step 5: Get Your URL

After deployment:
- Railway provides a URL like: `https://your-app.up.railway.app`
- This is your backend API URL

## Step 6: Add Custom Domain (Optional)

1. **Settings** → **Domains**
2. **Generate Domain** (free Railway domain)
   - Or **Add Custom Domain**: `api.agent.liquidcanvas.art`
3. **Follow DNS instructions**:
   - Add CNAME record in Wix
   - Point to Railway's provided hostname
4. **Wait for SSL** (automatic)

## Step 7: Update Frontend

Update your frontend environment variable:

```env
NEXT_PUBLIC_API_BASE_URL=https://your-app.up.railway.app/api/v1
```

Or if using custom domain:
```env
NEXT_PUBLIC_API_BASE_URL=https://api.agent.liquidcanvas.art/api/v1
```

## Step 8: Verify Deployment

### Test Backend:
```bash
# Health check
curl https://your-app.up.railway.app/health

# API endpoint
curl https://your-app.up.railway.app/api/v1/stats
```

### Test from Browser:
- Visit: `https://your-app.up.railway.app/docs` (FastAPI docs)

## Free Tier Details

- ✅ **$5 free credits/month**
- ✅ **No spin-down** (stays awake)
- ✅ **Automatic SSL**
- ✅ **Custom domains**
- ✅ **Persistent storage**

**Note**: Credits are usually enough for small apps, but monitor usage.

## Monitoring Usage

1. **Dashboard** → View usage
2. **Settings** → **Usage** → See credit consumption
3. Set up alerts if needed

## Troubleshooting

### Build Fails

**Error: "Module not found"**
- Check `requirements.txt` includes all dependencies
- Verify Python version

**Error: "Playwright install fails"**
- Build command should include: `playwright install chromium`
- May take longer on first build

### App Not Starting

**Check logs:**
- Click on service → **Logs** tab
- Look for errors

**Common issues:**
- Wrong start command
- Missing environment variables
- Port configuration

### Credits Running Out

**Monitor usage:**
- Dashboard shows credit consumption
- Upgrade to paid plan if needed ($5/month minimum)

### Database Issues

**SQLite not persisting:**
- Railway free tier has ephemeral storage
- Consider upgrading for persistent disk
- Or use Railway PostgreSQL (free tier available)

## Upgrade Options

If you need:
- **More credits**: $5/month minimum
- **Persistent storage**: Included in paid plans
- **More resources**: Scale up in settings

## Next Steps

1. ✅ Backend deployed to Railway
2. ✅ Custom domain configured
3. ✅ Frontend deployed to Vercel
4. ✅ DNS configured
5. ✅ Test full application

## Cost

**Total**: FREE (up to $5/month in credits)

- Railway: $5 free credits/month
- Frontend: Free (Vercel)

**Good option if credits are sufficient!**

