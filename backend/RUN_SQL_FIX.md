# How to Run SQL Fix on Render

## Step-by-Step Instructions

### Step 1: Access Render Dashboard
1. Go to https://dashboard.render.com
2. Log in to your account
3. Find your **PostgreSQL database** service (not the backend service)

### Step 2: Open Database Shell
1. Click on your **PostgreSQL database** service
2. Look for **"Shell"** tab (usually at the top)
3. Click **"Shell"** tab
4. You'll see a terminal prompt

### Step 3: Connect to Database
The shell should automatically connect. If not, you'll see connection info in the database service page.

### Step 4: Run the SQL
Copy and paste this ENTIRE block into the shell and press Enter:

```sql
-- Add column (idempotent - safe to run multiple times)
ALTER TABLE prospects 
ADD COLUMN IF NOT EXISTS discovery_query_id UUID;

-- Create index
CREATE INDEX IF NOT EXISTS ix_prospects_discovery_query_id 
ON prospects(discovery_query_id);

-- Add foreign key (if discovery_queries table exists)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'discovery_queries') THEN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.table_constraints 
            WHERE constraint_name = 'fk_prospects_discovery_query_id'
        ) THEN
            ALTER TABLE prospects
            ADD CONSTRAINT fk_prospects_discovery_query_id
            FOREIGN KEY (discovery_query_id)
            REFERENCES discovery_queries(id)
            ON DELETE SET NULL;
        END IF;
    END IF;
END $$;
```

### Step 5: Verify It Worked
Run this to check:

```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_name = 'prospects' 
AND column_name = 'discovery_query_id';
```

**Expected output:**
```
 column_name        | data_type | is_nullable 
--------------------+-----------+-------------
 discovery_query_id | uuid      | YES
```

### Step 6: Test the Application
1. Go back to your backend service logs
2. The errors should stop
3. Try accessing the prospects endpoint
4. Queries should work now

---

## Alternative: Using psql Command Line

If you have `psql` installed locally and have the `DATABASE_URL`:

```bash
psql $DATABASE_URL -f fix_discovery_query_id.sql
```

Or copy the SQL content and pipe it:

```bash
cat fix_discovery_query_id.sql | psql $DATABASE_URL
```

---

## Troubleshooting

**"relation does not exist"**
- The `prospects` table doesn't exist yet
- Run migrations first: `alembic upgrade head` in backend shell

**"permission denied"**
- Make sure you're using the database owner account
- Check Render database credentials

**"column already exists"**
- That's fine! The `IF NOT EXISTS` prevents errors
- The fix is idempotent

---

## Quick Copy-Paste Version

Just copy this entire block:

```sql
ALTER TABLE prospects ADD COLUMN IF NOT EXISTS discovery_query_id UUID;
CREATE INDEX IF NOT EXISTS ix_prospects_discovery_query_id ON prospects(discovery_query_id);
DO $$ BEGIN IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'discovery_queries') THEN IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name = 'fk_prospects_discovery_query_id') THEN ALTER TABLE prospects ADD CONSTRAINT fk_prospects_discovery_query_id FOREIGN KEY (discovery_query_id) REFERENCES discovery_queries(id) ON DELETE SET NULL; END IF; END IF; END $$;
```

