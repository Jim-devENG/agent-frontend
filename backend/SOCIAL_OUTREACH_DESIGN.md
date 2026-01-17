# Social Outreach System - Complete Design Document

## 🎯 Product Vision

Social Outreach is a **completely separate product** inside the same app, targeting **individual people** (not organizations) across LinkedIn, Facebook, Instagram, and TikTok.

## 🏗️ Architectural Principles

### Separation Guarantees

1. **Database Isolation**
   - All tables prefixed with `social_`
   - No foreign keys to website tables
   - No shared indexes or constraints

2. **Code Isolation**
   - Platform-specific services in `app/services/social/`
   - Separate pipeline logic in `app/api/social_pipeline.py`
   - No imports from website outreach code

3. **Validation Isolation**
   - Feature-scoped schema checks only
   - No global validation on requests
   - Missing tables return 200 with metadata (not 500)

4. **State Isolation**
   - Separate pipeline status computation
   - Independent unlock logic
   - No shared state or cache

## 📊 Database Schema Design

### Table: `social_profiles`

**Purpose:** Individual person profiles discovered from social platforms

```sql
CREATE TABLE social_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform VARCHAR(20) NOT NULL CHECK (platform IN ('linkedin', 'facebook', 'instagram', 'tiktok')),
    username VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    profile_url TEXT NOT NULL UNIQUE,
    bio TEXT,
    location VARCHAR(255),
    category VARCHAR(50),  -- Same categories as website outreach
    followers_count INTEGER DEFAULT 0,
    engagement_score NUMERIC(5,2) DEFAULT 0,  -- Computed engagement metric
    discovery_status VARCHAR(20) NOT NULL DEFAULT 'discovered',
    outreach_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    is_manual BOOLEAN DEFAULT FALSE,
    last_contacted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    
    -- Indexes
    INDEX idx_social_profiles_platform (platform),
    INDEX idx_social_profiles_discovery_status (discovery_status),
    INDEX idx_social_profiles_outreach_status (outreach_status),
    INDEX idx_social_profiles_category (category),
    INDEX idx_social_profiles_username (username)
);
```

**Status Enums:**
- `discovery_status`: `discovered`, `reviewed`, `qualified`, `rejected`
- `outreach_status`: `pending`, `drafted`, `sent`, `followup`, `closed`

### Table: `social_discovery_jobs`

**Purpose:** Discovery job tracking per platform

```sql
CREATE TABLE social_discovery_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform VARCHAR(20) NOT NULL CHECK (platform IN ('linkedin', 'facebook', 'instagram', 'tiktok')),
    categories TEXT[],  -- Array of categories
    locations TEXT[],   -- Array of locations
    keywords TEXT[],    -- Array of keywords
    parameters JSONB,   -- Platform-specific parameters
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    results_count INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Indexes
    INDEX idx_social_discovery_jobs_platform (platform),
    INDEX idx_social_discovery_jobs_status (status)
);
```

**Status Values:** `pending`, `running`, `completed`, `failed`

### Table: `social_messages`

**Purpose:** Message history per profile

```sql
CREATE TABLE social_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    social_profile_id UUID NOT NULL REFERENCES social_profiles(id) ON DELETE CASCADE,
    platform VARCHAR(20) NOT NULL,
    message_type VARCHAR(20) NOT NULL CHECK (message_type IN ('initial', 'followup')),
    draft_body TEXT,
    sent_body TEXT,
    sent_at TIMESTAMP WITH TIME ZONE,
    thread_id UUID,  -- For conversation threading
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    
    -- Indexes
    INDEX idx_social_messages_profile_id (social_profile_id),
    INDEX idx_social_messages_thread_id (thread_id),
    INDEX idx_social_messages_sent_at (sent_at)
);
```

## 🔄 Social Pipeline Stages

### Stage 1: Discovery
- **Unlock:** Always available
- **Action:** Platform-specific discovery
- **Output:** `social_profiles` with `discovery_status = 'discovered'`

### Stage 2: Profile Review
- **Unlock:** `discovered_count > 0`
- **Action:** Manual review and qualification
- **Output:** `discovery_status = 'reviewed'` or `'qualified'`

### Stage 3: Drafting
- **Unlock:** `qualified_count > 0`
- **Action:** Generate drafts (AI-powered, platform-specific)
- **Output:** Drafts saved (not sent)

### Stage 4: Sending
- **Unlock:** `drafted_count > 0`
- **Action:** Send messages via platform APIs
- **Output:** `social_messages` with `sent_at` timestamp

### Stage 5: Follow-ups
- **Unlock:** `sent_count > 0`
- **Action:** Generate follow-up messages (humorous, clever, non-repetitive)
- **Output:** New drafts with `message_type = 'followup'`

## 🔍 Platform-Specific Discovery Logic

### LinkedIn Discovery Service
**Location:** `app/services/social/linkedin_discovery.py`

**Parameters:**
- Job title / role
- Industry
- Location
- Keywords in headline or bio

**Method:**
- Search engine scraping OR LinkedIn Sales Nav queries
- Extract people profiles only
- Ignore companies entirely

### Instagram Discovery Service
**Location:** `app/services/social/instagram_discovery.py`

**Parameters:**
- Hashtags
- Bio keywords
- Location tags
- Follower range

**Method:**
- Hashtag graph traversal
- Bio parsing
- Profile engagement scoring

### TikTok Discovery Service
**Location:** `app/services/social/tiktok_discovery.py`

