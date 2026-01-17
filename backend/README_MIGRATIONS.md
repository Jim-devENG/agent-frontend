# Running Alembic Migrations

## Automatic Migrations (Recommended for Production)

Set the `AUTO_MIGRATE` environment variable to enable automatic migrations on startup:

```bash
# In Render dashboard or .env file
AUTO_MIGRATE=true
```

**Benefits:**
- Migrations run automatically on every deploy
- No manual intervention needed
- App stays up-to-date with latest schema

**Note:** Migrations are run with error handling - if they fail, the app will still start (with warnings).

## Manual Migrations

### Option 1: PowerShell Script (Windows)

```powershell
cd backend
.\run_migrations.ps1
```

### Option 2: Command Line

```bash
cd backend
alembic upgrade head
```

### Option 3: HTTP Endpoint

```bash
curl -X POST https://your-app.onrender.com/api/health/migrate \
     -H "X-Migration-Token: your-secret-token"
```

## Fix Alembic Version Table (If Corrupted)

If migrations are re-running from base, fix the `alembic_version` table:

```bash
cd backend
python fix_alembic_version.py
alembic upgrade head
```

## Environment Variables

- `AUTO_MIGRATE`: Set to `true`, `1`, or `yes` to enable automatic migrations on startup
- `DATABASE_URL`: PostgreSQL connection string (required for migrations)

## Troubleshooting

**Error: "column does not exist"**
- Run migrations: `alembic upgrade head`
- Or enable `AUTO_MIGRATE=true`

**Error: "alembic_version table missing"**
- Run: `python fix_alembic_version.py`
- Then: `alembic upgrade head`

**Migrations running repeatedly**
- Check `alembic_version` table has correct revision
- Run `fix_alembic_version.py` to fix

