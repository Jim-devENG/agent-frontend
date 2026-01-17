# Supabase Connection Setup

## Your Supabase Connection String

```
postgresql://postgres:L1qu!dcvnvs@db.wlsbtxwbyqdagvrbkebl.supabase.co:5432/postgres
```

## Step 1: Update Render Environment Variable

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Navigate to your Backend Service**
3. **Click on the service**
4. **Go to "Environment" tab**
5. **Find `DATABASE_URL`** (or add it if it doesn't exist)
6. **Set the value to**:
   ```
   postgresql://postgres:L1qu!dcvnvs@db.wlsbtxwbyqdagvrbkebl.supabase.co:5432/postgres
   ```
7. **Click "Save Changes"**
8. **Render will automatically redeploy**

## Step 2: Verify Connection

After deployment, check the logs:

1. **Go to your Backend Service → Logs**
2. **Look for**:
   ```
   ✅ Database connectivity verified
   Attempting to connect to database at: db.wlsbtxwbyqdagvrbkebl.supabase.co:5432
   ```

## Step 3: Check Migrations

Migrations should run automatically if `AUTO_MIGRATE=true` is set. Look for:
```
🔄 Smart auto-migrate: Running migrations automatically...
✅ Database migrations completed successfully
```

## Step 4: Verify Tables in Supabase

1. **Go to Supabase Dashboard**: https://supabase.com/dashboard
2. **Select your project**
3. **Go to "Table Editor"**
4. **You should see tables**:
   - `prospects`
   - `jobs`
   - `email_logs`
   - `settings`
   - `discovery_queries`
   - `scraper_history`
   - `alembic_version`

## Step 5: Test API

```bash
curl https://your-backend-url/api/health
```

Should return:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

## Local Development Setup

If you want to test locally, create/update `backend/.env`:

```env
DATABASE_URL=postgresql://postgres:L1qu!dcvnvs@db.wlsbtxwbyqdagvrbkebl.supabase.co:5432/postgres
```

Then run:
```bash
cd backend
alembic upgrade head  # Run migrations
uvicorn app.main:app --reload  # Start server
```

## Connection String Details

- **Host**: `db.wlsbtxwbyqdagvrbkebl.supabase.co`
- **Port**: `5432`
- **Database**: `postgres`
- **User**: `postgres`
- **Password**: `L1qu!dcvnvs`

The backend code will automatically convert this to:
```
postgresql+asyncpg://postgres:L1qu!dcvnvs@db.wlsbtxwbyqdagvrbkebl.supabase.co:5432/postgres
```

## Troubleshooting

### Connection Refused
- Check Supabase project is running (green status)
- Verify password is correct (no extra spaces)
- Check firewall/network settings

### Migration Errors
- Check logs for specific error
- May need to run manually: `alembic upgrade head`
- Check Alembic version: `alembic current`

### SSL Errors
If you get SSL errors, add `?sslmode=require`:
```
postgresql://postgres:L1qu!dcvnvs@db.wlsbtxwbyqdagvrbkebl.supabase.co:5432/postgres?sslmode=require
```

## Next Steps

1. ✅ Update `DATABASE_URL` in Render
2. ✅ Wait for deployment
3. ✅ Check logs for connection success
4. ✅ Verify tables in Supabase
5. ✅ Test API endpoints

Your backend is now connected to Supabase! 🎉

