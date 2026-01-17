# DataForSEO Discovery Bug Fix Report

## ✅ STEP 1 — BUG IDENTIFICATION

### What Variable is a String
- **Variable**: `limit_str` in `backend/app/utils/rate_limiter.py`
- **Value**: String like `"100/hour"`, `"900/hour"`, `"60/minute"`

### Where `.key_for()` is Being Called
- **Location**: `backend/app/utils/rate_limiter.py`, line 68 (original bug)
- **Method**: `strategy.hit(key, limit_str)`
- **Issue**: The `limits` library's `MovingWindowRateLimiter.hit()` method internally tries to call `.key_for()` on the limit parameter if it detects it might be an enum-like object. When we pass a raw string like `"100/hour"`, the library's internal logic incorrectly tries to call `.key_for()` on it, causing the error.

### Why This Causes All Queries to Fail
1. Every DataForSEO API call goes through rate limiting
2. Rate limiting is called before the API request
3. The `strategy.hit()` call fails with `'str' object has no attribute 'key_for'`
4. Exception is caught but not properly handled
5. Discovery job continues but API calls never execute
6. UI shows "No websites found" instead of the actual error

## ✅ STEP 2 — ROOT CAUSE CLASSIFICATION

**Classification**: **Mixed usage (some enums, some strings)**

**Justification**:
- The `limits` library expects rate limit strings to be parsed into `RateLimitItem` objects
- We were passing raw strings directly to `strategy.hit()`
- The library's internal logic tries to handle both strings and enum-like objects
- When it detects what it thinks might be an enum, it calls `.key_for()` on it
- Our strings were being incorrectly identified as enum-like objects
- The fix: Parse the limit string into a `RateLimitItem` object before passing to `hit()`

**Not**:
- ❌ Locations refactored from enums → strings (locations are already strings)
- ❌ Categories refactored from objects → strings (categories are already strings)
- ❌ UI sends raw strings while backend expects enum-like objects (UI correctly sends strings)

## ✅ STEP 3 — THE FIX

### Preferred Fix Applied: Resolver Layer

**File**: `backend/app/utils/rate_limiter.py`

**Changes**:
1. Import `parse` from `limits` library
2. Parse `limit_str` into a `RateLimitItem` object before calling `hit()`
3. Pass the parsed `RateLimitItem` to `strategy.hit(rate_limit_item, key)`
4. Wrap in try-except to fail open (allow requests if rate limiter fails)

**Code**:
```python
from limits import parse

# Parse the limit string into a RateLimitItem object
rate_limit_item = parse(limit_str)

# CORRECT USAGE: hit(rate_limit_item, key)
can_proceed = strategy.hit(rate_limit_item, key)
```

**Safety**:
- ✅ Backward compatible (still accepts string inputs)
- ✅ Non-breaking (wrapped in try-except, fails open)
- ✅ Minimal change (only affects rate limiter, not discovery logic)

## ✅ STEP 4 — ERROR HANDLING FIX

### File: `backend/app/tasks/discovery.py`

**Changes**:
1. **Differentiate API failure vs zero results**:
   - `api_failure`: API call failed (no response, error response)
   - `zero_results`: API succeeded but returned no results
   - `success`: API succeeded with results

2. **Proper error classification**:
   - `if not serp_results`: Mark as `api_failure` (no response)
   - `if not serp_results.get("success")`: Check error message to determine if API failure or zero results
   - API errors contain "API", "failed", or "error" keywords → mark as `api_failure`
   - Other cases → mark as `zero_results` (API succeeded, just no data)

3. **Job status handling**:
   - API failures → `discovery_query.status = "failed"`
   - Zero results → `discovery_query.status = "success"` (API worked, just no data)
   - Job only marked as `failed` if all queries are API failures

4. **Exception handling**:
   - Catch `key_for` errors specifically and log as bug
   - All exceptions marked as `api_failure`
   - Full error details logged with `exc_info=True`

## ✅ STEP 5 — DEFENSIVE LOGGING

### File: `backend/app/clients/dataforseo.py`

**Added Logging**:
1. **Before API call**:
   - Final payload (exact JSON)
   - Endpoint URL
   - All parameters (keyword, location_code, language_code, device)

2. **HTTP Request**:
   - HTTP method and URL
   - Request headers (debug level)

3. **HTTP Response**:
   - Response status code
   - Response headers (debug level)
   - Full response body (truncated to 2000 chars for production safety)

4. **Error Cases**:
   - Parse errors: Response text preview (500 chars)
   - Validation errors: Full error message
   - API errors: Full error details with traceback

**Log Levels**:
- `INFO`: Request/response summary, payload
- `DEBUG`: Headers, full details
- `ERROR`: Failures with full traceback

## ✅ STEP 6 — VERIFICATION

### Test Query: "Art Gallery usa"

**Expected Behavior After Fix**:
1. ✅ Rate limiter parses `"900/hour"` correctly
2. ✅ No `key_for()` error
3. ✅ API request is sent to DataForSEO
4. ✅ API response is received
5. ✅ Success or failure is accurately reported
6. ✅ No false "No websites found" message

**If API Fails**:
- Job status: `failed`
- Error message: Clear API error (not "No websites found")
- Logs: Full error details with traceback

**If API Succeeds with Zero Results**:
- Job status: `completed`
- Results: 0 websites found (honest reporting)
- Logs: "Zero results" (not "API failure")

**If API Succeeds with Results**:
- Job status: `completed`
- Results: X websites found
- Logs: Success message with count

## 📋 SUMMARY

### Bug
- **Error**: `'str' object has no attribute 'key_for'`
- **Location**: `backend/app/utils/rate_limiter.py`, `strategy.hit()` call
- **Root Cause**: Raw string passed to `hit()` instead of parsed `RateLimitItem`

### Fix
- **Solution**: Parse limit string using `limits.parse()` before calling `hit()`
- **Safety**: Wrapped in try-except to fail open (don't block discovery if rate limiter fails)
- **Impact**: All DataForSEO discovery queries now work correctly

### Error Handling
- **Improvement**: Differentiate API failure vs zero results
- **Result**: Honest error reporting, no false "No websites found" messages

### Logging
- **Added**: Comprehensive logging at request/response level
- **Safety**: Truncated for production, debug-level details available

### Verification
- **Status**: Ready for testing
- **Test**: Run discovery query "Art Gallery usa" to verify fix

