# Quick Start: Fix Supabase Connection in 5 Minutes

## 🎯 Goal
Get your Supabase database connection working on Render by providing the IPv4 address directly.

---

## Step 1: Find Your IPv4 Address (2 minutes)

### Option A: Using PowerShell (Windows)
Open PowerShell and run:
```powershell
nslookup db.wlsbtxwbyqdagvrbkebl.supabase.co
```

Look for the line that says:
```
Address:  54.xxx.xxx.xxx
```
That's your IPv4 address. Copy it.

### Option B: Using Online Tool
1. Go to: https://mxtoolbox.com/SuperTool.aspx?action=a%3adb.wlsbtxwbyqdagvrbkebl.supabase.co
2. Look for the **A record** showing an IPv4 address (4 numbers separated by dots)
3. Copy the IP address

### Option C: Using Command Prompt (Windows)
Open Command Prompt (cmd) and run:
```cmd
nslookup db.wlsbtxwbyqdagvrbkebl.supabase.co
```

Copy the IPv4 address you see.

---

## Step 2: Set Environment Variable on Render (2 minutes)

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com
   - Sign in

2. **Find Your Backend Service**
   - Click on your backend service (usually named something like "agent-liquidcanvas")

3. **Open Environment Variables**
   - Click **"Environment"** in the left sidebar
   - Or scroll to **"Environment Variables"** section

4. **Add New Variable**
   - Click **"Add Environment Variable"** or **"Add"** button
   - **Key**: `SUPABASE_IPV4`
   - **Value**: Paste your IPv4 address (e.g., `54.xxx.xxx.xxx`)
     - ⚠️ **IMPORTANT**: No quotes, no spaces, just the IP address
     - Example: `54.123.45.67` ✅
     - NOT: `"54.123.45.67"` ❌
     - NOT: `54.123.45.67 ` (with space) ❌

5. **Save**
   - Click **"Save Changes"**
   - Render will automatically redeploy (takes 2-5 minutes)

---

## Step 3: Verify It Works (1 minute)

1. **Wait for Deployment**
   - Render will show "Deploying..." then "Live" when done
   - Usually takes 2-5 minutes

2. **Check Logs**
   - Click **"Logs"** tab in Render dashboard
   - Look for these messages:
     ```
     🔍 Resolving db.wlsbtxwbyqdagvrbkebl.supabase.co to IPv4 address...
     ⚠️  Using SUPABASE_IPV4 environment variable: 54.xxx.xxx.xxx
     ✅ Using IPv4 from SUPABASE_IPV4 env var: 54.xxx.xxx.xxx:5432
     ✅ Async engine created successfully
     ✅ Database connection test passed
     ```

3. **Test API**
   - Visit: https://agent-liquidcanvas.onrender.com/health
   - Should return: `{"status":"ready","database":"connected"}`

---

## ✅ Done!

If you see `✅ Database connection test passed` in the logs, you're all set!

---

## ⚠️ Troubleshooting

### Still Getting Errors?

1. **Double-check the IP address**
   - Make sure it's correct (4 numbers, separated by dots)
   - Try looking it up again

2. **Check Environment Variable**
   - Make sure variable name is exactly `SUPABASE_IPV4` (case-sensitive)
   - Make sure value has no quotes or spaces

3. **Wait for Redeploy**
   - After adding the variable, wait 2-5 minutes for deployment to complete

4. **Check Logs Again**
   - Look for any error messages
   - Make sure you see the "Using SUPABASE_IPV4" message

### Need More Help?

See the full detailed guide: `SUPABASE_CONNECTION_FIX_GUIDE.md`

