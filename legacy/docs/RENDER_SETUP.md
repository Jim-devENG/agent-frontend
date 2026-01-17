# Deploy Backend to Render (Free Tier)

Step-by-step guide to deploy your FastAPI backend to Render with free tier.

## Prerequisites

- ✅ Render account: https://render.com/signup
- ✅ GitHub repository with your code
- ✅ Code pushed to GitHub

## Step 1: Prepare Your Code

Make sure your code is ready:

```bash
# Verify requirements.txt exists
cat requirements.txt

# Verify main.py exists
ls main.py
```

## Step 2: Push to GitHub

If not already done:

```bash
git add .
git commit -m "Prepare for Render deployment"
git push
```

## Step 3: Create Render Account

1. Go to https://render.com
2. Click **"Get Started for Free"**
3. Sign up with GitHub (recommended) or email

## Step 4: Create New Web Service

1. **Dashboard** → Click **"New +"**
2. Select **"Web Service"**
3. **Connect GitHub** (if not connected):
   - Authorize Render
   - Select your repository
4. **Select your repository**

## Step 5: Configure Service

Fill in the settings:

### Basic Settings:
- **Name**: `art-outreach-backend` (or your choice)
- **Region**: Choose closest to you
- **Branch**: `main` (or your default branch)
- **Root Directory**: Leave empty (or `/` if your backend is in root)

### Build & Deploy:
- **Environment**: `Python 3`
- **Build Command**:
  ```bash
  pip install -r requirements.txt && playwright install chromium
  ```
- **Start Command**:
  ```bash
  uvicorn main:app --host 0.0.0.0 --port $PORT
  ```

### Plan:
- **Free** (select this)

## Step 6: Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add all variables from your `.env` file:

```
DEBUG=False
HOST=0.0.0.0
PORT=$PORT
CORS_ORIGINS=["https://agent.liquidcanvas.art","https://www.liquidcanvas.art"]
DATABASE_URL=sqlite:///./art_outreach.db
GEMINI_API_KEY=your_key_here
# ... add all other variables
```

**Important**:
- `PORT` is automatically set by Render (use `$PORT` in start command)
- `CORS_ORIGINS` should include your frontend domain
- Don't commit `.env` file to GitHub

## Step 7: Deploy

1. Click **"Create Web Service"**
2. Render will:
   - Clone your repo
   - Install dependencies
   - Build your app
   - Start the service

3. **Watch the logs** for any errors

## Step 8: Get Your URL

After deployment:
- Render provides a URL like: `https://art-outreach-backend.onrender.com`
- This is your backend API URL

## Step 9: Set Up Keep-Alive (Important!)

**Render free tier spins down after 15 minutes of inactivity.**

To keep it awake 24/7:

### Option A: cron-job.org (Free)

1. Sign up: https://cron-job.org
2. Create new cron job:
   - **Title**: Keep Render Alive
   - **URL**: `https://your-app.onrender.com/health`
   - **Schedule**: Every 10 minutes
   - **Request Method**: GET
   - **Save**

### Option B: UptimeRobot (Free)

1. Sign up: https://uptimerobot.com
2. Add Monitor:
   - **Monitor Type**: HTTP(s)
   - **URL**: `https://your-app.onrender.com/health`
   - **Interval**: 5 minutes
   - **Save**

### Option C: EasyCron (Free Tier)

1. Sign up: https://www.easycron.com
2. Create cron job:
   - **URL**: `https://your-app.onrender.com/health`
   - **Schedule**: `*/10 * * * *` (every 10 minutes)

**Result**: Your app stays awake 24/7!

## Step 10: Add Custom Domain (Optional)

1. **Service Settings** → **Custom Domains**
2. **Add Domain**: `api.agent.liquidcanvas.art`
3. **Follow DNS instructions**:
   - Add CNAME record in Wix
   - Point to Render's provided hostname
4. **Wait for SSL** (automatic, takes a few minutes)

## Step 11: Update Frontend

Update your frontend environment variable:

```env
NEXT_PUBLIC_API_BASE_URL=https://your-app.onrender.com/api/v1
```

Or if using custom domain:
```env
NEXT_PUBLIC_API_BASE_URL=https://api.agent.liquidcanvas.art/api/v1
```

## Step 12: Verify Deployment

### Test Backend:
```bash
# Health check
curl https://your-app.onrender.com/health

# API endpoint
curl https://your-app.onrender.com/api/v1/stats
```

### Test from Browser:
- Visit: `https://your-app.onrender.com/docs` (FastAPI docs)
- Should show Swagger UI

## Troubleshooting

### Build Fails

**Error: "Module not found"**
- Check `requirements.txt` includes all dependencies
- Verify Python version compatibility

**Error: "Playwright install fails"**
- Build command should include: `playwright install chromium`
- May take longer on first build

### App Spins Down

**Scheduler not running:**
- Set up keep-alive ping (see Step 9)
- First request after spin-down takes ~30 seconds

### Database Issues

**SQLite file not persisting:**
- Render free tier doesn't persist files between deployments
- Consider upgrading to paid plan for persistent disk
- Or use external database (PostgreSQL on Render, free tier available)

### CORS Errors

**Frontend can't connect:**
- Verify `CORS_ORIGINS` includes frontend domain
- Check environment variables are set correctly
- Restart service after updating env vars

### Port Issues

**Error: "Address already in use"**
- Always use `$PORT` in start command
- Render sets this automatically

## Free Tier Limits

- ✅ 750 hours/month (enough for always-on if kept awake)
- ✅ 512 MB RAM
- ✅ Automatic SSL
- ⚠️ Spins down after 15 min inactivity (use keep-alive)
- ⚠️ Cold start ~30 seconds

## Upgrade Options

If you need:
- **Persistent disk** (for SQLite): $7/month
- **More RAM**: $7/month
- **No spin-down**: $7/month

## Next Steps

1. ✅ Backend deployed to Render
2. ✅ Keep-alive set up
3. ✅ Frontend deployed to Vercel
4. ✅ DNS configured
5. ✅ Test full application

## Cost

**Total**: FREE (with keep-alive service)

- Render: Free tier
- Keep-alive: Free (cron-job.org, UptimeRobot, etc.)
- Frontend: Free (Vercel)

**Perfect for getting started!**

