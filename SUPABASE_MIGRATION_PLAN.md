# Complete Supabase Migration Plan

## Overview

This guide covers migrating your entire application to use Supabase for database and authentication, while keeping your Python backend/worker on a compatible hosting platform.

## What Supabase Provides

✅ **PostgreSQL Database** - Managed PostgreSQL with connection pooling  
✅ **Authentication** - Built-in auth with email/password, OAuth, magic links  
✅ **Real-time** - Real-time subscriptions for live updates  
✅ **Storage** - File storage (if needed)  
✅ **Edge Functions** - Serverless functions (TypeScript/Deno, not Python)

## What We'll Keep on Render/Railway/Vercel

- **Backend API** (FastAPI) - Python apps need external hosting
- **Worker Service** (Python RQ) - Python workers need external hosting
- **Redis** - Moving to Upstash (serverless Redis, works great with Supabase)

## Architecture After Migration

```
┌─────────────────┐
│   Frontend      │  (Vercel)
│   (Next.js)     │  ── Uses Supabase Auth Client
└────────┬────────┘
         │
         ├──► Supabase Auth (JWT tokens)
         │
         └──► Backend API (Render/Railway)
              │
              ├──► Supabase PostgreSQL (via connection string)
              │
              └──► Worker (Render/Railway)
                   │
                   ├──► Supabase PostgreSQL
                   └──► Upstash Redis (serverless)
```

## Migration Steps

### Phase 1: Set Up Supabase

#### Step 1.1: Create Supabase Project

1. Go to https://supabase.com
2. Sign up / Log in
3. Click "New Project"
4. Fill in:
   - **Name**: `liquidcanvas` (or your preferred name)
   - **Database Password**: Generate a strong password (save it!)
   - **Region**: Choose closest to you
5. Wait ~2 minutes for project to initialize

#### Step 1.2: Get Connection Strings

1. Go to **Settings** → **Database**
2. Find **Connection string** section
3. Copy the **URI** connection string:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
   ```
4. Also note:
   - **Project URL**: `https://[PROJECT-REF].supabase.co`
   - **Anon Key**: Found in Settings → API
   - **Service Role Key**: Found in Settings → API (keep secret!)

### Phase 2: Migrate Database

#### Step 2.1: Export Current Database Schema

```bash
# From your local machine or Render shell
pg_dump $DATABASE_URL --schema-only > schema.sql
```

#### Step 2.2: Create Tables in Supabase

1. Go to Supabase Dashboard → **SQL Editor**
2. Run your Alembic migrations OR import schema.sql
3. Or run migrations directly:
   ```bash
   # Update DATABASE_URL to Supabase connection string
   export DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres"
   cd backend
   alembic upgrade head
   ```

#### Step 2.2: Migrate Data (Optional - if you have existing data)

```bash
# Export data from Render
pg_dump $OLD_DATABASE_URL --data-only > data.sql

# Import to Supabase (update connection string)
psql "postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres" < data.sql
```

### Phase 3: Update Backend to Use Supabase

#### Step 3.1: Update Database Connection

The connection string format is compatible! Just update `DATABASE_URL`:

```python
# backend/app/db/database.py
# No code changes needed - just update environment variable!
# Supabase uses standard PostgreSQL connection strings
```

#### Step 3.2: Update Environment Variables

In Render dashboard, update:
```
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

**Note**: Supabase uses connection pooling. For better performance, use the **Session** mode connection string (found in Supabase Dashboard → Settings → Database → Connection Pooling).

### Phase 4: Replace Auth with Supabase Auth

#### Step 4.1: Install Supabase Python Client

```bash
cd backend
pip install supabase
```

Add to `requirements.txt`:
```
supabase==2.3.0
```

#### Step 4.2: Update Auth Endpoints

Replace `backend/app/api/auth.py` to use Supabase Auth instead of custom JWT.

#### Step 4.3: Update Environment Variables

Add to Render:
```
SUPABASE_URL=https://[PROJECT-REF].supabase.co
SUPABASE_SERVICE_ROLE_KEY=[SERVICE-ROLE-KEY]  # For backend operations
SUPABASE_ANON_KEY=[ANON-KEY]  # For public operations
```

### Phase 5: Set Up Upstash Redis

Since Supabase doesn't provide Redis, we'll use Upstash (serverless Redis):

1. Go to https://upstash.com
2. Sign up / Log in
3. Create a new Redis database
4. Choose **Global** region (or closest to you)
5. Copy the **UPSTASH_REDIS_REST_URL** and **UPSTASH_REDIS_REST_TOKEN**

#### Update Worker

Update `REDIS_URL` in Render to use Upstash:
```
REDIS_URL=redis://default:[TOKEN]@[ENDPOINT]:6379
```

Or use Upstash REST API (better for serverless):
```python
# worker/worker.py
from upstash_redis import Redis

