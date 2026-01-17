# Fix Your Render PostgreSQL Connection String

## Your Current Connection String

```
postgresql://db_liquidcanvas_user:4c3vuhonCX7vyd7QfmgO9y2XPrgTrfx4@dpg-d5hdk6ur433s73bmro40-a/db_liquidcanvas
```

## Issues Found

1. ❌ **Missing `+asyncpg`** - Needs to be `postgresql+asyncpg://`
2. ❌ **Missing full hostname** - Should have `.oregon-postgres.render.com` (or your region)
3. ❌ **Missing port** - Should have `:5432`

---

## ✅ Corrected Connection String

### Option 1: Oregon Region (Most Common)

```
postgresql+asyncpg://db_liquidcanvas_user:4c3vuhonCX7vyd7QfmgO9y2XPrgTrfx4@dpg-d5hdk6ur433s73bmro40-a.oregon-postgres.render.com:5432/db_liquidcanvas
```

### Option 2: Frankfurt Region

```
postgresql+asyncpg://db_liquidcanvas_user:4c3vuhonCX7vyd7QfmgO9y2XPrgTrfx4@dpg-d5hdk6ur433s73bmro40-a.frankfurt-postgres.render.com:5432/db_liquidcanvas
```

### Option 3: Singapore Region

```
postgresql+asyncpg://db_liquidcanvas_user:4c3vuhonCX7vyd7QfmgO9y2XPrgTrfx4@dpg-d5hdk6ur433s73bmro40-a.singapore-postgres.render.com:5432/db_liquidcanvas
```

### Option 4: Virginia/Ohio (us-east)

```
postgresql+asyncpg://db_liquidcanvas_user:4c3vuhonCX7vyd7QfmgO9y2XPrgTrfx4@dpg-d5hdk6ur433s73bmro40-a.ohio-postgres.render.com:5432/db_liquidcanvas
```

---

## How to Find Your Region

1. **Go to**: Render Dashboard → Your PostgreSQL Database
2. **Click** on your database
3. **Look for** region information (usually shown in database details)
   - Should say something like "Region: Oregon" or "Region: Frankfurt"

**If you can't find it:**
- Try **Option 1 (Oregon)** first - it's the most common
- If that doesn't work, try the other options one by one

---

## Steps to Fix

1. **Go to**: https://dashboard.render.com
2. **Click** your backend service
3. **Go to**: Environment tab
4. **Find** `DATABASE_URL`
5. **Click Edit**
6. **Replace** the entire value with the corrected connection string above
7. **Use Option 1 (Oregon)** if you're not sure which region
8. **Save Changes**
9. **Wait for redeploy** (2-5 minutes)

---

## Changes Made

**From:**
```
postgresql://db_liquidcanvas_user:4c3vuhonCX7vyd7QfmgO9y2XPrgTrfx4@dpg-d5hdk6ur433s73bmro40-a/db_liquidcanvas
```

**To (Oregon example):**
```
postgresql+asyncpg://db_liquidcanvas_user:4c3vuhonCX7vyd7QfmgO9y2XPrgTrfx4@dpg-d5hdk6ur433s73bmro40-a.oregon-postgres.render.com:5432/db_liquidcanvas
```

**Changes:**
1. ✅ Changed `postgresql://` to `postgresql+asyncpg://`
2. ✅ Added `.oregon-postgres.render.com` after hostname
3. ✅ Added `:5432` port number

---

## After Fixing

Once you update and redeploy:

1. ✅ **Check logs** - Should see:
   ```
   ✅ Using Render PostgreSQL (port 5432) - internal network, should work fine
   🔗 Attempting to connect to: dpg-d5hdk6ur433s73bmro40-a.oregon-postgres.render.com:5432
   ✅ Async engine created successfully
   ```

2. ✅ **Test health endpoint:**
   ```
   https://agent-liquidcanvas-9y2s.onrender.com/health/ready
   ```
   Should return: `{"status":"ready","database":"connected"}`

3. ✅ **Test database query:**
   ```
   https://agent-liquidcanvas-9y2s.onrender.com/api/prospects?limit=10
   ```
   Should return data or empty array (not errors)

4. ✅ **Run migrations** (if needed):
   ```bash
   cd backend
   alembic upgrade head
   ```

---

## Quick Action: Update Now

**Copy this connection string** (Oregon region - most common):

```
postgresql+asyncpg://db_liquidcanvas_user:4c3vuhonCX7vyd7QfmgO9y2XPrgTrfx4@dpg-d5hdk6ur433s73bmro40-a.oregon-postgres.render.com:5432/db_liquidcanvas
```

1. Go to Render → Your Backend Service → Environment tab
2. Edit `DATABASE_URL`
3. Replace with the string above
4. Save and wait for redeploy

**If Oregon doesn't work, try the other regions above!** 🚀

