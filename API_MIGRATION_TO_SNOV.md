# API Migration: Hunter.io → Snov.io

## Summary

Replaced Hunter.io with Snov.io for email enrichment. Removed all Hunter.io references and updated code to use Snov.io API.

## Changes Made

### 1. New Snov.io Client
- **Created**: `backend/app/clients/snov.py`
- **Replaces**: `backend/app/clients/hunter.py`
- **Features**:
  - Domain search
  - Email verification
  - Email finder
  - OAuth2 authentication

### 2. Updated Services
- **`backend/app/services/enrichment.py`**: Now uses `SnovIOClient` instead of `HunterIOClient`
- **`backend/app/tasks/enrichment.py`**: Updated all references from Hunter to Snov
- **`backend/app/api/settings.py`**: Updated service status checks and test endpoints

### 3. Updated Models
- **`backend/app/models/prospect.py`**: Changed `hunter_payload` to `snov_payload`

### 4. Environment Variables

**Old (Hunter.io):**
```
HUNTER_IO_API_KEY=...
```

**New (Snov.io):**
```
SNOV_USER_ID=39d57b684e12e180f20497dfd83d6373
SNOV_SECRET=d3caa8f44d382dcc17d31669d4fb073a
```

## Database Migration Required

The Prospect model has changed from `hunter_payload` to `snov_payload`. You need to:

1. **Create Alembic migration:**
```bash
cd backend
alembic revision -m "rename_hunter_payload_to_snov_payload"
```

2. **Edit the migration file** to rename the column:
```python
def upgrade():
    op.rename_table('prospects', 'prospects')  # No table rename needed
    op.alter_column('prospects', 'hunter_payload', new_column_name='snov_payload')

def downgrade():
    op.alter_column('prospects', 'snov_payload', new_column_name='hunter_payload')
```

3. **Run migration:**
```bash
alembic upgrade head
```

**OR** manually in SQL:
```sql
ALTER TABLE prospects RENAME COLUMN hunter_payload TO snov_payload;
```

## Files Changed

### Backend
- ✅ `backend/app/clients/snov.py` (NEW)
- ✅ `backend/app/services/enrichment.py`
- ✅ `backend/app/tasks/enrichment.py`
- ✅ `backend/app/api/settings.py`
- ✅ `backend/app/models/prospect.py`

### To Remove (Optional)
- ❌ `backend/app/clients/hunter.py` (can be deleted)
- ❌ `backend/scripts/test_hunter_api.py` (can be deleted)

## API Configuration

### Snov.io API Credentials
- **User ID**: `39d57b684e12e180f20497dfd83d6373`
- **Secret**: `d3caa8f44d382dcc17d31669d4fb073a`

### Environment Variables to Update

**In Render Dashboard → Environment Variables:**

Remove:
```
HUNTER_IO_API_KEY=...
```

Add:
```
SNOV_USER_ID=39d57b684e12e180f20497dfd83d6373
SNOV_SECRET=d3caa8f44d382dcc17d31669d4fb073a
```

## Testing

After deployment, test the Snov.io integration:

1. **Test via Settings API:**
```bash
curl https://your-backend.onrender.com/api/settings/services/Snov.io/test
```

2. **Test enrichment:**
```bash
curl -X POST https://your-backend.onrender.com/api/prospects/enrich/direct?domain=example.com
```

## Remaining APIs

After this migration, the system uses:
- ✅ **DataForSEO** - Website discovery
- ✅ **Snov.io** - Email enrichment (replaces Hunter.io)
- ✅ **Google Gemini** - Email composition
- ✅ **Gmail API** - Email sending

All other third-party APIs have been removed.

## Notes

- Snov.io uses OAuth2 authentication (different from Hunter.io's API key)
- Response format is compatible (converted to match Hunter.io format)
- Rate limiting handling is similar
- Database column rename is required for existing data

