# Social Outreach System - Implementation Status

## ✅ Completed

### 1. Design Document
**File:** `backend/SOCIAL_OUTREACH_DESIGN.md`

Complete architectural design including:
- Database schema design
- Platform-specific discovery logic
- Pipeline stages and unlock logic
- API route design
- Frontend routing plan
- Error handling strategy
- Implementation phases

### 2. Updated Models
**File:** `backend/app/models/social.py`

Models updated to match new requirements:
- ✅ `SocialProfile`: Added `username`, `full_name`, `category`, `engagement_score`
- ✅ `SocialProfile`: Added `discovery_status` and `outreach_status` enums
- ✅ `SocialPlatform`: Added `FACEBOOK` support
- ✅ `SocialDiscoveryJob`: Added `categories`, `locations`, `keywords` arrays
- ✅ `SocialMessage`: Added `message_type` enum, `thread_id`, `draft_body`, `sent_body`
- ✅ All enums properly defined: `DiscoveryStatus`, `OutreachStatus`, `MessageType`

### 3. Database Migration
**File:** `backend/alembic/versions/update_social_models_complete_schema.py`

Idempotent migration that:
- Adds all new columns to `social_profiles`
- Creates new enum types
- Updates `social_discovery_jobs` with array columns
- Updates `social_messages` with new fields
- Includes proper downgrade support

## 📋 Next Steps (Implementation Phases)

### Phase 1: Platform Discovery Services ⏳
**Location:** `backend/app/services/social/`

Create directory structure:
```
app/services/social/
├── __init__.py
├── base_discovery.py          # Base class for discovery services
├── linkedin_discovery.py      # LinkedIn-specific discovery
├── instagram_discovery.py     # Instagram-specific discovery
├── tiktok_discovery.py        # TikTok-specific discovery
├── facebook_discovery.py      # Facebook-specific discovery
└── discovery_runner.py        # Orchestrates discovery jobs
```

**Requirements:**
- Each platform service implements `BaseDiscoveryService`
- Platform-specific parameter parsing
- Profile extraction and normalization
- Engagement score calculation
- Error handling and rate limiting

### Phase 2: Separate Pipeline API ⏳
**File:** `backend/app/api/social_pipeline.py` (NEW)

Create completely separate pipeline API:
- `GET /api/social/pipeline/status` - Pipeline status (social tables only)
- `POST /api/social/pipeline/discover` - Stage 1: Discovery
- `POST /api/social/pipeline/review` - Stage 2: Profile Review
- `POST /api/social/pipeline/draft` - Stage 3: Drafting
- `POST /api/social/pipeline/send` - Stage 4: Sending
- `POST /api/social/pipeline/followup` - Stage 5: Follow-ups

**Key Requirements:**
- NO imports from `app/api/pipeline.py`
- NO shared logic with website pipeline
- Pipeline status computed from social tables only
- Stage unlock logic based on social data only

### Phase 3: Pipeline Status Computation ⏳
**Location:** `backend/app/api/social_pipeline.py`

Implement status computation:
```python
async def get_social_pipeline_status(db: AsyncSession):
    """
    Compute pipeline status from social tables ONLY.
    
    Returns:
    {
        "discovered": int,      # discovery_status = 'discovered'
        "reviewed": int,        # discovery_status = 'reviewed'
        "qualified": int,       # discovery_status = 'qualified'
        "drafted": int,         # outreach_status = 'drafted'
        "sent": int,            # outreach_status = 'sent'
        "followup_ready": int,  # outreach_status = 'sent' AND last_contacted_at < threshold
    }
    """
```

**Unlock Logic:**
- Discovery: Always unlocked
- Review: `discovered_count > 0`
- Drafting: `qualified_count > 0`
- Sending: `drafted_count > 0`
- Follow-ups: `sent_count > 0`

### Phase 4: AI Drafting Service ⏳
**Location:** `backend/app/services/social/drafting.py`

Platform-specific AI drafting:
- LinkedIn: Professional tone
- Instagram: Casual, visual-focused
- TikTok: Trendy, engaging
- Facebook: Conversational

**Requirements:**
- Use Gemini API (existing `app/clients/gemini.py`)
- Platform-specific prompts
- Follow-up generation (humorous, clever, non-repetitive)
- Message history tracking

### Phase 5: Message Sending Service ⏳
**Location:** `backend/app/services/social/sending.py`

Platform-specific sending:
- LinkedIn: LinkedIn API integration
- Instagram: Instagram API integration
- TikTok: TikTok API integration
- Facebook: Facebook Messenger API integration

**Requirements:**
- Rate limiting per platform
- Error handling and retry logic
- Message status tracking
- Thread ID management

### Phase 6: Frontend Integration ⏳
**Location:** `frontend/`

1. **Login Flow:**
   - Add card selection UI
   - Store selected outreach type in context
   - Reset app state on switch

2. **Routes:**
   - `/outreach/websites/*` - Existing website routes
   - `/outreach/social/*` - New social routes

3. **Components:**
   - `SocialPipeline.tsx` - Pipeline cards for social
   - `SocialDiscovery.tsx` - Platform selector and filters
   - `SocialProfilesTable.tsx` - Profile review table
   - `SocialDraftsTable.tsx` - Drafts management
   - `SocialSend.tsx` - Sending interface

## 🔒 Separation Guarantees (Verified)

✅ **Database:** All tables prefixed with `social_`, no foreign keys to website tables
✅ **Models:** Separate models in `app/models/social.py`, no imports from `prospect.py`
✅ **API Routes:** Separate router in `app/api/social.py`, will have separate `social_pipeline.py`
✅ **Validation:** Feature-scoped schema checks only (already implemented)
✅ **Error Handling:** Independent error handling (already implemented)

## 🎯 Success Criteria

- [ ] Social outreach works independently of website outreach
- [ ] Missing social tables don't crash website outreach
- [ ] Missing website tables don't crash social outreach
- [ ] Pipeline stages unlock based on social data only
- [ ] Platform-specific discovery works correctly
- [ ] Frontend can switch between outreach types seamlessly
- [ ] No 500 errors for schema validation in requests
- [ ] All endpoints return predictable responses

## 📝 Notes

- **Do not rush implementation** - Design is complete, proceed carefully
- **Platform services first** - Discovery is the foundation
- **Pipeline API second** - Status computation must be accurate
- **Frontend last** - Backend must be stable first

## 🚀 Ready to Deploy

The following can be deployed immediately:
1. ✅ Design document
2. ✅ Updated models
3. ✅ Database migration

These provide the foundation for implementation without breaking existing functionality.

