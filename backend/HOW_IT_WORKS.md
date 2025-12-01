# 🔧 How The Database Reset System Works

## 📋 Overview

The files I created form a complete database reset and migration system. Here's how each piece works:

---

## 1. Migration Files (Alembic)

### `000000000000_create_base_tables.py`
**What it does:**
- Creates the 3 core tables: `jobs`, `prospects`, `email_logs`
- Sets as BASE migration (`down_revision = None`)
- Runs FIRST when you do `alembic upgrade head`

**When it runs:**
```bash
alembic upgrade head
# Step 1: Runs 000000000000 → Creates jobs, prospects, email_logs
# Step 2: Runs 4b9608290b5d → Creates settings
# Step 3: Runs add_discovery_query → Creates discovery_queries
# Step 4: Runs 556b79de2825 → Adds discovery_query_id to prospects
```

**Execution flow:**
```
Empty DB
  ↓
000000000000 (creates jobs, prospects, email_logs)
  ↓
4b9608290b5d (creates settings)
  ↓
add_discovery_query (creates discovery_queries)
  ↓
556b79de2825 (adds discovery_query_id column)
  ↓
Complete schema ✅
```

---

## 2. Reset Scripts

### `reset_database.sh` (Linux/Mac) or `reset_database.ps1` (Windows)

**What it does:**
1. **Warns you** - 5 second countdown before deleting data
2. **Shows current state** - Lists all tables before deletion
3. **Drops everything** - `DROP SCHEMA public CASCADE`
4. **Recreates schema** - `CREATE SCHEMA public`
5. **Runs migrations** - `alembic upgrade head` (runs all 4 migrations in order)
6. **Verifies** - Shows tables and migration version

**Execution:**
```bash
cd backend
./reset_database.sh
```

**What happens step-by-step:**
```
1. Script starts
   ↓
2. Checks DATABASE_URL exists
   ↓
3. Shows current tables (if any)
   ↓
4. Waits 5 seconds (safety)
   ↓
5. Drops ALL tables: DROP SCHEMA public CASCADE
   ↓
6. Creates empty schema: CREATE SCHEMA public
   ↓
7. Runs: alembic upgrade head
   ├─→ 000000000000: Creates jobs, prospects, email_logs
   ├─→ 4b9608290b5d: Creates settings
   ├─→ add_discovery_query: Creates discovery_queries
   └─→ 556b79de2825: Adds discovery_query_id
   ↓
8. Shows new tables (should be 5)
   ↓
9. Shows alembic_version (should be 556b79de2825)
   ↓
10. Done! ✅
```

---

## 3. How Migrations Work Together

### Migration Chain:
```
<base> (empty database)
  ↓
000000000000 (BASE - creates core tables)
  ↓
4b9608290b5d (creates settings)
  ↓
add_discovery_query (creates discovery_queries)
  ↓
556b79de2825 (HEAD - adds discovery_query_id)
```

**Each migration:**
- Has a `revision` ID (unique identifier)
- Has a `down_revision` (points to previous migration)
- Has `upgrade()` function (runs when going forward)
- Has `downgrade()` function (runs when rolling back)

**Alembic tracks state:**
- Stores current revision in `alembic_version` table
- Knows which migrations have run
- Only runs migrations that haven't been applied

---

## 4. What Happens on Render (Production)

### Current Setup:
Your `backend/app/main.py` has this on startup:

```python
@app.on_event("startup")
async def startup():
    # Tries migrations first
    command.upgrade(alembic_cfg, "head")
    
    # If migrations fail, falls back to:
    await conn.run_sync(Base.metadata.create_all)
```

