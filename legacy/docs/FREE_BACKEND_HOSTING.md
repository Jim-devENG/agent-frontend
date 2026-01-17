# Free Backend Hosting Options

This guide covers free hosting options for your FastAPI backend with scheduler.

## ⚠️ Important Considerations

Your backend needs:
- ✅ Persistent process (for APScheduler)
- ✅ Long-running tasks (scraping can take time)
- ✅ Database storage (SQLite is fine)
- ✅ Background jobs running 24/7

**Challenge**: Most free tiers have limitations that may affect schedulers.

---

## Option 1: Render (Recommended for Free Tier)

**Best balance of free features and functionality**

### Pros:
- ✅ **Free tier available**
- ✅ Supports Python/FastAPI
- ✅ Automatic SSL
- ✅ Custom domains
- ✅ Easy deployment from GitHub

### Cons:
- ⚠️ **Spins down after 15 minutes of inactivity**
- ⚠️ Cold start takes ~30 seconds
- ⚠️ Scheduler won't run when spun down

### Workaround:
Use external cron service (like cron-job.org) to ping your app every 10 minutes to keep it awake.

### Setup:
1. Sign up: https://render.com
2. New Web Service → Connect GitHub
3. Configure:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt && playwright install chromium`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables
5. Free tier: 750 hours/month (enough for always-on if kept awake)

### Keep-Alive Setup:
1. Sign up at https://cron-job.org (free)
2. Create cron job:
   - **URL**: `https://your-app.onrender.com/health`
   - **Schedule**: Every 10 minutes
   - **Method**: GET

**Cost**: FREE (with keep-alive ping)

---

## Option 2: Railway

**Good free credits, but limited**

### Pros:
- ✅ **$5 free credits/month** (usually enough for small apps)
- ✅ No spin-down (stays awake)
- ✅ Easy deployment
- ✅ Supports persistent processes

### Cons:
- ⚠️ Credits can run out (need to monitor)
- ⚠️ May need to upgrade after free credits

### Setup:
1. Sign up: https://railway.app
2. New Project → Deploy from GitHub
3. Configure:
   - **Root Directory**: `/`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables
5. Generate domain or add custom domain

**Cost**: FREE (up to $5/month in credits)

---

## Option 3: Fly.io

**Generous free tier**

### Pros:
- ✅ **3 shared-cpu VMs free**
- ✅ 3GB persistent storage
- ✅ 160GB outbound data transfer
- ✅ No spin-down
- ✅ Global edge network

### Cons:
- ⚠️ More complex setup
- ⚠️ Need to install Fly CLI

### Setup:
1. Sign up: https://fly.io
2. Install Fly CLI: https://fly.io/docs/getting-started/installing-flyctl/
3. Create `fly.toml` (I'll create this)
4. Deploy: `fly deploy`

**Cost**: FREE (generous limits)

---

## Option 4: PythonAnywhere

**Free tier for Python apps**

### Pros:
- ✅ **Free tier available**
- ✅ Python-focused
- ✅ Persistent processes
- ✅ Cron jobs supported

### Cons:
- ⚠️ Limited to 1 web app
- ⚠️ Only accessible from whitelisted domains
- ⚠️ Less modern platform

### Setup:
1. Sign up: https://www.pythonanywhere.com
2. Upload code via web interface or Git
3. Configure web app
4. Set up scheduled tasks

**Cost**: FREE (with limitations)

---

## Option 5: Google Cloud Run

**Free tier with generous limits**

### Pros:
- ✅ **2 million requests/month free**
- ✅ 400,000 GB-seconds compute
- ✅ 200,000 GiB-seconds memory
- ✅ Auto-scaling

### Cons:
- ⚠️ **Spins down after inactivity** (like Render)
- ⚠️ Cold starts
- ⚠️ More complex setup
- ⚠️ Need Google Cloud account

### Setup:
1. Sign up: https://cloud.google.com
2. Install gcloud CLI
3. Create Cloud Run service
4. Deploy container

**Cost**: FREE (within limits, then pay-as-you-go)

---

## Option 6: Replit

**Free tier but not ideal for production**

### Pros:
- ✅ Free tier
- ✅ Easy setup
- ✅ Always-on option (paid)

### Cons:
- ⚠️ Free tier spins down
- ⚠️ Not ideal for production
- ⚠️ Limited resources

**Not recommended** for production use.

---

## Comparison Table

| Service | Free Tier | Spin-Down | Scheduler Support | Difficulty | Recommendation |
|---------|-----------|-----------|-------------------|------------|----------------|
| **Render** | ✅ 750 hrs/month | ⚠️ Yes (15 min) | ⚠️ With keep-alive | ⭐ Easy | ⭐⭐⭐⭐ Best free option |
| **Railway** | ✅ $5 credits | ✅ No | ✅ Yes | ⭐ Easy | ⭐⭐⭐⭐ Good if credits last |
| **Fly.io** | ✅ 3 VMs | ✅ No | ✅ Yes | ⭐⭐ Medium | ⭐⭐⭐⭐⭐ Best for always-on |
| **PythonAnywhere** | ✅ Limited | ✅ No | ✅ Yes | ⭐⭐ Medium | ⭐⭐⭐ Works but dated |
| **Cloud Run** | ✅ Generous | ⚠️ Yes | ⚠️ With keep-alive | ⭐⭐⭐ Hard | ⭐⭐⭐ Complex setup |
| **Replit** | ✅ Limited | ⚠️ Yes | ⚠️ Limited | ⭐ Easy | ⭐ Not for production |

---

## Recommended: Render + Keep-Alive

**Best free option with workaround**

### Why Render?
- Easiest setup
- Good free tier
- Automatic SSL
- Easy to keep awake

### Setup Steps:

1. **Deploy to Render** (see RENDER_SETUP.md)
2. **Set up Keep-Alive**:
   - Use https://cron-job.org (free)
   - Ping `/health` endpoint every 10 minutes
   - Keeps app awake 24/7

3. **Alternative Keep-Alive Services**:
   - https://cron-job.org (free)
   - https://www.easycron.com (free tier)
   - https://uptimerobot.com (free tier)

**Result**: Free backend that stays awake!

---

## Alternative: Fly.io (Best Always-On Free Option)

**If you want true always-on without keep-alive**

### Why Fly.io?
- No spin-down
- Generous free tier
- True persistent processes
- Global edge network

### Setup Steps:

1. **Install Fly CLI**
2. **Create fly.toml** (I'll create this)
3. **Deploy**

**Result**: Free backend that never spins down!

---

## Quick Decision Guide

**Choose Render if:**
- ✅ You want the easiest setup
- ✅ You're okay with keep-alive ping
- ✅ You want automatic SSL

**Choose Fly.io if:**
- ✅ You want true always-on (no keep-alive needed)
- ✅ You're comfortable with CLI
- ✅ You want best free tier

**Choose Railway if:**
- ✅ You want easy setup
- ✅ $5/month credits are enough
- ✅ You can monitor usage

---

## Next Steps

1. **Choose your platform** (I recommend Render or Fly.io)
2. **See specific setup guide**:
   - `RENDER_SETUP.md` (for Render)
   - `FLYIO_SETUP.md` (for Fly.io)
   - `RAILWAY_SETUP.md` (for Railway)
3. **Deploy backend**
4. **Set up keep-alive** (if using Render)
5. **Deploy frontend to Vercel**
6. **Configure DNS**

Would you like me to create detailed setup guides for:
- Render (easiest)
- Fly.io (best always-on)
- Railway (good middle ground)

