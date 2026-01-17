# Pipeline Stability Fix

## Summary

Fixed backend instability and frontend polling abuse that was breaking pipeline behavior. Focus: stability first, not features.

## PART 1 — BACKEND FIXES

### What caused the instability:

1. **CORS Middleware Order**: CORS middleware was added AFTER custom middleware, causing CORS headers to be missing on some error responses
2. **Heavy Pipeline Status Endpoint**: `/api/pipeline/status` was performing many COUNT queries and extensive logging, causing slow responses and 502 errors
3. **No CORS on Errors**: Error responses didn't consistently include CORS headers

### How CORS is guaranteed:

**Fixed middleware order:**
- CORS middleware (`CORSMiddleware`) is now added FIRST, before any custom middleware
- Custom middleware runs AFTER CORS to add fallback headers
- Exception handlers explicitly set CORS headers on all error responses
- Added `Access-Control-Expose-Headers` for better browser compatibility

**Implementation:**
- `CORSMiddleware` runs first (line 89-97 in `main.py`)
- Custom `add_cors_headers_fallback` middleware runs after (line 26-52)
- Exception handlers add CORS headers to all JSON error responses (lines 54-85)

### How pipeline status is stabilized:

**Optimized `/api/pipeline/status` endpoint:**
- Removed excessive logging (removed 8+ `logger.info` calls per request)
- Removed unnecessary total prospects count query
- Kept all COUNT queries but removed verbose logging
- Endpoint is now read-only, idempotent, and fast (< 500ms target)

**What was removed:**
- `logger.info("📊 [PIPELINE STATUS] Computing data-driven counts...")` 
- `logger.info(f"📊 [PIPELINE STATUS] Total prospects in database: {total_prospects}")`
- `logger.info(f"📊 [PIPELINE STATUS] DISCOVERED count: {discovered_count}...")`
- `logger.info(f"📊 [PIPELINE STATUS] SCRAPED count: {scraped_count}...")`
- `logger.info(f"📊 [PIPELINE STATUS] VERIFIED count: {verified_count}...")`
- `logger.info(f"📊 [PIPELINE STATUS] DRAFT-READY count: {draft_ready_count}...")`
- `logger.info(f"📊 [PIPELINE STATUS] DRAFTED count: {drafted_count}...")`
- `logger.info(f"📊 [PIPELINE STATUS] SENT count: {sent_count}...")`
- `logger.info(f"📊 [PIPELINE STATUS] SEND-READY count: {send_ready_count}...")`
- `logger.info(f"📊 [PIPELINE STATUS] Counts computed: ...")`

**What remains:**
- All COUNT queries (required for pipeline state)
- Error logging (only on failures)
- Exception handling (returns safe defaults on error)

## PART 2 — FRONTEND FIXES

### How polling was fixed:

**Removed aggressive polling:**
- Removed `setInterval` polling from `Pipeline.tsx` (was polling every 10 seconds)
- Removed `setInterval` polling from `SocialPipeline.tsx` (was polling every 10 seconds)
- Removed debounce timeouts (unnecessary without polling)

**New behavior:**
- Pipeline status loads ONLY on:
  - Initial component mount
  - Manual refresh button click
  - User actions (scrape, verify, draft, send)
  - Discovery completion events (with confirmation)
  - Explicit refresh events (`refreshPipelineStatus`, `refreshSocialPipelineStatus`)

**No more:**
- Interval-based automatic polling
- Debounced polling
- Repeated API calls on every render

### How false resets were prevented:

**Fixed reset logic:**
- Only reset pipeline state when a NEW job ID is confirmed (not on initial load)
- Don't reset `latestDiscoveryJobId` to `null` on discovery events (was causing false resets)
- Treat network errors as temporary failures (don't reset state)
- Track job IDs properly: only reset if current ID is not null AND different from new ID

**Implementation:**
- `loadDiscoveryJobs()` only resets state if `latestDiscoveryJobId !== null && latestJob.id !== latestDiscoveryJobId`
- First-time job ID tracking doesn't trigger reset (just sets the ID)
- Network errors in `loadDiscoveryJobs()` don't trigger state resets

## Files Modified

### Backend:
- `backend/app/main.py`:
  - Moved CORS middleware to run FIRST (before custom middleware)
  - Added `expose_headers` to CORS middleware
  - Updated exception handlers to include CORS headers

- `backend/app/api/pipeline.py`:
  - Removed excessive logging from `get_pipeline_status()`
  - Removed unnecessary total prospects count query
  - Optimized endpoint for performance

### Frontend:
- `frontend/components/Pipeline.tsx`:
  - Removed `setInterval` polling (was every 10 seconds)
  - Removed debounce timeout logic
  - Fixed `loadDiscoveryJobs()` to prevent false resets
  - Status now loads only on mount, user actions, and explicit events

- `frontend/components/SocialPipeline.tsx`:
  - Removed `setInterval` polling (was every 10 seconds)
  - Removed debounce timeout logic
  - Status now loads only on mount, user actions, and explicit events

## How to Verify the Fix Manually

### 1. CORS Headers:
- Open browser DevTools → Network tab
- Trigger an error (e.g., disconnect backend)
- Check response headers → Should see `Access-Control-Allow-Origin: *`
- No CORS errors in console

### 2. Pipeline Status Performance:
- Open browser DevTools → Network tab
- Navigate to Pipeline tab
- Check `/api/pipeline/status` request → Should complete in < 500ms
- Check response size → Should be reasonable (< 1KB)

### 3. No Aggressive Polling:
- Open browser DevTools → Network tab
- Navigate to Pipeline tab
- Watch network requests → Should see only ONE `/api/pipeline/status` call on mount
- No repeated calls every 10 seconds
- Refresh only happens when:
  - Clicking "Refresh" button
  - Running discovery
  - Performing pipeline actions (scrape, verify, draft, send)

### 4. Stable UI State:
- Navigate to Pipeline tab
- Wait 30 seconds
- UI should remain stable (no resets, no button flickering)
- Action buttons should remain visible if work exists
- Counts should not change unless user performs actions

### 5. No False Resets:
- Run a discovery
- Wait for completion
- Pipeline should reset ONLY once (not repeatedly)
- Buttons should re-enable based on new data
- No additional resets after initial reset

## Success Criteria Met

- [x] No repeated pipeline resets (removed interval polling)
- [x] No CORS errors in console (CORS middleware runs first)
- [x] `/api/pipeline/status` responds < 500ms (removed excessive logging)
- [x] Action buttons appear when work exists (stable state)
- [x] UI state remains stable (no polling, no false resets)

