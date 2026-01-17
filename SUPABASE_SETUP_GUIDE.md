# Supabase Setup Guide - Step by Step

## Quick Start Checklist

- [ ] Create Supabase project
- [ ] Get connection strings and API keys
- [ ] Run database migrations
- [ ] Update backend environment variables
- [ ] Update frontend environment variables
- [ ] Test authentication
- [ ] Set up Upstash Redis

## Step 1: Create Supabase Project

1. Go to https://supabase.com
2. Click **"Start your project"** or **"Sign in"**
3. Click **"New Project"**
4. Fill in:
   - **Name**: `liquidcanvas` (or your choice)
   - **Database Password**: 
     - Click "Generate a password" or create your own
     - **SAVE THIS PASSWORD** - you'll need it!
   - **Region**: Choose closest to you (e.g., `US East (North Virginia)`)
5. Click **"Create new project"**
6. Wait 2-3 minutes for setup to complete

## Step 2: Get Your Credentials

### 2.1: Database Connection String

1. Go to **Settings** → **Database**
2. Scroll to **Connection string** section
3. Select **URI** tab
4. Copy the connection string:
   ```
   postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
   ```
   
   **OR** for direct connection (Session mode):
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
   ```

**Important**: 
- Use **Session** mode for migrations and direct connections
- Use **Transaction** mode for connection pooling (better for production)

### 2.2: API Keys

1. Go to **Settings** → **API**
2. Copy these values:
   - **Project URL**: `https://[PROJECT-REF].supabase.co`
   - **anon public** key: `eyJhbGc...` (for frontend)
   - **service_role** key: `eyJhbGc...` (for backend - keep secret!)

### 2.3: Project Reference

Your project reference is in the URL: `https://supabase.com/dashboard/project/[PROJECT-REF]`

## Step 3: Run Database Migrations

### Option A: Using Alembic (Recommended)

1. Update your `DATABASE_URL` environment variable:
   ```bash
   export DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres"
   ```

2. Run migrations:
   ```bash
   cd backend
   alembic upgrade head
   ```

### Option B: Using Supabase SQL Editor

1. Go to Supabase Dashboard → **SQL Editor**
2. Click **"New query"**
3. Run your migration SQL files one by one
4. Or paste your schema SQL

### Option C: Import from Existing Database

If you have data in Render PostgreSQL:

```bash
# Export from Render
pg_dump $OLD_DATABASE_URL > backup.sql

# Import to Supabase (update connection string)
psql "postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres" < backup.sql
```

## Step 4: Create First User (Optional)

Supabase Auth doesn't require pre-creating users, but you can:

1. Go to **Authentication** → **Users**
2. Click **"Add user"** → **"Create new user"**
3. Enter:
   - **Email**: your email
   - **Password**: your password
   - **Auto Confirm User**: ✅ (check this)
4. Click **"Create user"**

Or let users sign up via the frontend!

## Step 5: Update Backend Environment Variables

In Render Dashboard → Your Backend Service → **Environment**:

### Remove (if using Supabase Auth):
```
JWT_SECRET_KEY=...
ADMIN_USERNAME=...
ADMIN_PASSWORD=...
```

### Add:
```
# Supabase
SUPABASE_URL=https://[PROJECT-REF].supabase.co
SUPABASE_SERVICE_ROLE_KEY=[SERVICE-ROLE-KEY]
SUPABASE_ANON_KEY=[ANON-KEY]  # Optional, for public operations

# Database (update to Supabase)
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

**Note**: For better performance, use connection pooling URL:
```
DATABASE_URL=postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?pgbouncer=true
```

## Step 6: Update Backend Code

### Option A: Use New Supabase Auth (Recommended)

1. Update `backend/app/main.py` to use Supabase auth router:
   ```python
   from app.api import auth_supabase
   app.include_router(auth_supabase.router, prefix="/api/auth", tags=["auth"])
   ```

2. Update dependencies in endpoints:
   ```python
   # Old:
   from app.api.auth import get_current_user
   
   # New:
   from app.api.auth_supabase import get_current_user
   ```

### Option B: Keep Old Auth (Temporary)

You can keep both auth systems during migration. Just update the router in `main.py` when ready.

## Step 7: Update Frontend Environment Variables

In Vercel Dashboard → Your Project → **Settings** → **Environment Variables**:

### Add:
```
NEXT_PUBLIC_SUPABASE_URL=https://[PROJECT-REF].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[ANON-KEY]
```

### Keep:
```
NEXT_PUBLIC_API_BASE_URL=https://your-backend.onrender.com/api
```

## Step 8: Update Frontend Code

### Install Supabase Client

```bash
cd frontend
npm install @supabase/supabase-js
```

### Update Login Component

Replace your login logic to use Supabase:

```typescript
import { signIn } from '@/lib/supabase'

