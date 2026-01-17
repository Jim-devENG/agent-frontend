# Supabase Migration - Quick Start

## 🚀 Fast Track (5 Steps)

### 1. Create Supabase Project
- Go to https://supabase.com → New Project
- Save your database password!

### 2. Get Credentials
- **Settings** → **Database**: Copy connection string
- **Settings** → **API**: Copy Project URL, anon key, service_role key

### 3. Run Migrations
```bash
export DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres"
cd backend
alembic upgrade head
```

### 4. Update Environment Variables

**Render (Backend/Worker):**
```
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
SUPABASE_URL=https://[PROJECT-REF].supabase.co
SUPABASE_SERVICE_ROLE_KEY=[SERVICE-ROLE-KEY]
```

**Vercel (Frontend):**
```
NEXT_PUBLIC_SUPABASE_URL=https://[PROJECT-REF].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[ANON-KEY]
```

### 5. Switch to Supabase Auth

**Backend (`backend/app/main.py`):**
```python
# Replace:
from app.api import auth
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

# With:
from app.api import auth_supabase
app.include_router(auth_supabase.router, prefix="/api/auth", tags=["auth"])
```

**Update dependencies in API files:**
```python
# Old:
from app.api.auth import get_current_user

# New:
from app.api.auth_supabase import get_current_user
```

**Frontend:** Update login to use Supabase client (see `frontend/lib/supabase.ts`)

## 📋 Full Details

See `SUPABASE_SETUP_GUIDE.md` for complete step-by-step instructions.

## ✅ What You Get

- ✅ Free PostgreSQL database (500 MB)
- ✅ Built-in authentication
- ✅ Real-time capabilities
- ✅ Better dashboard
- ✅ Automatic backups
- ✅ Connection pooling

## 💰 Cost Savings

- **Before**: ~$7/month for Render PostgreSQL
- **After**: **FREE** (Supabase free tier)
- **Savings**: $7/month

