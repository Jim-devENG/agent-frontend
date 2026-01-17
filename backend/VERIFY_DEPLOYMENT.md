# Verify Deployment Execution

## ✅ What Should Happen Automatically

1. **Render Auto-Deploy**: When you push to `main`, Render detects the change and starts a new deployment
2. **Migrations Run**: On startup, `backend/app/main.py` runs `alembic upgrade head` automatically
3. **Code Changes Active**: New transaction helpers (`safe_commit`, `safe_flush`) are used immediately

## 🔍 How to Verify They're Actually Executing

### Step 1: Check Render Deployment Status

1. Go to **Render Dashboard** → Your Backend Service
2. Check **Events** tab - should show recent deployment from your push
3. Check **Logs** tab - look for:
   ```
   Running database migrations on startup...
   ✅ Database migrations completed successfully
   ```
   OR if migration already applied:
   ```
   ℹ️  Column discovery_query_id already exists, skipping
   ```

### Step 2: Verify Database Column Exists

**Option A: Via Render Shell**
1. Render Dashboard → Backend Service → **Shell** tab
2. Run:
   ```bash
   psql $DATABASE_URL -c "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'prospects' AND column_name = 'discovery_query_id';"
   ```

**Option B: Via API Endpoint** (if you have one)
```bash
curl https://agent-liquidcanvas.onrender.com/health
```

### Step 3: Verify Code Changes Are Active

Check logs for transaction errors. If you see:
- ❌ `PendingRollbackError` → Old code (not deployed yet)
- ✅ No transaction errors → New code is active

### Step 4: Test Transaction Safety

Run a discovery job and check logs. You should see:
- `safe_commit()` being called
- Proper rollback on errors (if any occur)
- No `PendingRollbackError` or `InFailedSQLTransaction` errors

## 🚨 If Changes Are NOT Executing

### Check 1: Is Render Actually Deploying?

1. Render Dashboard → **Events** tab
2. Look for deployment event with your commit hash (`51c67c6`)
3. If no deployment → Render might not be connected to GitHub or auto-deploy is disabled

### Check 2: Did Migrations Run?

1. Render Dashboard → **Logs** tab
2. Search for: `"Running database migrations"`
3. If not found → Startup event might not be firing

### Check 3: Force Manual Deployment

1. Render Dashboard → **Manual Deploy** button
2. Select `main` branch
3. Deploy

### Check 4: Run Migration Manually

1. Render Dashboard → **Shell** tab
2. Run:
   ```bash
   cd backend
   alembic upgrade head
   ```
3. Check output for: `✅ Added discovery_query_id column` or `ℹ️  Column already exists`

## 📊 Expected Log Output

**On Successful Deployment:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Running database migrations on startup...
INFO:     ✅ Database migrations completed successfully
INFO:     Application startup complete.
```

**If Migration Already Applied:**
```
INFO:     Running database migrations on startup...
ℹ️  Column discovery_query_id already exists, skipping
ℹ️  Index ix_prospects_discovery_query_id already exists, skipping
INFO:     ✅ Database migrations completed successfully
```

## ✅ Quick Verification Command

Run this in Render Shell to verify everything:
```bash
# Check column exists
psql $DATABASE_URL -c "SELECT column_name FROM information_schema.columns WHERE table_name = 'prospects' AND column_name = 'discovery_query_id';"

# Check migration version
cd backend && alembic current

# Check if safe_commit is in code
grep -r "safe_commit" app/
```

Expected output:
- Column query returns: `discovery_query_id`
- Migration shows: Latest revision
- Code search shows: `safe_commit` in `app/tasks/discovery.py`

