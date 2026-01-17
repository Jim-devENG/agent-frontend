# Vercel Deployment Guide for agent.liquidcanvas.art

Vercel is excellent for Next.js frontends, but your FastAPI backend needs a different solution. Here are your options:

## Option 1: Hybrid Deployment (Recommended)

**Frontend on Vercel** + **Backend on VPS**

This gives you the best of both worlds:
- ✅ Fast, global CDN for frontend (Vercel)
- ✅ Full control for backend with scheduler (VPS)
- ✅ Cost-effective

### Setup:

1. **Deploy Frontend to Vercel**
   - Connect your GitHub repo to Vercel
   - Configure environment variables
   - Deploy

2. **Deploy Backend to VPS**
   - Use the VPS deployment guide for backend only
   - Point frontend API calls to backend URL

3. **Configure DNS**
   - Frontend: `agent.liquidcanvas.art` → Vercel
   - Backend: `api.agent.liquidcanvas.art` → VPS (or use subdomain)

## Option 2: Full Vercel (With Limitations)

**Frontend on Vercel** + **Backend as Vercel Serverless Functions**

⚠️ **Limitations:**
- Scheduler jobs won't work (serverless functions are stateless)
- Long-running scraping tasks may timeout
- Background jobs need external service (like VPS or separate worker)

### If You Choose This:

You'd need to:
1. Convert FastAPI to Vercel serverless functions (major refactoring)
2. Use external service for scheduled jobs (separate VPS or cloud function)
3. Handle database connections carefully (serverless)

**Not recommended** for this application due to scheduler requirements.

## Option 3: Vercel Frontend + Railway/Render Backend

**Frontend on Vercel** + **Backend on Railway or Render**

- Railway: https://railway.app (supports Python/FastAPI)
- Render: https://render.com (supports Python/FastAPI)

Both can run your FastAPI backend with persistent processes.

---

## Recommended: Hybrid Deployment

Let's set up **Frontend on Vercel** + **Backend on VPS**.

### Step 1: Prepare Frontend for Vercel

The frontend is already configured for production. Just need to:

1. **Update API URL** for production
2. **Configure environment variables in Vercel**
3. **Deploy**

### Step 2: Deploy Backend to VPS

Follow the VPS deployment guide for backend only (simpler setup).

### Step 3: Configure DNS

- **Frontend**: `agent.liquidcanvas.art` → Vercel
- **Backend**: `api.agent.liquidcanvas.art` → VPS (or use same domain with `/api` path)

---

## Detailed: Vercel Frontend Deployment

### Prerequisites

1. **Vercel Account**: Sign up at https://vercel.com
2. **GitHub Repository**: Push your code to GitHub (or GitLab/Bitbucket)

### Step 1: Prepare Repository

```bash
# Make sure frontend is ready
cd frontend
npm run build  # Should work without errors
```

### Step 2: Push to GitHub

```bash
# Initialize git if not already
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

### Step 3: Deploy to Vercel

1. **Go to Vercel Dashboard**: https://vercel.com/dashboard
2. **Click "Add New Project"**
3. **Import your GitHub repository**
4. **Configure Project**:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend` (important!)
   - **Build Command**: `npm run build` (or leave default)
   - **Output Directory**: `.next` (or leave default)

### Step 4: Configure Environment Variables

In Vercel project settings → Environment Variables, add:

```
NEXT_PUBLIC_API_BASE_URL=https://api.agent.liquidcanvas.art/api/v1
```

Or if backend is on same domain:
```
NEXT_PUBLIC_API_BASE_URL=https://agent.liquidcanvas.art/api/v1
```

### Step 5: Configure Custom Domain

1. **In Vercel Project** → Settings → Domains
2. **Add Domain**: `agent.liquidcanvas.art`
3. **Follow DNS instructions**:
   - Add CNAME record in Wix: `agent` → `cname.vercel-dns.com`
   - Or add A records as shown by Vercel

### Step 6: Deploy Backend Separately

Deploy backend to VPS following `DEPLOYMENT_STEPS.md`, but:
- Only deploy backend (not frontend)
- Use subdomain like `api.agent.liquidcanvas.art` for backend
- Or serve backend on same domain at `/api` path

---

## Alternative: Backend on Railway/Render

If you prefer not to manage a VPS:

### Railway (Recommended for Backend)

1. **Sign up**: https://railway.app
2. **New Project** → Deploy from GitHub
3. **Select your repo**
4. **Configure**:
   - Root Directory: `/` (backend root)
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **Add Environment Variables** (from `.env`)
6. **Generate Domain**: Railway provides a domain
7. **Custom Domain**: Add `api.agent.liquidcanvas.art` in Railway settings

### Render (Alternative)

1. **Sign up**: https://render.com
2. **New Web Service**
3. **Connect GitHub repo**
4. **Configure**:
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **Add Environment Variables**
6. **Custom Domain**: Add `api.agent.liquidcanvas.art`

---

## DNS Configuration for Hybrid Setup

### Option A: Separate Subdomains

**In Wix DNS:**
- `agent` → CNAME → Vercel (for frontend)
- `api.agent` → A Record → VPS IP (for backend)

**Result:**
- Frontend: https://agent.liquidcanvas.art (Vercel)
- Backend: https://api.agent.liquidcanvas.art (VPS)

### Option B: Same Domain, Different Paths

**In Wix DNS:**
- `agent` → CNAME → Vercel

**Vercel Configuration:**
- Add rewrite rule to proxy `/api/*` to backend VPS

**Result:**
- Frontend: https://agent.liquidcanvas.art (Vercel)
- Backend: https://agent.liquidcanvas.art/api/v1 (proxied to VPS)

---

## Cost Comparison

### Option 1: Hybrid (Vercel + VPS)
- **Vercel**: Free tier (sufficient for most apps)
- **VPS**: $6-12/month (DigitalOcean)
- **Total**: ~$6-12/month

### Option 2: Full VPS
- **VPS**: $6-12/month
- **Total**: ~$6-12/month

### Option 3: Vercel + Railway
- **Vercel**: Free tier
- **Railway**: $5/month (hobby plan)
- **Total**: ~$5/month

---

## Recommendation

**For your use case (scraper with scheduler):**

**Best Option**: **Vercel (Frontend) + VPS (Backend)**

**Why:**
- ✅ Scheduler needs persistent process (VPS)
- ✅ Scraping can be long-running (VPS)
- ✅ Full control over backend (VPS)
- ✅ Fast, global frontend (Vercel)
- ✅ Cost-effective

**Setup:**
1. Deploy frontend to Vercel → `agent.liquidcanvas.art`
2. Deploy backend to VPS → `api.agent.liquidcanvas.art`
3. Configure frontend to call backend API

Would you like me to create specific deployment guides for:
- Vercel frontend deployment?
- Railway backend deployment?
- Render backend deployment?

