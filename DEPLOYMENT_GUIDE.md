# Deployment Guide - Phase 9

## Overview

This guide covers deploying the complete application to production:
- **Backend API**: Render Web Service
- **Worker**: Render Background Worker
- **Frontend**: Vercel
- **Database**: Render PostgreSQL
- **Queue**: Render Redis

## Prerequisites

1. GitHub repository with all code
2. Render account (free tier available)
3. Vercel account (free tier available)
4. All API keys configured

## Step 1: Deploy PostgreSQL Database (Render)

1. Go to Render Dashboard → New → PostgreSQL
2. Name: `art-outreach-db`
3. Database: `art_outreach`
4. User: `art_outreach` (or auto-generated)
5. Note the **Internal Database URL** (for Render services)
6. Note the **External Connection String** (for local development)

## Step 2: Deploy Redis (Render)

1. Go to Render Dashboard → New → Redis
2. Name: `art-outreach-redis`
3. Note the **Internal Redis URL** (for Render services)
4. Note the **External Redis URL** (for local development)

## Step 3: Deploy Backend API (Render)

1. Go to Render Dashboard → New → Web Service
2. Connect your GitHub repository
3. Configure:
   - **Name**: `art-outreach-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add Environment Variables:
   ```
   DATABASE_URL=<Internal PostgreSQL URL from Step 1>
   REDIS_URL=<Internal Redis URL from Step 2>
   DATAFORSEO_LOGIN=your_email@example.com
   DATAFORSEO_PASSWORD=your_password
   HUNTER_IO_API_KEY=your_api_key
   GEMINI_API_KEY=your_api_key
   GMAIL_ACCESS_TOKEN=your_token (or)
   GMAIL_REFRESH_TOKEN=your_refresh_token
   GMAIL_CLIENT_ID=your_client_id
   GMAIL_CLIENT_SECRET=your_client_secret
   JWT_SECRET_KEY=<generate secure random string>
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=<secure password>
   ```
5. Deploy

## Step 4: Run Database Migrations

After backend deploys, run migrations:

1. SSH into Render shell or use Render's shell
2. Run:
   ```bash
   cd backend
   alembic upgrade head
   ```

Or add to build command:
```bash
pip install -r requirements.txt && alembic upgrade head
```

## Step 5: Deploy Worker (Render)

1. Go to Render Dashboard → New → Background Worker
2. Connect same GitHub repository
3. Configure:
   - **Name**: `art-outreach-worker`
   - **Root Directory**: `worker`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python worker.py`
4. Add same Environment Variables as backend (except JWT_SECRET_KEY, ADMIN_*)
5. Deploy

## Step 6: Deploy Frontend (Vercel)

1. Go to Vercel Dashboard → Add New Project
2. Import GitHub repository
3. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (or leave default)
   - **Output Directory**: `.next` (default)
4. Add Environment Variables:
   ```
   NEXT_PUBLIC_API_BASE_URL=https://art-outreach-backend.onrender.com/api
   ```
5. Deploy

## Step 7: Update DNS (If Using Custom Domain)

1. In Vercel: Add custom domain `agent.liquidcanvas.art`
2. Update DNS records in Wix:
   - A record: `agent` → Vercel IP
   - Or CNAME: `agent` → Vercel domain

## Step 8: Verify Deployment

1. **Backend**: Visit `https://your-backend.onrender.com/docs`
2. **Frontend**: Visit `https://agent.liquidcanvas.art` (or Vercel URL)
3. **Login**: Use admin credentials
4. **Test**: Create a discovery job and verify it processes

## Environment Variables Summary

### Backend/Worker (Render)
```
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
DATAFORSEO_LOGIN=...
DATAFORSEO_PASSWORD=...
HUNTER_IO_API_KEY=...
GEMINI_API_KEY=...
GMAIL_REFRESH_TOKEN=...
GMAIL_CLIENT_ID=...
GMAIL_CLIENT_SECRET=...
JWT_SECRET_KEY=...
ADMIN_USERNAME=...
ADMIN_PASSWORD=...
```

### Frontend (Vercel)
```
NEXT_PUBLIC_API_BASE_URL=https://your-backend.onrender.com/api
```

## Troubleshooting

### Backend not starting
- Check logs in Render dashboard
- Verify all environment variables are set
- Check database connection string

### Worker not processing jobs
- Verify Redis URL is correct
- Check worker logs
- Ensure worker is running (not sleeping)

### Frontend can't connect to backend
- Verify `NEXT_PUBLIC_API_BASE_URL` is correct
- Check CORS settings in backend
- Verify backend is running

### Database migration errors
- Run migrations manually via Render shell
- Check database connection
- Verify Alembic is configured correctly

## Cost Estimate (Free Tier)

- **Render PostgreSQL**: Free (limited)
- **Render Redis**: Free (limited)
- **Render Web Service**: Free (spins down after inactivity)
- **Render Worker**: Free (spins down after inactivity)
- **Vercel**: Free (generous limits)

**Total**: $0/month (with limitations)

## Production Considerations

For production use:
1. Upgrade to paid Render plans for always-on services
2. Use managed database (Render PostgreSQL Pro)
3. Set up monitoring (Sentry, LogDNA)
4. Configure backups
5. Set up alerts

