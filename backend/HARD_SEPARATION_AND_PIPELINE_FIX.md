# Hard Separation and Pipeline Reset Fix

## Summary

Fixed hard separation between Website Outreach and Social Outreach, added CSV exports, and ensured pipeline state resets properly.

## PART 1 — HARD SEPARATION

### How separation is enforced:

**Backend API Endpoints:**

1. **`list_websites`** (`/api/prospects/websites`):
   - Filters by: `source_type='website' OR source_type IS NULL`
   - Excludes: All social profiles (LinkedIn, Instagram, Facebook, TikTok)
   - Implementation: Direct query with `website_filter = or_(Prospect.source_type == 'website', Prospect.source_type.is_(None))`

2. **`list_leads`** (`/api/prospects/leads`):
   - Already filters by: `source_type='website' OR source_type IS NULL`
   - Excludes: All social profiles
   - Status: ✅ Already correctly implemented

3. **`list_scraped_emails`** (`/api/prospects/scraped-emails`):
   - Now filters by: `source_type='website' OR source_type IS NULL`
   - Excludes: All social profiles
   - Implementation: Added `website_filter` to count and query

4. **Social Endpoints** (`/api/social/*`):
   - Filter by: `source_type='social'`
   - Platform-specific filtering: `source_platform IN ('linkedin', 'instagram', 'facebook', 'tiktok')`

**Frontend:**
- Website Outreach tabs use endpoints that filter by `source_type='website'`
- Social Outreach tabs use `/api/social/*` endpoints
- No shared data between the two systems

**Database:**
- All prospects stored in `prospects` table
- `source_type` column: `'website'`, `'social'`, or `NULL` (legacy = website)
- `source_platform` column: `'linkedin'`, `'instagram'`, `'facebook'`, `'tiktok'` (for social only)

## PART 2 — DISCOVERY PIPELINE RESET

### How pipeline state is recalculated:

**Website Outreach:**
1. When discovery completes, `discoveryCompleted` event is dispatched
2. `Pipeline` component listens for this event
3. Triggers `loadStatusDebounced()` which reloads pipeline status
4. Backend recalculates counts based on current database state
5. UI re-evaluates button states based on fresh counts

**Social Outreach:**
1. When discovery completes, `socialDiscoveryCompleted` event is dispatched
2. `SocialPipeline` component listens for this event
3. Triggers `loadStatusDebounced()` which reloads pipeline status
4. Backend recalculates counts for social profiles only
5. UI re-evaluates button states based on fresh counts

### Where pipeline reset occurs:

1. **Website Discovery** (`frontend/components/Pipeline.tsx` - `Step1Discovery`):
   - After `pipelineDiscover()` completes
   - Dispatches: `discoveryCompleted` and `refreshPipelineStatus` events

2. **Social Discovery** (`frontend/components/SocialDiscovery.tsx`):
   - After `discoverSocialProfilesPipeline()` completes
   - Dispatches: `socialDiscoveryCompleted` and `refreshSocialPipelineStatus` events

3. **Pipeline Components**:
   - `Pipeline.tsx`: Listens for `discoveryCompleted` → reloads status
   - `SocialPipeline.tsx`: Listens for `socialDiscoveryCompleted` → reloads status

### How buttons are re-enabled:

- Pipeline status is recalculated from database counts
- Button states are derived from current counts (not historical)
- Examples:
  - If `discovered > 0`, scraping button becomes `active`
  - If `scraped > 0`, verification button becomes `active`
  - If `verified > 0`, drafting button becomes `active`
  - If `drafted > 0`, sending button becomes `active`

## PART 3 — PIPELINE ACTION VISIBILITY

### Current Implementation:

**Website Outreach Pipeline:**
- Step 1 (Discovery): Always `active` (can always discover)
- Step 2 (Scraping): `locked` if `scrape_ready_count === 0`, else `active`/`completed`
- Step 3 (Verification): `locked` if `leads === 0`, else `active`/`completed`
- Step 4 (Drafting): `locked` if `drafting_ready === 0 AND drafted === 0`, else `active`/`completed`
- Step 5 (Sending): `locked` if `send_ready_count === 0 AND drafted === 0`, else `active`/`completed`

**Social Outreach Pipeline:**
- Step 1 (Discovery): Always `active` (can always discover)
- Step 2 (Review): `locked` if `discovered === 0`, else `active`/`completed`
- Step 3 (Drafting): `locked` if `qualified === 0`, else `active`/`completed`
- Step 4 (Sending): `locked` if `drafted === 0`, else `active`/`completed`
- Step 5 (Follow-ups): `locked` if `sent === 0`, else `active`/`completed`

