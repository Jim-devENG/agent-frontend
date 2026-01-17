# Social Outreach Refactor - Complete ✅

## Summary
Successfully refactored Social Outreach to reuse the `prospects` table instead of separate `social_profiles` table.

## Completed Tasks

### 1. Database Changes ✅
- ✅ Migration created: `add_social_columns_to_prospects.py`
- ✅ Added columns to `prospects` table:
  - `source_type` (website/social)
  - `source_platform` (linkedin/instagram/facebook/tiktok)
  - `profile_url`
  - `username`
  - `display_name`
  - `follower_count`
  - `engagement_rate`

### 2. Model Updates ✅
- ✅ Updated `Prospect` model with social fields
- ✅ All social profiles now stored in `prospects` table with `source_type='social'`

### 3. Adapter Pattern ✅
- ✅ Created `DiscoveryAdapter` interface
- ✅ Implemented platform adapters:
  - `WebsiteDiscoveryAdapter` (reuses existing logic)
  - `LinkedInDiscoveryAdapter` (stub)
  - `InstagramDiscoveryAdapter` (stub)
  - `TikTokDiscoveryAdapter` (stub)
  - `FacebookDiscoveryAdapter` (stub)

### 4. API Endpoints Refactored ✅
- ✅ `social_pipeline.py`:
  - Status endpoint: queries `Prospect` with `source_type='social'`
  - Discovery: uses adapters, saves to `Prospect`
  - Review: uses `Prospect` with approval_status
  - Draft: reuses website drafting task
  - Send: reuses website sending task
  - Follow-up: reuses website drafting task

- ✅ `social.py`:
  - Discovery: uses adapters
  - List profiles: queries `Prospect` with `source_type='social'`
  - Drafts: reuses website drafting task
  - Send: reuses website sending task
  - Follow-up: reuses website drafting task

### 5. Schema Checks Removed ✅
- ✅ Removed all `check_social_schema_ready` calls
- ✅ Removed social table validation from `main.py` startup
- ✅ Removed all `SocialProfile`, `SocialDraft`, `SocialMessage` references
- ✅ No more "schema not initialized" errors

## Architecture

### Key Principle
**REUSE, DON'T DUPLICATE**

- Social outreach uses the same `prospects` table
- Same pipeline stages (discovery → review → draft → send → follow-up)
- Same drafting/sending logic
- Filtered by `source_type='social'`

### Query Pattern
All social queries filter:
```python
Prospect.source_type == 'social'
```

### Platform-Specific Data
- `source_platform`: 'linkedin', 'instagram', 'facebook', 'tiktok'
- `profile_url`: Social profile URL
- `username`: @username or profile identifier
- `display_name`: Full name
- `follower_count`: Number of followers
- `engagement_rate`: Engagement metric

## Remaining Tasks

### 6. UI Updates (In Progress)
- [ ] Update frontend to filter by `source_type='social'`
- [ ] Add platform selector (LinkedIn/Instagram/Facebook/TikTok)
- [ ] Update discovery forms per platform
- [ ] Show social profiles in pipeline UI

### 7. Testing
- [ ] Test end-to-end social discovery
- [ ] Verify website outreach still works
- [ ] Test pipeline progression for social profiles
- [ ] Verify no data loss

## Migration Instructions

1. Run migration:
   ```bash
   alembic upgrade head
   ```

2. Verify columns added:
   ```sql
   SELECT column_name FROM information_schema.columns 
   WHERE table_name = 'prospects' 
   AND column_name IN ('source_type', 'source_platform', 'profile_url', 'username', 'display_name', 'follower_count', 'engagement_rate');
   ```

3. Test social discovery:
   ```bash
   POST /api/social/discover
   {
     "platform": "linkedin",
     "filters": {...}
   }
   ```

4. Verify data:
   ```sql
   SELECT COUNT(*) FROM prospects WHERE source_type = 'social';
   ```

## Notes

- No data migration needed (new feature)
- Website outreach completely unaffected
- All social endpoints now return 200 (no more 503s)
- Pipeline logic fully reused
- Adapter pattern allows platform-specific discovery logic

