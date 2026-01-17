# How to Update Hunter.io API Key

## Your New API Key
**Key:** `b8b197dff80f8cc991db92a6a37653c467c8b952`

## Method 1: Update in Render Dashboard (Production)

### Step 1: Access Render Dashboard
1. Go to **https://dashboard.render.com**
2. Sign in to your account
3. Find your backend service (usually named `agent-backend` or `agent-liquidcanvas`)

### Step 2: Navigate to Environment Variables
1. Click on your **backend service** to open it
2. In the left sidebar, click **"Environment"**
3. You'll see a list of current environment variables

### Step 3: Update HUNTER_IO_API_KEY
1. Find the existing `HUNTER_IO_API_KEY` variable in the list
2. Click on it to edit
3. Replace the old value with: `b8b197dff80f8cc991db92a6a37653c467c8b952`
4. Click **"Save Changes"**

**OR** if the variable doesn't exist:
1. Click **"Add Environment Variable"**
2. **Key:** `HUNTER_IO_API_KEY`
3. **Value:** `b8b197dff80f8cc991db92a6a37653c467c8b952`
4. Click **"Save Changes"**

### Step 4: Restart Service
After updating the environment variable:
1. Render will automatically restart your service
2. Wait for the deployment to complete (usually 1-2 minutes)
3. The new API key will be active

## Method 2: Update Locally (Development)

If you're running the backend locally:

1. Navigate to your backend directory:
   ```powershell
   cd C:\Users\MIKENZY\Documents\Apps\liquidcanvas\backend
   ```

2. Open or create `.env` file:
   ```powershell
   # If .env doesn't exist, create it
   if (!(Test-Path .env)) { New-Item .env -ItemType File }
   ```

3. Update the API key:
   ```powershell
   # Remove old key if exists
   (Get-Content .env) | Where-Object { $_ -notmatch "^HUNTER_IO_API_KEY" } | Set-Content .env
   
   # Add new key
   Add-Content .env "HUNTER_IO_API_KEY=b8b197dff80f8cc991db92a6a37653c467c8b952"
   ```

4. Restart your backend server for changes to take effect

## Verify the Update

After updating, you can verify it's working:

1. Go to your app's **Settings** page
2. Find **Hunter.io** service
3. Click **"Test"** button
4. It should show "connected" status if the key is valid

## Important Notes

- ⚠️ **The new API key is a Pro account key** - this should give you much higher rate limits (50,000 searches/month vs the previous free tier limits)
- ✅ **No code changes needed** - the system automatically uses the environment variable
- 🔄 **Service restart required** - Render will auto-restart, but if running locally, you need to manually restart
- 🔒 **Keep your API key secure** - Never commit it to git or share it publicly

## Troubleshooting

**"Hunter.io API key not configured"**
- Verify the environment variable name is exactly `HUNTER_IO_API_KEY` (case-sensitive)
- Make sure there are no extra spaces in the value
- Restart the backend service after updating

**"Rate limit exceeded" errors persist**
- Wait a few minutes after updating - the old key might still be cached
- Check that the new key is actually a Pro account key in your Hunter.io dashboard
- Verify the key is correct by testing it in the Settings page

