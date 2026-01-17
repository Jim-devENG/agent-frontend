# Render Database Reset Guide

This guide will help you delete the existing Render database and create a new one.

## ⚠️ WARNING: Data Loss

**Deleting a database will permanently delete ALL data:**
- All prospects
- All jobs
- All email logs
- All settings
- All discovery queries
- Everything!

**Make sure you:**
1. ✅ Have exported any data you need (see backup steps below)
2. ✅ Are ready to start fresh
3. ✅ Have Supabase set up (if migrating)

## Option 1: Delete Render Database (If Migrating to Supabase)

If you're fully migrating to Supabase, you can just delete the Render database:

### Steps:

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Navigate to your PostgreSQL database service**
3. **Click on the database service**
4. **Go to "Settings" tab**
5. **Scroll down to "Danger Zone"**
6. **Click "Delete Database"**
7. **Confirm deletion** (type the database name to confirm)

### After Deletion:

- The database service will be removed
- You can delete the database service entirely
- Your backend will now use Supabase (once `DATABASE_URL` is updated)

## Option 2: Create Fresh Database on Render (Keep Render)

If you want to keep using Render but start fresh:

### Step 1: Delete Old Database

1. Go to Render Dashboard
2. Navigate to your PostgreSQL database
3. Settings → Danger Zone → Delete Database
4. Confirm deletion

### Step 2: Create New Database

1. **In Render Dashboard**, click **"New +"**
2. **Select "PostgreSQL"**
3. **Configure**:
   - **Name**: `liquid-canvas-db` (or your preferred name)
   - **Database**: `liquidcanvas` (or your preferred name)
   - **User**: `liquidcanvas` (or your preferred name)
   - **Region**: Same as your backend service
   - **PostgreSQL Version**: Latest (15 or 16)
   - **Plan**: Free tier (or your preferred plan)
4. **Click "Create Database"**
5. **Wait 2-3 minutes** for database to be ready

### Step 3: Get New Connection String

1. **Click on your new database service**
2. **Go to "Info" tab**
3. **Copy "Internal Database URL"** (for Render services)
   - Format: `postgresql://user:password@host:port/database`
4. **Or copy "External Connection String"** (for local/other services)

### Step 4: Update Backend Environment Variable

1. **Go to your Backend Service** on Render
2. **Navigate to "Environment" tab**
3. **Update `DATABASE_URL`**:
   ```
   postgresql://user:password@host:port/database
   ```
   Replace with your new database connection string
4. **Click "Save Changes"**
5. **Render will automatically redeploy**

### Step 5: Run Migrations

Migrations will run automatically if `AUTO_MIGRATE=true` is set, or:

1. **Check deployment logs** for migration output
2. **Or run manually** (if needed):
   ```bash
   cd backend
   alembic upgrade head
   ```

## Option 3: Backup Before Deletion (Recommended)

If you want to keep a backup before deleting:

### Export Data from Render Database

1. **Install PostgreSQL client** (if not already):
   ```bash
   # Windows (PowerShell)
   # Download from: https://www.postgresql.org/download/windows/
   
   # Or use Docker
   docker run -it --rm postgres:15 psql [connection-string]
   ```

2. **Export database**:
   ```bash
   pg_dump -h [render-host] -U [user] -d [database] > backup.sql
   ```
   
   Or use Render's built-in backup:
   - Go to Database → Backups
   - Click "Create Backup"
   - Download when ready

3. **Save backup file** somewhere safe

### Restore to New Database (If Needed)

```bash
psql -h [new-host] -U [user] -d [database] < backup.sql
```

## Quick Checklist

### If Migrating to Supabase:
- [ ] Set up Supabase project
- [ ] Get Supabase connection string
- [ ] Update `DATABASE_URL` in Render backend environment
- [ ] Delete Render database (optional - saves costs)
- [ ] Verify backend connects to Supabase
- [ ] Run migrations on Supabase

### If Keeping Render:
- [ ] Export/backup current database (optional)
- [ ] Delete old Render database
- [ ] Create new Render database
- [ ] Get new connection string
- [ ] Update `DATABASE_URL` in backend environment
- [ ] Verify backend connects
- [ ] Run migrations

## Verification Steps

After resetting database:

1. **Check Backend Logs**:
   ```
   ✅ Database connectivity verified
   Attempting to connect to database at: [host]:[port]
   ```

2. **Test Health Endpoint**:
   ```bash
   curl https://your-backend-url/api/health
   ```
   Should return: `{"status": "healthy", "database": "connected"}`

3. **Check Database**:
   - **Render**: Go to Database → Connect → Use Table Editor
   - **Supabase**: Go to Table Editor
   - Should see empty tables (or tables with migrations applied)

4. **Test API Endpoints**:
   ```bash
   # Should work but return empty results
   curl https://your-backend-url/api/prospects
   ```

## Common Issues

### "Database does not exist"
- Wait a few more minutes for database to be fully ready
- Check connection string is correct

### "Connection refused"
- Check database is running (green status in Render)
- Verify connection string format
- Check firewall/network settings

### "Migration errors"
- Check Alembic version: `alembic current`
- Check logs for specific error
- May need to reset: `alembic downgrade base` then `alembic upgrade head`

## Cost Considerations

- **Render Free Tier**: 90 days free, then $7/month per database
- **Supabase Free Tier**: 500MB database, 2GB bandwidth (permanent free tier)
- **Recommendation**: If migrating to Supabase, delete Render database to save costs

## Next Steps After Reset

1. ✅ Database reset complete
2. ✅ Migrations applied
3. ✅ Backend connected
4. ✅ Test API endpoints
5. ✅ Start using the application

Your database is now fresh and ready! 🎉

