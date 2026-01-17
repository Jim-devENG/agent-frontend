# Canonical Liquid Canvas Positioning Implementation

## ✅ COMPLETED

### 1. Canonical Business Description
- **Location**: `backend/app/clients/gemini.py`
- **Constant**: `CANONICAL_LIQUID_CANVAS_DESCRIPTION`
- **Description**: Liquid Canvas is a mobile-to-TV streaming art platform (NOT an art services company)

### 2. Updated All Gemini Prompts
- ✅ `compose_email()` - Website email composition
- ✅ `compose_followup_email()` - Follow-up emails
- ✅ `build_chat_prompt()` - Chat refinement
- ✅ `_search_liquid_canvas_info()` - Search prompt updated
- ✅ `_build_positioning_summary()` - Fallback updated
- ✅ Social drafting service (`backend/app/services/social/drafting.py`)

### 3. Social Discovery Qualification Rules
- **Location**: `backend/app/tasks/social_discovery.py`
- **Rules Enforced**:
  - Followers ≥ 1,000 ✅
  - Engagement rate ≥ platform minimum:
    - LinkedIn: 1.0%
    - Instagram: 2.0%
    - Facebook: 1.5%
    - TikTok: 3.0%
- **Status**: ✅ Implemented and enforced at discovery time

### 4. Email Confidence Tracking
- **Location**: `backend/app/models/prospect.py`
- **Field**: `verification_confidence` (Numeric(5, 2))
- **Snov.io**: Returns `confidence_score` (0-100)
- **Status**: ✅ Tracked, but website-found emails default to 50.0

## 📋 VERIFIED WORKING

1. **Social Discovery → Accept/Reject Flow**: ✅ Working
   - Profiles appear in "Discovered" tab with PENDING status
   - Accept/Reject buttons work
   - Accepted profiles move to "Social Leads"

2. **Platform-Specific Discovery Tabs**: ✅ Working
   - LinkedIn, Instagram, Facebook, TikTok tabs exist
   - Each shows only profiles from that platform

3. **Gemini Chat Persistence**: ✅ Working
   - Chat history saved to localStorage per prospect ID
   - Persists across page refreshes

4. **Draft Editor Authority**: ✅ Working
   - Gemini chat is generative only
   - Drafts change only when user clicks "Use This Version"
   - No automatic mutations

## 🔍 AREAS FOR IMPROVEMENT

### 1. Email Confidence for Website Enrichment
**Current**: Website-found emails default to 50.0 confidence
**Recommendation**: 
- Distinguish between personal emails (john@, sarah@) vs generic (info@, support@)
- Personal emails: Higher confidence (70-90)
- Generic emails: Lower confidence (30-50)
- Store email type metadata

### 2. Website Discovery Priority Weighting
**Current**: All websites treated equally
**Recommendation**:
- Add priority scoring based on:
  - Personal websites (higher priority)
  - Named emails found (higher priority)
  - Small businesses (medium priority)
  - Corporate sites (lower priority)
- Store priority score in database
- Sort by priority in UI

### 3. Email Extraction for Social Profiles
**Current**: Not implemented
**Recommendation**:
- Extract emails from:
  - LinkedIn → contact info
  - Instagram → bio
  - TikTok → bio
  - Facebook → profile/page
- Store with confidence metadata
- Don't fabricate emails

## 🎯 ENFORCEMENT STATUS

### ✅ Enforced
- Canonical Liquid Canvas description in all prompts
- Social discovery qualification rules (followers, engagement rate)
- Source type separation (website vs social)
- Discovery → Accept → Leads flow for social
- Gemini chat persistence
- Draft editor authority

### ⚠️ Needs Attention
- Email confidence distinction (personal vs generic)
- Website discovery priority weighting
- Social profile email extraction

## 📝 NOTES

All prompts now correctly position Liquid Canvas as:
- **Mobile-to-TV streaming art platform**
- **NOT** an art services company, creative agency, design studio, or art consultancy

All drafts will emphasize:
- TV-based art streaming
- Playlists
- Connected TVs
- Personal + shared display
- NFTs (where relevant)

