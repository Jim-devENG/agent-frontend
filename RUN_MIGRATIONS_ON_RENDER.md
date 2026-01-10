# How to Run Migrations on Render - Fixed Multiple Heads Issue

## ✅ Problem Fixed

The migration history had **4 separate head revisions** (branched), which prevented Alembic from running. I've created a merge migration that combines all branches into a single head.

## ✅ Solution Applied

Created merge migration: `de8b5344821d_merge_all_migration_heads.py`

This migration merges all 4 branches:
- `add_scraper_history`
- `ensure_alembic_version_table`
- `fix_scrape_status_discovered`
- `merge_social_branches`

Into a single head: `de8b5344821d`

---

## Step-by-Step: Run Migrations on Render

### Step 1: Wait for Deployment

The merge migration has been pushed to your repo. Wait for Render to automatically redeploy (2-5 minutes), or manually trigger a deploy.

### Step 2: Open Render Shell

1. **Go to**: https://dashboard.render.com
2. **Click** your backend service
3. **Click** **"Shell"** tab (or "Logs" → "Open Shell")
4. **Wait** for shell to connect (10-20 seconds)

### Step 3: Run Migrations

Once shell is connected, run:

```bash
cd backend
alembic upgrade head
```

**You should now see:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade <revision> -> de8b5344821d, merge_all_migration_heads
INFO  [alembic.runtime.migration] Running upgrade ... -> ..., <other_migrations>
...
```

**No more "Multiple head revisions" error!** ✅

### Step 4: Verify Migrations Completed

After migrations finish, run:

```bash
alembic current
```

Should show: `de8b5344821d (head)`

---

## Alternative: Run Migrations Automatically

If you want migrations to run automatically on startup, set this environment variable on Render:

**Key:** `AUTO_MIGRATE`
**Value:** `true`

Then migrations will run automatically every time the service starts (if schema mismatch is detected).

**However**, now that we've fixed the multiple heads issue, the smart auto-migrate should work on the next deployment.

---

## What This Fix Does

The merge migration:
- ✅ Combines all 4 separate migration branches into one
- ✅ No-op migration (doesn't change schema, just merges branches)
- ✅ Creates single head for future migrations
- ✅ Safe to run - won't affect existing data

---

## After Migrations Complete

Once migrations finish successfully:

1. ✅ **Test health endpoint:**
   ```
   https://agent-liquidcanvas.onrender.com/health/ready
   ```
   Should return: `{"status":"ready","database":"connected"}`

2. ✅ **Test database query:**
   ```
   https://agent-liquidcanvas.onrender.com/api/prospects?limit=10
   ```
   Should return data or empty array (not errors)

3. ✅ **Verify tables exist:**
   - Check that `prospects` table has all required columns
   - Check that other tables (jobs, discovery_queries, etc.) exist

---

## Troubleshooting

### If you still see "Multiple head revisions":

**Solution:**
- Make sure the merge migration file is in your repo
- Check that you pulled the latest code
- Run `alembic heads` locally - should show only `de8b5344821d`

### If migrations still fail:

**Check:**
- Database connection is working (test `/health/ready`)
- Database user has permissions to create tables
- Check logs for specific error messages

---

**Next step: Wait for deployment, then run `alembic upgrade head` in Render Shell!** 🚀

