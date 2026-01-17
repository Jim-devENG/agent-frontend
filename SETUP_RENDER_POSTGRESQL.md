# Complete Guide: Setting Up Render PostgreSQL

## Step 1: Create New Render PostgreSQL Database

1. **Go to Render Dashboard:**
   - Visit: https://dashboard.render.com
   - Sign in with your account

2. **Create New PostgreSQL Database:**
   - Click the **"New +"** button (top right)
   - Select **"PostgreSQL"** from the dropdown

3. **Configure Database:**
   - **Name**: Give it a name (e.g., `liquidcanvas-db` or `agent-db`)
   - **Database**: Leave default (or name it `postgres`)
   - **User**: Leave default (or name it `postgres`)
   - **Region**: Choose **same region** as your backend service (important for performance)
     - If your backend is in Oregon, choose Oregon
     - If your backend is in Frankfurt, choose Frankfurt
   - **PostgreSQL Version**: Choose latest (usually 15 or 16)
   - **Plan**: Select **"Free"** (for testing) or **"Starter"** ($7/month for production)
   - Click **"Create Database"**

4. **Wait for Creation:**
   - Render will take 2-3 minutes to create the database
   - You'll see a "Creating..." status

---

## Step 2: Get the Connection String

Once the database is created:

1. **Click on Your Database:**
   - Find your new database in the dashboard
   - Click on its name to open details

2. **Copy Connection String:**
   - Look for **"Connection Pooling"** section (at the top)
   - Or scroll down to **"Connections"** section
   - You'll see:
     - **"Internal Database URL"** (for services on Render)
     - **"External Database URL"** (for local/other services)
   
   **For Render backend service, use "Internal Database URL":**
   - It looks like: `postgresql://user:password@dpg-xxxxx-a.oregon-postgres.render.com:5432/dbname`
   - **OR** if using connection pooling: `postgresql://user:password@dpg-xxxxx-a-pooler.oregon-postgres.render.com:5432/dbname`
   
   **Copy the entire connection string** (including password)

3. **Convert to asyncpg format:**
   - Change `postgresql://` to `postgresql+asyncpg://`
   - Example:
     ```
     postgresql+asyncpg://user:password@dpg-xxxxx-a.oregon-postgres.render.com:5432/dbname
     ```

---

## Step 3: Update Your Backend Service

1. **Go to Your Backend Service:**
   - In Render dashboard, find your backend service (e.g., "agent-liquidcanvas")
   - Click on it

2. **Update Environment Variables:**
   - Click **"Environment"** tab
   - Find `DATABASE_URL` variable
   - Click **"Edit"** (pencil icon)

3. **Replace the Value:**
   - Delete the old Supabase connection string
   - Paste the new Render PostgreSQL connection string
   - Make sure it starts with `postgresql+asyncpg://`
   - Click **"Save Changes"**

4. **Verify:**
   - Make sure the `DATABASE_URL` is saved correctly
   - The connection string should look like:
     ```
     postgresql+asyncpg://postgres:xxxxx@dpg-xxxxx-a.oregon-postgres.render.com:5432/postgres
     ```

---

## Step 4: Delete Old Database (Optional)

If you want to delete the old corrupted database:

1. **Find Old Database:**
   - In Render dashboard, look for your old PostgreSQL database
   - If you don't see it, it might already be deleted

2. **Delete Database:**
   - Click on the old database
   - Go to **"Settings"** tab (or look for delete option)
   - Scroll to bottom
   - Click **"Delete Database"** or **"Destroy"**
   - Type the database name to confirm
   - Click **"Delete"**

   **⚠️ WARNING:** This permanently deletes all data. Make sure you don't need it!

---

## Step 5: Initialize Your New Database

After updating `DATABASE_URL`, your backend will redeploy automatically. Now you need to run migrations:

### Option A: Run Migrations via Render Shell (Recommended)

1. **Open Render Shell:**
   - Go to your backend service on Render
   - Click **"Shell"** tab (or "Logs" → "Open Shell")
   - Wait for shell to connect

2. **Run Migrations:**
   ```bash
   cd backend
   alembic upgrade head
   ```

3. **Verify:**
   ```bash
   alembic current
   ```
   Should show your latest migration revision

### Option B: Run Migrations via SSH (If Shell Not Available)

1. **SSH into Render service:**
   - Render doesn't support direct SSH, so use Render Shell instead
   - Or run migrations manually via a one-off script

### Option C: Create Migration Script

I can create a script that runs migrations automatically on startup (first run only).

---

## Step 6: Verify Connection

1. **Check Backend Logs:**
   - Go to your backend service → **"Logs"** tab
   - Look for:
     ```
     ✅ Async engine created successfully
     ✅ Database connection test passed
     ```

2. **Test Health Endpoint:**
   - Visit: `https://agent-liquidcanvas.onrender.com/health/ready`
   - Should return: `{"status":"ready","database":"connected"}`

3. **Test API Endpoints:**
   - Try any endpoint that queries the database
   - Should work without errors

---

## Troubleshooting

### Problem: Can't Find Old Database

**Solution:**
- Old database might already be deleted
- Or it's in a different Render account/organization
- Check all organizations/teams in Render

### Problem: Connection String Not Working

**Solution:**
- Make sure you're using **"Internal Database URL"** (not external)
- Verify it starts with `postgresql+asyncpg://`
- Check that password is correct (no extra spaces)
- Ensure backend and database are in same region

### Problem: Migrations Fail

**Solution:**
- Make sure `DATABASE_URL` is correct
- Check that database user has permissions
- Verify Alembic can find migration files
- Check logs for specific error messages

### Problem: "Database does not exist" Error

**Solution:**
- The database might still be creating (wait a few minutes)
- Check database name matches in connection string
- Verify you're connecting to the right database

---

## Quick Checklist

- [ ] Created new Render PostgreSQL database
- [ ] Copied Internal Database URL
- [ ] Converted to `postgresql+asyncpg://` format
- [ ] Updated `DATABASE_URL` in backend service environment variables
- [ ] Deleted old database (optional)
- [ ] Ran migrations: `alembic upgrade head`
- [ ] Verified connection in logs
- [ ] Tested health endpoint
- [ ] Tested API endpoints

---

## Next Steps After Setup

1. **Run Initial Migrations:**
   ```bash
   # In Render Shell
   cd backend
   alembic upgrade head
   ```

2. **Verify Tables Created:**
   ```bash
   # Check if tables exist
   psql $DATABASE_URL -c "\dt"
   ```

3. **Seed Initial Data (if needed):**
   - Import any initial data you need
   - Set up admin users, etc.

---

**Ready to start? Let me know when you've created the database and I'll help you get the connection string set up!**

