# Run SQL Migration on Render PostgreSQL

## Quick Guide: Rename `hunter_payload` to `snov_payload`

### Step 1: Access Render Dashboard

1. Go to **https://dashboard.render.com**
2. Log in to your account
3. Find your **PostgreSQL database** service named **`agent-postgres`**

### Step 2: Open Database Shell

1. Click on **`agent-postgres`** (your PostgreSQL service)
2. Look for the **"Shell"** tab at the top of the page
3. Click **"Shell"** tab
4. You'll see a terminal prompt (usually `$` or `#`)

### Step 3: Connect to Database (if needed)

The shell should automatically connect. If you see a prompt, you're ready!

If you need to connect manually, you'll see connection info on the database service page.

### Step 4: Run the SQL Migration

Copy and paste this **ENTIRE** SQL command into the shell and press **Enter**:

```sql
ALTER TABLE prospects RENAME COLUMN hunter_payload TO snov_payload;
```

**Expected output:**
```
ALTER TABLE
```

This means it worked! ✅

### Step 5: Verify It Worked

Run this verification query:

```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'prospects' 
AND column_name IN ('hunter_payload', 'snov_payload');
```

**Expected output:**
```
 column_name  | data_type 
--------------+-----------
 snov_payload | json
```

You should see **`snov_payload`** and **NOT** see `hunter_payload`.

### Step 6: Check for Existing Data (Optional)

If you want to see if there's any data in the column:

```sql
SELECT COUNT(*) as total_prospects,
       COUNT(snov_payload) as prospects_with_snov_data
FROM prospects;
```

This shows:
- Total prospects
- How many have data in the `snov_payload` column

---

## Alternative Method: Using Backend Shell

If the PostgreSQL Shell doesn't work, you can use your **Backend Service Shell**:

### Step 1: Open Backend Shell

1. Go to Render Dashboard
2. Click on your **Backend Service** (not the database)
3. Click **"Shell"** tab

### Step 2: Run SQL via psql

```bash
psql $DATABASE_URL -c "ALTER TABLE prospects RENAME COLUMN hunter_payload TO snov_payload;"
```

### Step 3: Verify

```bash
psql $DATABASE_URL -c "SELECT column_name FROM information_schema.columns WHERE table_name = 'prospects' AND column_name = 'snov_payload';"
```

---

## Troubleshooting

### Error: "column does not exist"

If you see:
```
ERROR: column "hunter_payload" does not exist
```

This means:
- The column was already renamed, OR
- The column doesn't exist yet (first time setup)

**Check what columns exist:**
```sql
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'prospects' 
AND column_name LIKE '%payload%';
```

### Error: "permission denied"

If you see permission errors:
- Make sure you're using the **PostgreSQL Shell** (not backend shell)
- Or use the backend shell with `psql $DATABASE_URL`

### Error: "relation does not exist"

If you see:
```
ERROR: relation "prospects" does not exist
```

The table hasn't been created yet. This is normal for first-time setup. The backend will create it automatically on first run.

---

## After Migration

Once the migration is complete:

1. ✅ Column renamed: `hunter_payload` → `snov_payload`
2. ✅ Backend code updated (already pushed to repo)
3. ✅ Environment variables updated (add `SNOV_USER_ID` and `SNOV_SECRET`)
4. ✅ Deploy will pick up the changes automatically

Your application should now work with Snov.io! 🎉

