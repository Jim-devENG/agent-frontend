# Troubleshooting Connection Timeout

## Problem
You're seeing `TimeoutError` when trying to connect to the database. This means the connection attempt is timing out before a connection can be established.

## Possible Causes

### 1. ❌ DATABASE_URL Still Using Port 5432 (Direct Connection)

**Check**: Verify your `DATABASE_URL` on Render uses port `6543`, not `5432`.

**How to Check:**
1. Go to Render Dashboard → Your Service → Environment tab
2. Find `DATABASE_URL`
3. Look for the port number after the hostname
4. Should be `:6543` NOT `:5432`

**Fix:**
Update `DATABASE_URL` to:
```
postgresql+asyncpg://postgres:L1qu%21dcvnvs@db.wlsbtxwbyqdagvrbkebl.supabase.co:6543/postgres?pgbouncer=true
```

### 2. ❌ Wrong Pooler Hostname Format

Supabase might use a **different hostname** for the connection pooler, not the same as direct connection.

**Check Supabase Dashboard:**
1. Go to: https://app.supabase.com
2. Your Project → Settings → Database
3. Scroll to "Connection Pooling"
4. Look for "Transaction Mode" connection string
5. **Copy the EXACT connection string shown**

**Common Formats:**
- **Format A (same hostname)**: `db.wlsbtxwbyqdagvrbkebl.supabase.co:6543`
- **Format B (pooler hostname)**: `aws-0-us-east-1.pooler.supabase.com:6543`
- **Format C (different format)**: `db.wlsbtxwbyqdagvrbkebl.pooler.supabase.co:6543`

**If Format B or C:**
- The hostname is **different** from the direct connection
- You **must** use the exact hostname from Supabase dashboard
- Update `DATABASE_URL` to use that hostname

### 3. ❌ Network Restrictions on Supabase

Supabase might have network restrictions blocking Render's IP addresses.

**Check:**
1. Go to Supabase Dashboard → Settings → Database
2. Look for "Network Restrictions" section
3. Check if there are any IP restrictions enabled
4. If yes, you need to:
   - Either add Render's IP addresses (if known)
   - Or temporarily allow all IPs to test
   - Or disable restrictions

**Note**: Render uses dynamic IPs, so IP whitelisting may not work reliably.

### 4. ❌ Connection String Format Issue

The connection string format might be incorrect for the pooler.

**Correct Format:**
```
postgresql+asyncpg://postgres:L1qu%21dcvnvs@[HOSTNAME]:6543/postgres?pgbouncer=true
```

**Check:**
- ✅ Has `+asyncpg` after `postgresql`
- ✅ Port is `6543` (not 5432)
- ✅ Has `?pgbouncer=true` (or `&pgbouncer=true` if other params exist)
- ✅ Password is URL-encoded: `L1qu%21dcvnvs` (not `L1qu!dcvnvs`)
- ✅ Username might need to be `postgres.[project-ref]` for some poolers

### 5. ❌ Supabase Pooler Not Enabled

Your Supabase project might not have connection pooling enabled.

**Check:**
1. Go to Supabase Dashboard → Settings → Database
2. Look for "Connection Pooling" section
3. If it says "Not Available" or you don't see it, you may need to:
   - Upgrade your Supabase plan
   - Contact Supabase support
   - Use alternative solution (IPv4 add-on or VPN)

## Diagnostic Steps

### Step 1: Check Logs for Connection Target

Look in Render logs for:
```
🔗 Attempting to connect to: [HOSTNAME]:[PORT]
```

**Verify:**
- Port should be `6543` (not 5432)
- Hostname should match what Supabase shows for pooler

### Step 2: Check for Pooler Detection Message

Look for this message in logs:
```
ℹ️  Using connection pooler (port 6543 or pooler hostname) - skipping IPv4 resolution (pooler handles IPv4)
```

**If you DON'T see this message:**
- The code isn't detecting it as a pooler connection
- Check that `DATABASE_URL` has `:6543` or `pgbouncer=true`
- Or hostname contains `.pooler.supabase.com`

### Step 3: Test Connection from Local Machine

Try connecting from your local machine to verify the pooler connection string works:

```bash
# Install psql if not installed
# Then test connection
psql "postgresql://postgres:L1qu!dcvnvs@db.wlsbtxwbyqdagvrbkebl.supabase.co:6543/postgres?pgbouncer=true"
```

**If this works locally but not on Render:**
- Network restrictions issue
- Render's IPs might be blocked

**If this fails locally too:**
- Connection string is wrong
- Pooler not enabled on your project
- Wrong hostname/credentials

### Step 4: Check Render Logs for Startup

Look for startup logs that show:
```
📊 RAW DATABASE_URL (masked): postgresql+asyncpg://postgres:****@...
```

**Verify:**
- URL format is correct
- Port shows `6543`
- Hostname is correct

## Solutions to Try

### Solution 1: Use Exact Connection String from Supabase

1. **Copy the EXACT connection string** from Supabase dashboard (Connection Pooling → Transaction Mode)
2. **Convert it** to `postgresql+asyncpg://` format if needed
3. **Update** `DATABASE_URL` on Render with this exact string
4. **Redeploy** and test

### Solution 2: Try Different Pooler Hostname

If Supabase shows a different hostname for pooler (like `aws-0-[region].pooler.supabase.com`):

1. **Get the hostname** from Supabase dashboard
2. **Construct new connection string**:
   ```
   postgresql+asyncpg://postgres.[PROJECT_REF]:L1qu%21dcvnvs@aws-0-[REGION].pooler.supabase.com:6543/postgres
   ```
3. **Update** `DATABASE_URL` on Render
4. **Note**: Username might need to be `postgres.[project-ref]` format for pooler hostname

### Solution 3: Contact Supabase Support

If nothing works:
1. **Contact Supabase Support** via: https://supabase.com/support
2. **Ask them**:
   - Is connection pooling enabled for your project?
   - What is the correct pooler connection string for your project?
   - Are there any network restrictions blocking Render's IPs?
   - Is there an IPv4 add-on available?

### Solution 4: Use Supabase IPv4 Add-On (Paid)

If pooler doesn't work:
1. **Enable IPv4 Add-On** in Supabase (Settings → Add-ons)
2. **Get IPv4 address** after activation
3. **Set `SUPABASE_IPV4`** environment variable with the IPv4 address
4. **Redeploy**

## Quick Checklist

- [ ] Verified `DATABASE_URL` uses port `6543` (not 5432)
- [ ] Verified `DATABASE_URL` has `pgbouncer=true` parameter
- [ ] Checked Supabase dashboard for exact pooler connection string
- [ ] Compared hostname in `DATABASE_URL` with Supabase pooler hostname
- [ ] Checked for network restrictions on Supabase
- [ ] Verified connection string format is correct
- [ ] Tested connection locally with `psql`
- [ ] Checked Render logs for connection target details
- [ ] Saw "Using connection pooler" message in logs

## Most Likely Issue

Based on the timeout error, **the most likely issue is**:

1. **DATABASE_URL is still using port 5432** instead of 6543
2. **Wrong pooler hostname** - Supabase uses a different hostname for pooler
3. **Network restrictions** blocking Render's IPs

**Next Step**: Check your Supabase dashboard for the EXACT pooler connection string and use that exact format.

---

**Please share:**
1. What port number is in your current `DATABASE_URL`? (5432 or 6543?)
2. What does Supabase dashboard show for "Transaction Mode" connection string?
3. What hostname does it show? (is it `db.wlsbtxwbyqdagvrbkebl.supabase.co` or something else like `aws-0-...pooler.supabase.com`?)

This will help me give you the exact connection string to use!

