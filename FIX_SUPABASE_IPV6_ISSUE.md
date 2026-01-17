# Fix: Supabase IPv6 Connection Issue

## Problem
Your Supabase database hostname (`db.wlsbtxwbyqdagvrbkebl.supabase.co`) **only resolves to IPv6**, not IPv4. Render cannot connect to IPv6 addresses, so the connection fails.

**Current Error:**
- `SUPABASE_IPV4=192.168.156.253` is set (this is your local DNS server, NOT the database IP)
- Hostname resolves to IPv6 only: `2a05:d018:135e:167f:9ee3:668a:b264:6d39`
- Connection fails with "Network is unreachable"

## Solution: Use Supabase Connection Pooler (Port 6543)

Supabase provides a connection pooler called **Supavisor** that supports **both IPv4 and IPv6**. This is the recommended solution.

---

## Step-by-Step Fix

### Step 1: Get Connection Pooler URL from Supabase Dashboard

1. **Log in to Supabase Dashboard**
   - Go to: https://app.supabase.com
   - Sign in with your account

2. **Select Your Project**
   - Click on your project (the one with database `db.wlsbtxwbyqdagvrbkebl.supabase.co`)

3. **Navigate to Database Settings**
   - Click **"Settings"** in the left sidebar (gear icon)
   - Click **"Database"** under Settings

4. **Find Connection Pooling Section**
   - Scroll down to find **"Connection Pooling"** section
   - You'll see different connection modes:
     - **Transaction Mode** (port 6543) ← **Use this one**
     - **Session Mode** (port 5432)

5. **Copy Transaction Mode Connection String**
   - Look for **"Transaction Mode"** connection string
   - It should look like:
     ```
     postgresql://postgres.[project-ref]:[YOUR-PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres
     ```
   - **OR** it might be:
     ```
     postgresql://postgres:[YOUR-PASSWORD]@db.wlsbtxwbyqdagvrbkebl.supabase.co:6543/postgres?pgbouncer=true
     ```
   - The key is: **port 6543** and it might have a different hostname

6. **Extract the Components**
   - **Hostname**: Could be `aws-0-[region].pooler.supabase.com` or similar
   - **Port**: `6543`
   - **Username**: `postgres` or `postgres.[project-ref]`
   - **Password**: `L1qu!dcvnvs` (your password)
   - **Database**: `postgres`

### Step 2: Update DATABASE_URL on Render

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com
   - Sign in

2. **Open Your Backend Service**
   - Click on your backend service (e.g., "agent-liquidcanvas")

3. **Go to Environment Variables**
   - Click **"Environment"** tab in the left sidebar

4. **Find DATABASE_URL**
   - Look for the `DATABASE_URL` variable
   - Click the **"Edit"** button (pencil icon)

5. **Update the Connection String**
   
   **Option A: If pooler uses same hostname with port 6543**
   ```
   postgresql+asyncpg://postgres:L1qu%21dcvnvs@db.wlsbtxwbyqdagvrbkebl.supabase.co:6543/postgres?pgbouncer=true
   ```
   - Change port from `5432` to `6543`
   - Add `?pgbouncer=true` parameter
   - Keep `+asyncpg` after `postgresql`
   - Keep URL-encoded password: `L1qu%21dcvnvs`

   **Option B: If pooler uses different hostname (e.g., aws-0-us-east-1.pooler.supabase.com)**
   ```
   postgresql+asyncpg://postgres.L1qu%21dcvnvs@aws-0-us-east-1.pooler.supabase.com:6543/postgres
   ```
   - Use the pooler hostname from Supabase dashboard
   - Port: `6543`
   - Username might be `postgres.[project-ref]` - check Supabase dashboard
   - Password: URL-encoded