**After reset, this will:**
1. ✅ Run `alembic upgrade head` successfully
2. ✅ Create all tables via migrations (proper versioning)
3. ❌ Never need the fallback `create_all()` (but it's still there as safety)

**On Render deployment:**
```
1. Code pushed to GitHub
   ↓
2. Render detects change
   ↓
3. Builds Docker image
   ↓
4. Starts container
   ↓
5. Runs: uvicorn app.main:app
   ↓
6. Startup event fires
   ↓
7. Runs: alembic upgrade head
   ├─→ Checks alembic_version table
   ├─→ Sees which migrations are missing
   └─→ Runs only missing migrations
   ↓
8. App starts ✅
```

---

## 5. Testing Without Resetting

### Check Migration Chain:
```bash
cd backend
alembic history
```

**Expected output:**
```
add_discovery_query -> 556b79de2825 (head)
4b9608290b5d -> add_discovery_query
000000000000 -> 4b9608290b5d
<base> -> 000000000000
```

### Check Current State:
```bash
cd backend
alembic current
```

**Shows:** Current migration version in database

### Dry Run (See what would happen):
```bash
cd backend
alembic upgrade head --sql
```

**Shows:** SQL that would be executed (without running it)

---

## 6. Manual Execution (If Scripts Don't Work)

### Step-by-step:

**1. Drop all tables:**
```bash
psql $DATABASE_URL -c "DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public;"
```

**2. Run migrations:**
```bash
cd backend
alembic upgrade head
```

**3. Verify:**
```bash
psql $DATABASE_URL -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE' ORDER BY table_name;"
```

**Expected:**
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

## 7. What Each File Does

| File | Purpose | When It Runs |
|------|---------|--------------|
| `000000000000_create_base_tables.py` | Creates core tables | First migration |
| `4b9608290b5d_add_settings_table.py` | Creates settings | After base |
| `add_discovery_query_table.py` | Creates discovery_queries | After settings |
| `556b79de2825_add_discovery_query_id_to_prospects_safe.py` | Adds FK column | Last migration |
| `reset_database.sh` | Automated reset | When you run it |
| `reset_database.ps1` | Windows reset | When you run it |
| `RESET_INSTRUCTIONS.md` | Guide | Reference |

---

## 8. Safety Features

### Idempotent Migrations:
- `556b79de2825` checks if column exists before adding
- Safe to run multiple times
- Won't break if already applied

### Reset Script Safety:
- 5 second warning before deletion
- Shows current state first
- Verifies results after

### Fallback in Code:
- `Base.metadata.create_all()` still exists as backup
- Won't break if migrations fail
- But migrations should work now

---

## 9. Common Scenarios

### Scenario 1: Fresh Database
```
Database: Empty
Action: alembic upgrade head
Result: All 4 migrations run, 5 tables created ✅
```

### Scenario 2: Database Already Has Tables
```
Database: Has old tables (created via create_all)
Action: alembic upgrade head
Result: 
  - Sees alembic_version table missing
  - Tries to run migrations
  - May fail if tables conflict
  - Solution: Run reset script first
```

### Scenario 3: Partial Migrations Applied
```
Database: Has some migrations applied
Action: alembic upgrade head
Result: Only missing migrations run ✅
```

### Scenario 4: Production Reset
```
Database: Production with data
Action: 
  1. Backup: pg_dump $DATABASE_URL > backup.sql
  2. Reset: ./reset_database.sh
  3. Verify: Check tables exist
Result: Clean schema, all data lost (restore from backup if needed)
```

---

## 10. Verification Commands

After reset, run these to verify:

```bash
# Check tables exist
psql $DATABASE_URL -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE' ORDER BY table_name;"

# Check migration version
psql $DATABASE_URL -c "SELECT * FROM alembic_version;"

# Check foreign keys
psql $DATABASE_URL -c "SELECT tc.table_name, kcu.column_name, ccu.table_name AS foreign_table_name FROM information_schema.table_constraints AS tc JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name WHERE tc.constraint_type = 'FOREIGN KEY' ORDER BY tc.table_name;"

# Check discovery_query_id column
psql $DATABASE_URL -c "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'prospects' AND column_name = 'discovery_query_id';"
```

---

## ✅ Summary

**The system works by:**
1. Migration files define schema changes in order
2. Alembic tracks which migrations have run
3. Reset script drops everything and runs all migrations fresh
4. On startup, app runs migrations automatically
5. Everything is versioned and repeatable

**To use it:**
1. Run `./reset_database.sh` (or `.ps1` on Windows)
2. Wait for completion
3. Verify tables exist
4. Done! ✅

**The files are ready to use right now!**