// In your login component:
const handleLogin = async (email: string, password: string) => {
  try {
    const { session } = await signIn(email, password)
    if (session) {
      // Store token for API calls
      localStorage.setItem('auth_token', session.access_token)
      router.push('/')
    }
  } catch (error) {
    console.error('Login failed:', error)
  }
}
```

### Update API Client

Update `frontend/lib/api.ts` to get token from Supabase:

```typescript
import { getAccessToken } from '@/lib/supabase'

async function getAuthToken(): Promise<string | null> {
  // Try Supabase first
  const supabaseToken = await getAccessToken()
  if (supabaseToken) return supabaseToken
  
  // Fallback to localStorage (for migration period)
  return localStorage.getItem('auth_token')
}
```

## Step 9: Set Up Upstash Redis

Since Supabase doesn't provide Redis, use Upstash (serverless Redis):

1. Go to https://upstash.com
2. Sign up / Log in
3. Click **"Create Database"**
4. Fill in:
   - **Name**: `liquidcanvas-redis`
   - **Type**: **Regional** (or Global for multi-region)
   - **Region**: Choose closest to you
5. Click **"Create"**
6. Copy:
   - **UPSTASH_REDIS_REST_URL**: `https://[ENDPOINT]`
   - **UPSTASH_REDIS_REST_TOKEN**: `[TOKEN]`

### Update Worker

In Render Dashboard → Worker Service → **Environment**:

```
# Option 1: Direct Redis connection (if Upstash supports it)
REDIS_URL=redis://default:[TOKEN]@[ENDPOINT]:6379

# Option 2: REST API (better for serverless)
UPSTASH_REDIS_REST_URL=https://[ENDPOINT]
UPSTASH_REDIS_REST_TOKEN=[TOKEN]
```

### Update Worker Code (if using REST API)

Install Upstash Redis client:
```bash
cd worker
pip install upstash-redis
```

Update `worker/worker.py`:
```python
from upstash_redis import Redis
import os

redis_url = os.getenv("UPSTASH_REDIS_REST_URL")
redis_token = os.getenv("UPSTASH_REDIS_REST_TOKEN")

if redis_url and redis_token:
    redis_conn = Redis(url=redis_url, token=redis_token)
else:
    # Fallback to regular Redis
    import redis
    redis_conn = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
```

## Step 10: Test Everything

### Test Database Connection

```bash
# In Render Shell or locally
psql "postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres" -c "SELECT 1;"
```

### Test Authentication

1. Go to your frontend
2. Try to sign up with a new email
3. Check Supabase Dashboard → **Authentication** → **Users** - you should see the new user
4. Try logging in
5. Test protected API endpoints

### Test Worker

1. Create a discovery job from frontend
2. Check worker logs in Render
3. Verify job processes correctly
4. Check database for new prospects

## Troubleshooting

### "Connection refused" or "Timeout"

- Check firewall settings in Supabase Dashboard → **Settings** → **Database**
- Use **Session** mode connection string for direct connections
- Use **Transaction** mode for connection pooling

### "Invalid API key"

- Verify you're using the correct key:
  - **Anon key** for frontend
  - **Service role key** for backend
- Check key hasn't been regenerated

### "User not found" after login

- Check Supabase Dashboard → **Authentication** → **Users**
- Verify user was created
- Check email confirmation settings (may need to auto-confirm)

### Migration errors

- Ensure you're using **Session** mode connection string for migrations
- Check database password is correct
- Verify network access (Supabase may need IP whitelist for some operations)

## Next Steps

After setup:

1. ✅ Test all authentication flows
2. ✅ Test database operations
3. ✅ Test worker jobs
4. ✅ Monitor Supabase dashboard for usage
5. ✅ Set up backups (automatic in Supabase)
6. ✅ Consider enabling Row Level Security (RLS) for data protection

## Cost Monitoring

Supabase Free Tier Limits:
- **Database**: 500 MB storage, 2 GB bandwidth/month
- **Auth**: Unlimited users
- **API Requests**: 50,000/month
- **Storage**: 1 GB

Monitor usage in Supabase Dashboard → **Settings** → **Usage**

