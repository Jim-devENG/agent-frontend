# Run Migrations via PowerShell (Windows)

## Quick Command

**Copy and paste this into PowerShell:**

```powershell
Invoke-WebRequest -Uri "https://agent-liquidcanvas.onrender.com/api/health/migrate" -Method POST -Headers @{"X-Migration-Token"="migrate-2026-secret-token-xyz110556"}
```

## Alternative: Using curl.exe (if available)

If you have `curl.exe` installed:

```powershell
curl.exe -X POST https://agent-liquidcanvas.onrender.com/api/health/migrate -H "X-Migration-Token: migrate-2026-secret-token-xyz110556"
```

## Check Response

To see the response:

```powershell
$response = Invoke-WebRequest -Uri "https://agent-liquidcanvas.onrender.com/api/health/migrate" -Method POST -Headers @{"X-Migration-Token"="migrate-2026-secret-token-xyz110556"}
$response.Content
```

## What You Should See

If successful, you'll see JSON like:
```json
{
  "status": "success",
  "message": "Migrations completed successfully",
  "schema_diagnostics": {
    "social_tables": {
      "valid": true,
      "missing": []
    }
  }
}
```

## Troubleshooting

**Error: "Invalid migration token"**
- Make sure the token matches exactly: `migrate-2026-secret-token-xyz110556`
- Check that `MIGRATION_TOKEN` is set in Render environment variables

**Error: "Migration endpoint not configured"**
- Make sure `MIGRATION_TOKEN` is set in Render
- Wait for service to redeploy after adding the variable