6. **Remove SUPABASE_IPV4 Variable (if it exists)**
   - Find `SUPABASE_IPV4` environment variable
   - Click **"Delete"** or remove it (it's not needed anymore)
   - The value `192.168.156.253` was incorrect anyway

7. **Save Changes**
   - Click **"Save Changes"**
   - Render will automatically redeploy (wait 2-5 minutes)

### Step 3: Verify It's Working

After deployment completes:

1. **Check Render Logs**
   - Go to **"Logs"** tab
   - Look for:
     ```
     ✅ Configured SSL for Supabase connection
     ✅ Async engine created successfully
     ✅ Database connection test passed
     ```

2. **Test Health Endpoint**
   - Visit: https://agent-liquidcanvas.onrender.com/health
   - Should return: `{"status":"ready","database":"connected"}`

3. **Test API Endpoints**
   - Try any endpoint that queries the database
   - Should return data instead of errors

---

## Alternative Solution: Enable IPv4 Add-On (Paid)

If you prefer to use direct connection (port 5432) instead of the pooler:

1. **Go to Supabase Dashboard**
   - Settings → Add-ons
   - Enable **"IPv4 Add-On"**
   - **Note**: This is a paid feature (adds cost to your Supabase plan)

2. **Wait for Activation**
   - Supabase will assign an IPv4 address to your database
   - This may take a few minutes

3. **Find New IPv4 Address**
   - After activation, your hostname will resolve to IPv4
   - Use `nslookup` again to get the IPv4 address
   - Set `SUPABASE_IPV4` with the correct IP

**However, using the Connection Pooler (Method 1) is recommended because:**
- ✅ It's free
- ✅ Better for connection pooling
- ✅ Already supports IPv4
- ✅ No additional cost

---

## Quick Reference: Connection Strings

### Current (Not Working - Direct IPv6 Only)
```
postgresql+asyncpg://postgres:L1qu%21dcvnvs@db.wlsbtxwbyqdagvrbkebl.supabase.co:5432/postgres?sslmode=require
```

### Recommended (Connection Pooler - IPv4 Compatible)
```
postgresql+asyncpg://postgres:L1qu%21dcvnvs@db.wlsbtxwbyqdagvrbkebl.supabase.co:6543/postgres?pgbouncer=true
```
**OR** (if different hostname):
```
postgresql+asyncpg://postgres:[PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres
```

**Note**: Replace `[PASSWORD]` with your actual password (URL-encoded: `L1qu%21dcvnvs`)

---

## Troubleshooting

### Problem: Can't find Connection Pooling section in Supabase

**Solution**: 
- Make sure you're on the **Settings → Database** page
- Scroll down - it's usually near the bottom
- If you still can't find it, your project might be on an older plan - contact Supabase support

### Problem: Pooler connection string has different format

**Solution**:
- Copy the exact connection string from Supabase dashboard
- Convert it to `postgresql+asyncpg://` format (add `+asyncpg`)
- Ensure password is URL-encoded (`!` becomes `%21`)
- Port should be `6543`

### Problem: Still getting connection errors after switching to pooler

**Solution**:
1. Check that you're using port `6543` (not `5432`)
2. Verify the hostname is correct (from Supabase dashboard)
3. Check that password is correctly URL-encoded
4. Ensure SSL is still configured (our code handles this automatically)
5. Check Render logs for specific error messages

### Problem: Pooler says "too many connections"

**Solution**:
- Connection pooler has connection limits
- Check your pool size settings in `backend/app/db/database.py`
- Current settings: `pool_size=10, max_overflow=20`
- You might need to reduce these for the pooler

---

## Summary

**The Problem**: Supabase direct connections use IPv6 only. Render can't reach IPv6.

**The Solution**: Use Supabase Connection Pooler (port 6543) which supports IPv4.

**Steps**:
1. Get pooler connection string from Supabase dashboard
2. Update `DATABASE_URL` on Render to use port 6543
3. Remove incorrect `SUPABASE_IPV4` variable
4. Redeploy and verify

**This should fix your connection issue!** ✅

