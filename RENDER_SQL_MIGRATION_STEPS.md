# Run SQL Migration on Render PostgreSQL - Step by Step

## ✅ Correct Method: Use Backend Service Shell

PostgreSQL services on Render don't have a Shell tab. You need to use your **Backend Service Shell** instead.

### Step 1: Go to Your Backend Service

1. In Render Dashboard, go back to the main dashboard
2. Find your **Backend Service** (not the PostgreSQL database)
   - It might be named something like `agent-backend` or `agent-liquidcanvas-backend`
3. Click on it

### Step 2: Open Shell Tab

1. In your Backend Service page, look for the **"Shell"** tab at the top
2. Click **"Shell"** tab
3. You'll see a terminal prompt

### Step 3: Run the SQL Migration

Copy and paste this command:

```bash
psql $DATABASE_URL -c "ALTER TABLE prospects RENAME COLUMN hunter_payload TO snov_payload;"
```

Press **Enter**.

**Expected output:**
```
ALTER TABLE
```

✅ This means it worked!

### Step 4: Verify It Worked

Run this verification command:

```bash
psql $DATABASE_URL -c "SELECT column_name FROM information_schema.columns WHERE table_name = 'prospects' AND column_name = 'snov_payload';"
```

**Expected output:**
```
 column_name  
--------------
 snov_payload
```

You should see `snov_payload` in the results.

### Step 5: Check for Existing Data (Optional)

To see if there's any data in the column:

```bash
psql $DATABASE_URL -c "SELECT COUNT(*) as total, COUNT(snov_payload) as with_data FROM prospects;"
```

---

## Alternative: If Backend Shell Doesn't Work

If you can't access the backend shell, you can connect from your local machine:

### Step 1: Get Connection String

1. Go back to `agent-postgres` service
2. Find **"External Database URL"** 
3. Click to reveal it (it's hidden with dots)
4. Copy the connection string

### Step 2: Connect from Local Machine

If you have `psql` installed locally:

```bash
psql "YOUR_EXTERNAL_DATABASE_URL_HERE" -c "ALTER TABLE prospects RENAME COLUMN hunter_payload TO snov_payload;"
```

Or connect interactively:

```bash
psql "YOUR_EXTERNAL_DATABASE_URL_HERE"
```

Then run:
```sql
ALTER TABLE prospects RENAME COLUMN hunter_payload TO snov_payload;
```

---

## Quick Reference Commands

**Run migration:**
```bash
psql $DATABASE_URL -c "ALTER TABLE prospects RENAME COLUMN hunter_payload TO snov_payload;"
```

**Verify:**
```bash
psql $DATABASE_URL -c "SELECT column_name FROM information_schema.columns WHERE table_name = 'prospects' AND column_name = 'snov_payload';"
```

**Check all payload columns:**
```bash
psql $DATABASE_URL -c "SELECT column_name FROM information_schema.columns WHERE table_name = 'prospects' AND column_name LIKE '%payload%';"
```

---

## Troubleshooting

### "psql: command not found"

If you see this in the backend shell, try:
```bash
which psql
```

If it's not found, you might need to install it or use a different method.

### "relation does not exist"

The `prospects` table doesn't exist yet. This is normal for first-time setup. The backend will create it automatically when it starts.

### "column does not exist"

The column might already be renamed. Check with:
```bash
psql $DATABASE_URL -c "SELECT column_name FROM information_schema.columns WHERE table_name = 'prospects';"
```

