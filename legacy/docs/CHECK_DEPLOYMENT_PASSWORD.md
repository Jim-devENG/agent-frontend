# How to Check Your Current Backend Password

## If Backend is on Render

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Select your backend service** (the FastAPI/backend service)
3. **Go to "Environment" tab**
4. **Look for these variables**:
   - `ADMIN_USERNAME`
   - `ADMIN_PASSWORD`
   - `JWT_SECRET_KEY`

The password shown there is what's currently active in your deployed backend.

## If Backend is on Other Platforms

### Railway
1. Go to https://railway.app
2. Select your project → Backend service
3. Go to "Variables" tab
4. Check `ADMIN_PASSWORD`

### Fly.io
1. Go to https://fly.io
2. Run: `fly secrets list` in your project directory
3. Look for `ADMIN_PASSWORD`

### VPS/Server
1. SSH into your server
2. Check the `.env` file or environment variables
3. Or check systemd service file for environment variables

## Generate New Password

If you want to set a new password:

### Option 1: Use the Generator Script
```powershell
py generate_auth.py
```

This will show you a new password. Then:

1. **Copy the password** from the output
2. **Go to your deployment platform** (Render/Railway/etc.)
3. **Update the `ADMIN_PASSWORD` environment variable**
4. **Redeploy** (or restart the service)

### Option 2: Set Manually

1. **Generate a secure password** (or use the script)
2. **Update in your deployment platform**:
   - Render: Environment tab → Edit `ADMIN_PASSWORD`
   - Railway: Variables tab → Edit `ADMIN_PASSWORD`
   - Fly.io: `fly secrets set ADMIN_PASSWORD=your_password`
3. **Redeploy/restart** the service

## Important Notes

⚠️ **The password in your local `.env` file is NOT the same as the deployed password** unless you've manually set them to match.

⚠️ **After redeploying**, the backend uses whatever environment variables are set in your hosting platform, not your local `.env` file.

## Quick Check

To see what's currently in your local `.env`:
```powershell
Get-Content .env | Select-String -Pattern "ADMIN"
```

But remember: **Your deployed backend uses the environment variables from your hosting platform, not your local `.env` file.**