**Note:** Actions are shown based on current state, not historical data. Each discovery run resets the pipeline, and actions become available as data progresses through stages.

## PART 4 — CSV EXPORT

### How export is unified:

**Backend Endpoints:**
- `/api/prospects/websites/export/csv` - Website prospects CSV
- `/api/prospects/leads/export/csv` - Leads CSV
- `/api/prospects/scraped-emails/export/csv` - Scraped emails CSV
- `/api/social/profiles/export/csv` - Social profiles CSV
- `/api/social/drafts/export/csv` - Social drafts CSV
- `/api/social/sent/export/csv` - Social sent CSV

**Frontend Functions:**
- `exportWebsitesCSV()` - Uses `/api/prospects/websites/export/csv`
- `exportLeadsCSV()` - Uses `/api/prospects/leads/export/csv`
- `exportScrapedEmailsCSV()` - Uses `/api/prospects/scraped-emails/export/csv`
- `exportSocialProfilesCSV()` - Uses `/api/social/profiles/export/csv`
- `exportSocialDraftsCSV()` - Uses `/api/social/drafts/export/csv`
- `exportSocialSentCSV()` - Uses `/api/social/sent/export/csv`

**Frontend Components with CSV Export:**
- ✅ `WebsitesTable.tsx` - Download CSV button
- ✅ `LeadsTable.tsx` - Download CSV button (just added)
- ✅ `EmailsTable.tsx` - Download CSV button
- ✅ `SocialProfilesTable.tsx` - Download CSV button
- ✅ `SocialDraftsTable.tsx` - Download CSV button
- ✅ `SocialSentTable.tsx` - Download CSV button

**Export Rules:**
- All exports respect current filters (category, platform, status)
- Exports full dataset (not just visible page)
- Returns CSV Blob for download
- Filenames include date: `{type}_{YYYY-MM-DD}.csv`

## Files Modified

### Backend:
- `backend/app/api/prospects.py`:
  - `list_websites`: Now filters by `source_type='website'`
  - `list_scraped_emails`: Now filters by `source_type='website'`
  - All website endpoints enforce hard separation

### Frontend:
- `frontend/components/LeadsTable.tsx`: Added Download CSV button

## How to Verify Correctness Manually

### 1. Hard Separation:
- **Website Outreach**:
  - Navigate to Websites tab → Should show only websites (domains, not social profiles)
  - Navigate to Leads tab → Should show only website leads
  - Navigate to Emails tab → Should show only website emails
  - Verify: No LinkedIn, Instagram, Facebook, TikTok profiles appear

- **Social Outreach**:
  - Navigate to Social → Profiles tab → Should show only social profiles
  - Verify: No website domains appear
  - Verify: Profiles have platform icons (LinkedIn, Instagram, etc.)

### 2. Pipeline Reset:
- **Website Outreach**:
  1. Run a discovery
  2. Wait for completion
  3. Check Pipeline tab → Buttons should unlock based on new discovery
  4. Run discovery again → Pipeline should reset and re-arm buttons

- **Social Outreach**:
  1. Run a social discovery
  2. Wait for completion
  3. Check Pipeline tab → Buttons should unlock based on new discovery
  4. Run discovery again → Pipeline should reset and re-arm buttons

### 3. Pipeline Action Visibility:
- **Website Outreach**:
  - If websites discovered → Scraping button should be `active`
  - If websites scraped → Verification button should be `active`
  - If leads verified → Drafting button should be `active`
  - If drafts exist → Sending button should be `active`

- **Social Outreach**:
  - If profiles discovered → Review button should be `active`
  - If profiles reviewed → Drafting button should be `active`
  - If drafts exist → Sending button should be `active`
  - If messages sent → Follow-ups button should be `active`

### 4. CSV Export:
- **Website Outreach**:
  - Websites tab → Click "Download CSV" → Should download websites CSV
  - Leads tab → Click "Download CSV" → Should download leads CSV
  - Emails tab → Click "Download CSV" → Should download emails CSV

- **Social Outreach**:
  - Profiles tab → Click "Download CSV" → Should download profiles CSV
  - Drafts tab → Click "Download CSV" → Should download drafts CSV
  - Sent tab → Click "Download CSV" → Should download sent CSV

## Success Criteria Met

- [x] Website Outreach shows ONLY websites (filters by `source_type='website'`)
- [x] Social Outreach shows ONLY social profiles (filters by `source_type='social'`)
- [x] Every discovery re-arms the pipeline (events trigger status reload)
- [x] Action buttons appear when work exists (based on current counts)
- [x] CSV export exists in all tabs (Websites, Leads, Emails, Profiles, Drafts, Sent)

