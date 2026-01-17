# Deploy Frontend to Vercel - Step by Step

This guide walks you through deploying the Next.js frontend to Vercel.

## Prerequisites

- ✅ Vercel account (free): https://vercel.com/signup
- ✅ GitHub account (free): https://github.com
- ✅ Code pushed to GitHub repository

## Step 1: Push Code to GitHub

### If you don't have a GitHub repo yet:

```bash
# In your project root
git init
git add .
git commit -m "Initial commit - Art Outreach Scraper"

# Create a new repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### If you already have a repo:

```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push
```

## Step 2: Connect to Vercel

1. **Go to Vercel**: https://vercel.com
2. **Sign in** (or create account)
3. **Click "Add New Project"**
4. **Import Git Repository**:
   - Connect GitHub (authorize if needed)
   - Select your repository
   - Click "Import"

## Step 3: Configure Project Settings

**Important Settings:**

- **Framework Preset**: Next.js (auto-detected)
- **Root Directory**: `frontend` ⚠️ **IMPORTANT!**
- **Build Command**: `npm run build` (default)
- **Output Directory**: `.next` (default)
- **Install Command**: `npm install` (default)

**Click "Deploy"**

## Step 4: Configure Environment Variables

After first deployment, go to **Settings → Environment Variables**:

Add:
```
NEXT_PUBLIC_API_BASE_URL=https://api.agent.liquidcanvas.art/api/v1
```

**Or if backend is on same domain:**
```
NEXT_PUBLIC_API_BASE_URL=https://agent.liquidcanvas.art/api/v1
```

**Important**: 
- Variable name must start with `NEXT_PUBLIC_` to be available in browser
- Redeploy after adding variables

## Step 5: Add Custom Domain

1. **Go to Project → Settings → Domains**
2. **Add Domain**: `agent.liquidcanvas.art`
3. **Vercel will show DNS instructions**

### DNS Configuration in Wix:

**Option A: CNAME (Recommended)**
- In Wix DNS, add:
  - **Type**: CNAME
  - **Name**: `agent`
  - **Value**: `cname.vercel-dns.com` (or what Vercel shows)

**Option B: A Records**
- Vercel will provide IP addresses
- Add A records in Wix pointing to those IPs

4. **Wait for DNS propagation** (5-30 minutes)
5. **Vercel will automatically provision SSL**

## Step 6: Redeploy with Environment Variables

After adding environment variables:
1. Go to **Deployments** tab
2. Click **"..."** on latest deployment
3. Click **"Redeploy"**
4. This ensures new env vars are included

## Step 7: Verify Deployment

1. **Check Vercel deployment**: Should show "Ready"
2. **Visit**: https://agent.liquidcanvas.art
3. **Test API calls**: Check browser console for errors
4. **Verify SSL**: Should show green lock icon

## Step 8: Configure API Proxy (If Backend on Same Domain)

If you want backend on same domain (`agent.liquidcanvas.art/api`), add `vercel.json` to project root:

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://api.agent.liquidcanvas.art/api/:path*"
    }
  ]
}
```

This proxies `/api/*` requests to your backend.

## Troubleshooting

### Build Fails

**Error: "Cannot find module"**
- Check Root Directory is set to `frontend`
- Verify `package.json` exists in frontend folder

**Error: "Build timeout"**
- Upgrade Vercel plan (if on free tier)
- Optimize build (remove unused dependencies)

### Environment Variables Not Working

- Must start with `NEXT_PUBLIC_`
- Redeploy after adding variables
- Check in browser: `console.log(process.env.NEXT_PUBLIC_API_BASE_URL)`

### DNS Not Working

- Wait longer (up to 48 hours, usually 5-30 min)
- Verify DNS record in Wix
- Check DNS propagation: https://dnschecker.org

### CORS Errors

- Backend CORS must include `https://agent.liquidcanvas.art`
- Check backend `.env` file
- Restart backend after updating CORS

## Continuous Deployment

Vercel automatically deploys on every push to main branch:

```bash
git add .
git commit -m "Update frontend"
git push
# Vercel automatically deploys!
```

## Vercel CLI (Optional)

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
cd frontend
vercel

# Deploy to production
vercel --prod
```

## Next Steps

After frontend is on Vercel:

1. ✅ Deploy backend to VPS (see DEPLOYMENT_STEPS.md)
2. ✅ Configure backend CORS to include Vercel domain
3. ✅ Test full application
4. ✅ Monitor both services

## Cost

**Vercel Free Tier Includes:**
- ✅ 100GB bandwidth/month
- ✅ Unlimited deployments
- ✅ Automatic SSL
- ✅ Custom domains
- ✅ Global CDN

**Should be sufficient** for most applications!