**Parameters:**
- Niche keywords
- Bio keywords
- Video caption keywords
- Location inference

**Method:**
- Content-first discovery
- Profile extraction from videos

### Facebook Discovery Service
**Location:** `app/services/social/facebook_discovery.py`

**Parameters:**
- Public profile search
- Bio keywords
- Location
- Interests

**Method:**
- Public profile indexing
- Group-based discovery

## 🛣️ API Route Design

### Base Path: `/api/social/`

### Discovery Routes
- `POST /api/social/discover` - Start discovery job
- `GET /api/social/discovery-jobs` - List discovery jobs
- `GET /api/social/discovery-jobs/{job_id}` - Get job status

### Profile Routes
- `GET /api/social/profiles` - List profiles (with filters)
- `GET /api/social/profiles/{profile_id}` - Get profile details
- `PATCH /api/social/profiles/{profile_id}` - Update profile (qualify/reject)
- `POST /api/social/profiles/bulk-qualify` - Bulk qualify profiles

### Pipeline Routes
- `GET /api/social/pipeline/status` - Get pipeline status (counts per stage)
- `POST /api/social/pipeline/discover` - Stage 1: Discovery
- `POST /api/social/pipeline/review` - Stage 2: Review (manual)
- `POST /api/social/pipeline/draft` - Stage 3: Drafting
- `POST /api/social/pipeline/send` - Stage 4: Sending
- `POST /api/social/pipeline/followup` - Stage 5: Follow-ups

### Draft Routes
- `GET /api/social/drafts` - List drafts
- `GET /api/social/drafts/{draft_id}` - Get draft
- `PATCH /api/social/drafts/{draft_id}` - Edit draft
- `DELETE /api/social/drafts/{draft_id}` - Delete draft

### Message Routes
- `GET /api/social/messages` - List sent messages
- `GET /api/social/messages/{message_id}` - Get message details
- `GET /api/social/profiles/{profile_id}/messages` - Get message history for profile

## 🎨 Frontend Routing Plan

### Route Structure
```
/outreach/websites/*  - Website Outreach (existing)
/outreach/social/*    - Social Outreach (new)
```

### Social Routes
- `/outreach/social` - Main dashboard (pipeline cards)
- `/outreach/social/discover` - Discovery stage
- `/outreach/social/profiles` - Profile review stage
- `/outreach/social/drafts` - Drafting stage
- `/outreach/social/send` - Sending stage
- `/outreach/social/followups` - Follow-ups stage

### Login Flow
1. User logs in
2. Show two cards: "Website Outreach" and "Social Outreach"
3. User selects one
4. App context switches entirely
5. All routes and state reset

## 🚨 Error Handling Strategy

### Schema Validation
- **Request-time:** Feature-scoped checks only
- **Missing tables:** Return 200 with `status="inactive"`, `reason="schema not initialized"`
- **Never:** Return 500 for missing social tables

### Platform Errors
- **API failures:** Log and return structured error
- **Rate limits:** Queue and retry
- **Invalid credentials:** Clear error message

### Pipeline Errors
- **Stage not unlocked:** Return 403 with unlock requirements
- **No data:** Return empty arrays, not errors
- **Validation failures:** Return 400 with specific field errors

## 📦 Implementation Phases

### Phase 1: Database Schema
- [ ] Create Alembic migration for `social_profiles`
- [ ] Create Alembic migration for `social_discovery_jobs`
- [ ] Create Alembic migration for `social_messages`
- [ ] Update models in `app/models/social.py`

### Phase 2: Backend Services
- [ ] Create `app/services/social/` directory
- [ ] Implement LinkedIn discovery service
- [ ] Implement Instagram discovery service
- [ ] Implement TikTok discovery service
- [ ] Implement Facebook discovery service
- [ ] Create shared discovery runner

### Phase 3: API Routes
- [ ] Create `app/api/social_pipeline.py` (separate from website pipeline)
- [ ] Implement discovery endpoints
- [ ] Implement profile management endpoints
- [ ] Implement pipeline status endpoint
- [ ] Implement drafting endpoints
- [ ] Implement sending endpoints
- [ ] Implement follow-up endpoints

### Phase 4: Pipeline Logic
- [ ] Implement pipeline status computation (social tables only)
- [ ] Implement stage unlock logic
- [ ] Implement AI drafting (platform-specific)
- [ ] Implement message sending (platform-specific)
- [ ] Implement follow-up generation

### Phase 5: Frontend Integration
- [ ] Create login card selection UI
- [ ] Create social outreach routes
- [ ] Create pipeline cards component
- [ ] Create platform selector
- [ ] Create profile review UI
- [ ] Create drafting UI
- [ ] Create sending UI

## ✅ Separation Guarantees Checklist

- [ ] No shared database tables
- [ ] No shared API routes
- [ ] No shared validation logic
- [ ] No shared pipeline state
- [ ] No shared services
- [ ] No shared models (except Base)
- [ ] No shared schemas
- [ ] Feature-scoped schema validation only
- [ ] Independent error handling
- [ ] Independent logging

## 🎯 Success Criteria

1. Social outreach works independently of website outreach
2. Missing social tables don't crash website outreach
3. Missing website tables don't crash social outreach
4. Pipeline stages unlock based on social data only
5. Platform-specific discovery works correctly
6. Frontend can switch between outreach types seamlessly
7. No 500 errors for schema validation in requests
8. All endpoints return predictable responses

