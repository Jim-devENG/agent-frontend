# 🗑️ Database Reset Instructions

## ⚠️ WARNING
**This will DELETE ALL DATA from your database. Make a backup first if you have production data!**

---

## 📋 Prerequisites

1. **Backup Database** (if production):
   ```bash
   pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **Verify Environment:**
   ```bash
   echo $DATABASE_URL  # Should show your PostgreSQL connection string
   ```

3. **Install Dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

---

## 🔄 Reset Methods

### Method 1: Automated Script (Recommended)

**Linux/Mac:**
```bash
cd backend
chmod +x reset_database.sh
./reset_database.sh
```

**Windows (PowerShell):**
```powershell
cd backend
.\reset_database.ps1
```

### Method 2: Manual Reset

**Step 1: Drop All Tables**
```bash
psql $DATABASE_URL -c "DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public;"
```

**Step 2: Run Migrations**
```bash
cd backend
alembic upgrade head
```

**Step 3: Verify**
```bash
psql $DATABASE_URL -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE' ORDER BY table_name;"
```

Expected output:
```
      table_name
------------------------
 discovery_queries
 email_logs
 jobs
 prospects
 settings
(5 rows)
```

---

## 🔍 Verification Queries

### Check All Tables Exist
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_type = 'BASE TABLE'
ORDER BY table_name;
```

### Check All Foreign Keys
```sql
SELECT
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
ORDER BY tc.table_name;
```

Expected foreign keys:
- `discovery_queries.job_id` → `jobs.id`
- `prospects.discovery_query_id` → `discovery_queries.id`
- `email_logs.prospect_id` → `prospects.id`

### Check Migration Version
```sql
SELECT * FROM alembic_version;
```

Expected: `556b79de2825` (or latest revision)

### Check Column Existence
```sql
-- Verify discovery_query_id exists in prospects
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'prospects' 
  AND column_name = 'discovery_query_id';
```

---

## 🚨 Troubleshooting

### Error: "relation does not exist"
**Cause:** Tables were dropped but migrations didn't run.

**Fix:**
```bash
cd backend
alembic upgrade head
```

### Error: "alembic_version table does not exist"
**Cause:** Schema was dropped but migrations haven't run yet.

**Fix:** This is normal. Run `alembic upgrade head` to create it.

### Error: "duplicate key value violates unique constraint"
**Cause:** Migration tried to create something that already exists.

**Fix:** The migrations are idempotent, but if this happens:
```bash
cd backend
alembic downgrade base
alembic upgrade head
```

### Error: "connection refused" or "authentication failed"
**Cause:** `DATABASE_URL` is incorrect or database is not accessible.

**Fix:**
1. Verify `DATABASE_URL` is set correctly
2. Test connection: `psql $DATABASE_URL -c "SELECT 1;"`
3. Check firewall/network settings

---

## ✅ Success Criteria

After reset, you should have:

1. ✅ **5 tables created:**
   - `jobs`
   - `prospects`
   - `email_logs`
   - `settings`
   - `discovery_queries`

2. ✅ **3 foreign keys:**
   - `discovery_queries.job_id` → `jobs.id`
   - `prospects.discovery_query_id` → `discovery_queries.id`
   - `email_logs.prospect_id` → `prospects.id`

3. ✅ **All indexes created:**
   - Check with: `\d+ table_name` in psql

4. ✅ **Alembic version set:**
   - `SELECT * FROM alembic_version;` shows latest revision

5. ✅ **No errors in application logs:**
   - Backend should start without schema errors
   - Discovery jobs should run without transaction errors

---

## 📝 Post-Reset Checklist

- [ ] All tables exist (5 total)
- [ ] All foreign keys are created
- [ ] Alembic version is correct
- [ ] Backend starts without errors
- [ ] Discovery job can be created
- [ ] Prospects can be saved
- [ ] No `PendingRollbackError` in logs
- [ ] No `InFailedSQLTransaction` errors

---

## 🔄 Migration Chain

After reset, the migration chain should be:

```
000000000000 (base) 
  → 4b9608290b5d (settings)
    → add_discovery_query (discovery_queries table)
      → 556b79de2825 (discovery_query_id column) [HEAD]
```

Verify with:
```bash
alembic history
```

---

**Reset Complete!** 🎉

