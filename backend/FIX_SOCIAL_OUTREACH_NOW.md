# Fix "Social Outreach Not Available" - Run Migrations

## Problem
The social outreach feature shows "Social Outreach Not Available" because the social database tables don't exist yet.

## Solution: Run Database Migrations

You have two options:

### Option 1: HTTP Migration Endpoint (Recommended)

**Step 1: Set Migration Token in Render**
1. Go to Render Dashboard → Your Service → Environment
2. Add environment variable:
   - **Key**: `MIGRATION_TOKEN`
   - **Value**: Any strong random string (e.g., `my-secret-token-2024`)
3. Click **Save Changes** (service will redeploy)

**Step 2: Run Migration via PowerShell**
```powershell
$token = "your-secret-token-2024"  # Replace with your token
Invoke-WebRequest -Uri "https://agent-liquidcanvas.onrender.com/api/health/migrate" `
  -Method POST `
  -Headers @{"X-Migration-Token"=$token} `
  -ContentType "application/json"
```

**Step 3: Verify**
After running, refresh the social outreach page. It should now show the pipeline instead of "Not Available".

### Option 2: Render Shell (If Available)

1. Go to Render Dashboard → Your Service → Shell
2. Run:
   ```bash
   cd /app
   alembic upgrade head
   ```
   OR
   ```bash
   cd /app/backend
   alembic upgrade head
   ```

## Verify Tables Were Created

After migrations, check the health endpoint:
```
https://agent-liquidcanvas.onrender.com/api/health/schema
```

Look for:
```json
{
  "social_tables": {
    "valid": true,
    "missing": []
  }
}
```

## Required Tables
The migrations will create:
- `social_profiles`
- `social_discovery_jobs`
- `social_drafts`
- `social_messages`

Once these exist, the social outreach feature will be active!