redis = Redis(url=UPSTASH_REDIS_REST_URL, token=UPSTASH_REDIS_REST_TOKEN)
```

### Phase 6: Update Frontend

#### Step 6.1: Install Supabase Client

```bash
cd frontend
npm install @supabase/supabase-js
```

#### Step 6.2: Create Supabase Client

Create `frontend/lib/supabase.ts`:
```typescript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

#### Step 6.3: Update Auth Flow

Replace login/logout in frontend to use Supabase Auth instead of custom JWT.

### Phase 7: Deploy and Test

1. Update all environment variables in Render
2. Redeploy backend and worker
3. Update frontend environment variables in Vercel
4. Redeploy frontend
5. Test authentication flow
6. Test database operations
7. Test worker jobs

## Environment Variables Summary

### Backend/Worker (Render)

```env
# Database (Supabase)
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres

# Supabase Auth
SUPABASE_URL=https://[PROJECT-REF].supabase.co
SUPABASE_SERVICE_ROLE_KEY=[SERVICE-ROLE-KEY]

# Redis (Upstash)
REDIS_URL=redis://default:[TOKEN]@[ENDPOINT]:6379
# OR for REST API:
UPSTASH_REDIS_REST_URL=https://[ENDPOINT]
UPSTASH_REDIS_REST_TOKEN=[TOKEN]

# Third-party APIs (unchanged)
DATAFORSEO_LOGIN=...
DATAFORSEO_PASSWORD=...
HUNTER_IO_API_KEY=...
GEMINI_API_KEY=...
GMAIL_CLIENT_ID=...
GMAIL_CLIENT_SECRET=...
GMAIL_REFRESH_TOKEN=...
```

### Frontend (Vercel)

```env
NEXT_PUBLIC_SUPABASE_URL=https://[PROJECT-REF].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[ANON-KEY]
NEXT_PUBLIC_API_BASE_URL=https://your-backend.onrender.com/api
```

## Benefits After Migration

✅ **Free Database** - Supabase free tier (500 MB, 2 GB bandwidth)  
✅ **Better Auth** - Built-in auth with email/password, OAuth, magic links  
✅ **Real-time** - Can add real-time job status updates  
✅ **Better Dashboard** - Supabase has excellent database UI  
✅ **Connection Pooling** - Built-in PgBouncer for better performance  
✅ **Automatic Backups** - Daily backups included  
✅ **Row Level Security** - Can add RLS policies if needed  

## Cost Comparison

### Before (Render)
- Database: $7/month (after 90-day free trial)
- Backend: Free (spins down) or $7/month
- Worker: Free (spins down) or $7/month
- Redis: Free (limited) or $7/month
- **Total**: ~$7-28/month

### After (Supabase + Render)
- Database: **FREE** (Supabase free tier)
- Backend: Free (Render) or $7/month
- Worker: Free (Render) or $7/month
- Redis: **FREE** (Upstash free tier: 10K commands/day)
- **Total**: **$0-14/month** (saves $7-14/month)

## Next Steps

1. ✅ Create Supabase project
2. ✅ Export current database schema
3. ✅ Run migrations in Supabase
4. ✅ Update backend database connection
5. ✅ Replace auth with Supabase Auth
6. ✅ Set up Upstash Redis
7. ✅ Update frontend to use Supabase Auth
8. ✅ Deploy and test

## Troubleshooting

### Connection Issues
- Use **Session** mode connection string for better compatibility
- Check firewall settings in Supabase Dashboard
- Verify password is correct

### Auth Issues
- Ensure `SUPABASE_SERVICE_ROLE_KEY` is used in backend (not anon key)
- Check Supabase Auth settings in dashboard
- Verify email templates are configured

### Redis Issues
- Upstash REST API is more reliable than direct Redis connection
- Check rate limits (free tier: 10K commands/day)

