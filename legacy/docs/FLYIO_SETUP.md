# Deploy Backend to Fly.io (Free Tier - Always On)

Step-by-step guide to deploy your FastAPI backend to Fly.io with true always-on free tier.

## Prerequisites

- ✅ Fly.io account: https://fly.io/app/sign-up
- ✅ GitHub repository with your code
- ✅ Fly CLI installed (we'll do this)

## Step 1: Install Fly CLI

### Windows (PowerShell):

```powershell
# Using winget
winget install --id=flyctl.flyctl

# Or download from: https://fly.io/docs/getting-started/installing-flyctl/
```

### Or Download:
1. Go to https://fly.io/docs/getting-started/installing-flyctl/
2. Download Windows installer
3. Run installer

### Verify Installation:
```bash
flyctl version
```

## Step 2: Login to Fly.io

```bash
flyctl auth login
```

This opens a browser to authenticate.

## Step 3: Prepare Your Code

Make sure you have:
- `requirements.txt`
- `main.py`
- All dependencies

## Step 4: Create fly.toml

I'll create this file for you. It configures your Fly.io app.

## Step 5: Initialize Fly App

```bash
# In your project root
flyctl launch
```

This will:
- Ask for app name (or generate one)
- Ask for region (choose closest)
- Ask to deploy now (say no, we'll configure first)

## Step 6: Configure fly.toml

The generated `fly.toml` will be created. We'll customize it.

## Step 7: Set Secrets (Environment Variables)

```bash
# Set each environment variable
flyctl secrets set DEBUG=False
flyctl secrets set CORS_ORIGINS='["https://agent.liquidcanvas.art","https://www.liquidcanvas.art"]'
flyctl secrets set DATABASE_URL=sqlite:///./art_outreach.db
flyctl secrets set GEMINI_API_KEY=your_key_here
# ... add all other secrets
```

**Or set from file:**
```bash
# Create secrets file (don't commit to git!)
flyctl secrets import < .env
```

## Step 8: Deploy

```bash
flyctl deploy
```

This will:
- Build your app
- Deploy to Fly.io
- Provide a URL like: `https://your-app.fly.dev`

## Step 9: Verify Deployment

```bash
# Check status
flyctl status

# View logs
flyctl logs

# Test health endpoint
curl https://your-app.fly.dev/health
```

## Step 10: Add Custom Domain

```bash
# Add domain
flyctl domains add api.agent.liquidcanvas.art

# Follow DNS instructions
# Add CNAME record in Wix pointing to Fly.io hostname
```

## Step 11: Configure Persistent Storage (Optional)

For SQLite database persistence:

```bash
# Create volume
flyctl volumes create data --size 1

# Update fly.toml to mount volume (I'll show this)
```

## Free Tier Limits

- ✅ **3 shared-cpu VMs** (1 app can use all 3)
- ✅ **3GB persistent storage**
- ✅ **160GB outbound data/month**
- ✅ **No spin-down** (always on!)
- ✅ **Global edge network**

**Perfect for your scheduler!**

## Troubleshooting

### Build Fails

```bash
# Check logs
flyctl logs

# Rebuild
flyctl deploy --no-cache
```

### App Not Starting

```bash
# Check status
flyctl status

# View logs
flyctl logs

# SSH into app
flyctl ssh console
```

### Database Not Persisting

- Create volume (see Step 11)
- Update fly.toml to mount volume
- Redeploy

## Useful Commands

```bash
# Deploy
flyctl deploy

# View logs
flyctl logs

# Check status
flyctl status

# SSH into app
flyctl ssh console

# Scale app
flyctl scale count 1

# View secrets
flyctl secrets list
```

## Next Steps

1. ✅ Backend deployed to Fly.io
2. ✅ Custom domain configured
3. ✅ Frontend deployed to Vercel
4. ✅ DNS configured
5. ✅ Test full application

## Cost

**Total**: FREE (within generous limits)

- Fly.io: Free tier (3 VMs, 3GB storage, 160GB transfer)
- Frontend: Free (Vercel)

**Best free always-on option!**

