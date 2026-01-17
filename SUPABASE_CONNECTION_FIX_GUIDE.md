# Complete Guide: Fixing Supabase Database Connection on Render

## 📋 Table of Contents
1. [Understanding the Problem](#understanding-the-problem)
2. [Current Status](#current-status)
3. [Solution Options](#solution-options)
4. [Method 1: Using SUPABASE_IPV4 Environment Variable (Recommended)](#method-1-using-supabase_ipv4-environment-variable-recommended)
5. [Method 2: Using Supabase Connection Pooler](#method-2-using-supabase-connection-pooler)
6. [Method 3: Direct IPv4 Address in Connection String](#method-3-direct-ipv4-address-in-connection-string)
7. [Verification Steps](#verification-steps)
8. [Troubleshooting](#troubleshooting)

---

## Understanding the Problem

### What's Happening
Your Render deployment is trying to connect to Supabase PostgreSQL database, but:
- **DNS Resolution Fails**: Render's network cannot resolve the Supabase hostname (`db.wlsbtxwbyqdagvrbkebl.supabase.co`) to an IPv4 address
- **IPv6 Not Available**: The hostname resolves to IPv6, but Render cannot reach IPv6 addresses
- **Error**: `[Errno -5] No address associated with hostname` or `[Errno 101] Network is unreachable`

### Why This Happens
- Supabase databases are hosted on cloud infrastructure that may primarily use IPv6
- Render's network may have DNS resolution issues or IPv6 connectivity limitations
- DNS queries at import time might fail before network is fully initialized

---

## Current Status

### ✅ What We've Fixed
1. **Removed import-time DNS resolution** - DNS resolution now happens at runtime when engine is created
2. **Added retry logic** - 5 attempts with exponential backoff (1s, 2s, 4s, 8s, 16s)
3. **Added fallback methods** - Falls back to `gethostbyname` if `getaddrinfo` fails
4. **Added timeout protection** - 5-second timeout per DNS attempt
5. **Added environment variable support** - `SUPABASE_IPV4` can be used as last resort

### ⚠️ What Still Needs Configuration
- The DNS resolution is still failing, so we need to provide the IPv4 address manually

---

## Solution Options

You have **3 methods** to fix this. We recommend **Method 1** (easiest and most reliable):

1. **Method 1**: Use `SUPABASE_IPV4` environment variable (Recommended ✅)
2. **Method 2**: Use Supabase Connection Pooler on port 6543
3. **Method 3**: Embed IPv4 directly in connection string (not recommended)

---

## Method 1: Using SUPABASE_IPV4 Environment Variable (Recommended)

This is the **easiest and most reliable** method. We'll find the IPv4 address and set it as an environment variable.

### Step 1: Find Your Supabase Database IPv4 Address

You have several ways to find the IPv4 address:

#### Option A: Using Command Line (If you have access to a local machine)

**On Windows (PowerShell):**
```powershell
nslookup db.wlsbtxwbyqdagvrbkebl.supabase.co
```

**On Windows (Command Prompt):**
```cmd
nslookup db.wlsbtxwbyqdagvrbkebl.supabase.co
```

**On Mac/Linux:**
```bash
nslookup db.wlsbtxwbyqdagvrbkebl.supabase.co
# OR
dig +short db.wlsbtxwbyqdagvrbkebl.supabase.co A
```

Look for the **A record** (IPv4 address). It will look something like:
```
Name:    db.wlsbtxwbyqdagvrbkebl.supabase.co
Address:  54.xxx.xxx.xxx
```

#### Option B: Using Online DNS Lookup Tools

1. Go to: https://mxtoolbox.com/SuperTool.aspx?action=a%3adb.wlsbtxwbyqdagvrbkebl.supabase.co
2. Or: https://www.whatsmydns.net/#A/db.wlsbtxwbyqdagvrbkebl.supabase.co
3. Look for the **A record** (IPv4 address)

#### Option C: Using Python Script (If you have Python installed)

Create a temporary file `find_ip.py`:
```python
import socket
try:
    hostname = "db.wlsbtxwbyqdagvrbkebl.supabase.co"
    ipv4 = socket.gethostbyname(hostname)
    print(f"IPv4 Address: {ipv4}")
except Exception as e:
    print(f"Error: {e}")
```

Run it:
```bash
python find_ip.py
```

#### Option D: Contact Supabase Support

If none of the above work, contact Supabase support and ask for the IPv4 address of your database instance.

### Step 2: Set Environment Variable on Render

Once you have the IPv4 address (e.g., `54.xxx.xxx.xxx`), follow these steps:

1. **Log in to Render Dashboard**
   - Go to: https://dashboard.render.com
   - Sign in with your account

2. **Navigate to Your Backend Service**
   - Click on your backend service (likely named something like "agent-liquidcanvas" or "liquidcanvas-backend")

3. **Go to Environment Variables**
   - Click on the **"Environment"** tab in the left sidebar
   - Or scroll down to the **"Environment Variables"** section

4. **Add New Environment Variable**
   - Click **"Add Environment Variable"** or **"Add"** button
   - In the **"Key"** field, enter: `SUPABASE_IPV4`
   - In the **"Value"** field, enter your IPv4 address (e.g., `54.xxx.xxx.xxx`)
   - **DO NOT** include any quotes, ports, or protocols - just the IP address
   - Click **"Save Changes"**

5. **Verify the Variable**
   - You should see `SUPABASE_IPV4` in your environment variables list
   - Make sure there are no extra spaces or characters

6. **Redeploy Your Service**
   - Render will automatically redeploy when you save environment variables
   - Or manually click **"Manual Deploy"** → **"Deploy latest commit"**
   - Wait for deployment to complete (usually 2-5 minutes)

### Step 3: Verify It's Working

After deployment, check your Render logs:

1. Go to your service dashboard
2. Click on **"Logs"** tab
3. Look for these log messages:
   ```
   🔍 Resolving db.wlsbtxwbyqdagvrbkebl.supabase.co to IPv4 address...
   ⚠️  DNS resolution failed (attempt 1/5): ...
   ...
   ⚠️  Using SUPABASE_IPV4 environment variable: 54.xxx.xxx.xxx
   ✅ Using IPv4 from SUPABASE_IPV4 env var: 54.xxx.xxx.xxx:5432
   ✅ Async engine created successfully
   ✅ Database connection test passed
   ```

If you see `✅ Database connection test passed`, you're done! 🎉

---

## Method 2: Using Supabase Connection Pooler

Supabase provides a connection pooler that may have better IPv4 support. This uses port **6543** instead of **5432**.

### Step 1: Get Your Pooler Connection String from Supabase

1. **Log in to Supabase Dashboard**
   - Go to: https://app.supabase.com
   - Sign in with your account

2. **Select Your Project**
   - Click on your project (likely named something related to "liquidcanvas")

3. **Go to Database Settings**
   - Click **"Settings"** in the left sidebar
   - Click **"Database"** under Settings

4. **Find Connection Pooling**
   - Look for **"Connection Pooling"** section
   - Find the **"Connection String"** for **"Transaction Mode"** or **"Session Mode"**
   - It should look like:
     ```
     postgresql://postgres:[YOUR-PASSWORD]@db.wlsbtxwbyqdagvrbkebl.supabase.co:6543/postgres
     ```

5. **Copy the Pooler URL**
   - The pooler URL uses port **6543** (not 5432)
   - Note: The pooler URL might have a different hostname format

### Step 2: Update Your Render Environment Variable

1. **Log in to Render Dashboard**
   - Go to: https://dashboard.render.com

2. **Navigate to Your Backend Service**
   - Click on your backend service

3. **Update DATABASE_URL**
   - Go to **"Environment"** tab
   - Find the `DATABASE_URL` variable
   - Click **"Edit"** (pencil icon)

4. **Modify the Connection String**
   - Change the port from `5432` to `6543`
   - Ensure the format is: `postgresql+asyncpg://postgres:L1qu%21dcvnvs@db.wlsbtxwbyqdagvrbkebl.supabase.co:6543/postgres?sslmode=require`
   - **IMPORTANT**: Keep the `+asyncpg` after `postgresql`
   - **IMPORTANT**: Keep the URL-encoded password (`L1qu%21dcvnvs` which is `L1qu!dcvnvs`)
   - **IMPORTANT**: Keep `?sslmode=require` at the end (our code will strip it, but it helps identify SSL requirement)

5. **Save Changes**
   - Click **"Save Changes"**
   - Wait for automatic redeploy

### Step 3: Verify It's Working

Check Render logs for:
```
✅ Configured SSL for Supabase connection
✅ Async engine created successfully
✅ Database connection test passed
```

**Note**: The pooler may have different connection limits. If you encounter connection limit errors, you may need to adjust pool settings in your code or use Method 1 instead.

---

## Method 3: Direct IPv4 Address in Connection String

This method embeds the IPv4 address directly in the `DATABASE_URL`. **Not recommended** because IP addresses can change, but it will work if Methods 1 and 2 don't.

### Step 1: Find IPv4 Address

Follow **Step 1 of Method 1** to find your IPv4 address.

### Step 2: Update DATABASE_URL on Render

1. **Log in to Render Dashboard**
   - Go to: https://dashboard.render.com

2. **Navigate to Your Backend Service**
   - Click on your backend service

3. **Update DATABASE_URL**
   - Go to **"Environment"** tab
   - Find `DATABASE_URL`
   - Click **"Edit"**

4. **Replace Hostname with IPv4**
   - **OLD**: `postgresql+asyncpg://postgres:L1qu%21dcvnvs@db.wlsbtxwbyqdagvrbkebl.supabase.co:5432/postgres?sslmode=require`
   - **NEW**: `postgresql+asyncpg://postgres:L1qu%21dcvnvs@54.xxx.xxx.xxx:5432/postgres?sslmode=require`
   - Replace `54.xxx.xxx.xxx` with your actual IPv4 address
   - Keep everything else the same

5. **Save Changes**
   - Click **"Save Changes"**
   - Wait for redeploy

### Step 3: Verify

Check logs for successful connection.

**⚠️ Warning**: If Supabase changes the IP address, your connection will break. You'll need to update the `DATABASE_URL` again. Method 1 is safer because the code will try DNS first, then fall back to the environment variable.

---

## Verification Steps

After implementing any method, verify everything is working:

### 1. Check Render Logs

Look for these success indicators:
```
✅ Async engine created successfully
✅ Database connection test passed
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:10000
```

### 2. Test API Endpoint

Try accessing your health check endpoint:
```bash
curl https://agent-liquidcanvas.onrender.com/health
```

Or visit in browser:
```
https://agent-liquidcanvas.onrender.com/health
```

Expected response:
```json
{
  "status": "ready",
  "database": "connected"
}
```

### 3. Check Database Connection Diagnostic Endpoint

We have a special diagnostic endpoint:
```bash
curl https://agent-liquidcanvas.onrender.com/health/connection-string
```

This will show you:
- What hostname/IP the backend is trying to connect to
- Whether DNS resolution succeeded
- SSL configuration status

### 4. Test Actual Database Queries

If you have any API endpoints that query the database, test them:
```bash
curl https://agent-liquidcanvas.onrender.com/api/pipeline/status
```

If it returns data instead of errors, you're good! ✅

---

## Troubleshooting

### Problem: Still Getting DNS Resolution Errors

**Solution**: 
- Make sure you set `SUPABASE_IPV4` correctly (no quotes, no spaces, just IP)
- Verify the IP address is correct using `nslookup` or online tools
- Check Render logs to see if the environment variable is being read

### Problem: Connection Timeout

**Possible Causes**:
1. Wrong IP address
2. Firewall blocking connection
3. Supabase IP changed

**Solution**:
- Re-verify the IP address using Method 1, Step 1
- Try Method 2 (Connection Pooler) instead
- Contact Supabase support if IP keeps changing

### Problem: SSL Certificate Errors

**Solution**:
- Ensure `?sslmode=require` is in your connection string (our code handles this)
- Our code automatically configures SSL via `connect_args`, so SSL should work

### Problem: Authentication Failed

**Solution**:
- Verify your password is correctly URL-encoded: `L1qu!dcvnvs` → `L1qu%21dcvnvs`
- Check that the username is `postgres`
- Verify database name is `postgres` (not something else)

### Problem: Environment Variable Not Found

**Solution**:
- Make sure variable name is exactly `SUPABASE_IPV4` (case-sensitive)
- Ensure you saved the environment variable
- Redeploy the service after adding the variable
- Check Render logs to see if variable is visible (it won't show the value for security)

### Problem: Connection Works But Queries Fail

**Possible Causes**:
1. Schema mismatch (missing tables/columns)
2. Permissions issue
3. Database not fully initialized

**Solution**:
- Check if migrations ran successfully
- Verify database schema matches your models
- Check Supabase logs for permission errors

---

## Quick Reference: Connection Strings

### Current (Direct Connection - Port 5432)
```
postgresql+asyncpg://postgres:L1qu%21dcvnvs@db.wlsbtxwbyqdagvrbkebl.supabase.co:5432/postgres?sslmode=require
```

### With IPv4 (Method 3)
```
postgresql+asyncpg://postgres:L1qu%21dcvnvs@54.xxx.xxx.xxx:5432/postgres?sslmode=require
```

### With Pooler (Method 2 - Port 6543)
```
postgresql+asyncpg://postgres:L1qu%21dcvnvs@db.wlsbtxwbyqdagvrbkebl.supabase.co:6543/postgres?sslmode=require
```

**Note**: Replace `54.xxx.xxx.xxx` with your actual IPv4 address.

---

## Next Steps After Fix

Once your connection is working:

1. ✅ **Monitor Logs**: Watch Render logs for the first few hours to ensure stability
2. ✅ **Test All Features**: Test your API endpoints to ensure database queries work
3. ✅ **Set Up Alerts**: Configure Render alerts for deployment failures
4. ✅ **Document**: Update your team documentation with the connection setup

---

## Support

If you're still having issues after trying all methods:

1. **Check Render Status**: https://status.render.com
2. **Check Supabase Status**: https://status.supabase.com
3. **Render Support**: https://render.com/docs/support
4. **Supabase Support**: https://supabase.com/docs/guides/platform/support

---

## Summary: Recommended Approach

**For most users, we recommend Method 1 (SUPABASE_IPV4 environment variable)**:

1. Find IPv4 using `nslookup db.wlsbtxwbyqdagvrbkebl.supabase.co`
2. Set `SUPABASE_IPV4=54.xxx.xxx.xxx` in Render environment variables
3. Redeploy service
4. Verify in logs

This is the safest and most maintainable solution. The code will automatically use this IP if DNS resolution fails.

---

**Last Updated**: Based on your current codebase (commit 3b9ff9f)
**Code Location**: `backend/app/db/database.py` - `_resolve_to_ipv4_sync()` function

