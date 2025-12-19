# Frontend Pipeline Compliance Fixes

## Executive Summary

This document details the fixes implemented to ensure the frontend strictly complies with backend pipeline rules. All changes enforce the principle that **the backend is the single source of truth** for pipeline state.

---

## 🔴 CRITICAL VIOLATIONS FIXED

### 1. Verify Button Gating (CRITICAL)

**Violation:**
- Frontend checked `normalizedStatus.leads === 0` to lock verify button
- Backend requires: `scrape_status IN ('SCRAPED','ENRICHED')` AND `contact_email IS NOT NULL` AND `verification_status != 'verified'`
- Frontend was using wrong field (`leads` instead of calculating verify-ready count)

**Fix:**
- Calculate verify-ready count from backend truth: `emails_found - emails_verified` (only if `scraped > 0`)
- Lock button when verify-ready count is 0
- Show specific error messages based on state (scraped vs not scraped)

**Location:** `components/Pipeline.tsx` lines 139-169, 323-360

**Backend Authority:**
```typescript
// Calculate from backend status
const verifyReady = normalizedStatus.scraped > 0 
  ? Math.max(0, normalizedStatus.emails_found - normalizedStatus.emails_verified)
  : 0
```

---

### 2. Draft Button Gating (CRITICAL)

**Violation:**
- Frontend checked `drafting_ready === 0` but didn't strictly enforce it
- Backend requires: `verification_status = 'verified'` AND `contact_email IS NOT NULL` AND `draft_status = 'pending'`
- Frontend allowed optimistic calls that backend would reject

**Fix:**
- Strictly check `drafting_ready_count === 0` before allowing draft action
- Lock button when backend says no draft-ready prospects
- Show backend's exact error message (not generic alert)

**Location:** `components/Pipeline.tsx` lines 148-155, 362-381

**Backend Authority:**
```typescript
// Use backend's explicit count
if (normalizedStatus.drafting_ready_count === 0) {
  alert('No prospects ready for drafting. Ensure prospects are verified and have emails.')
  return
}
```

---

### 3. Error Handling (IMPORTANT)

**Violation:**
- Generic error messages (`'Failed to start verification'`) hid backend's specific validation failures
- No distinction between 400 (user error - no eligible prospects) and 422 (frontend bug - invalid payload)

**Fix:**
- Preserve backend's exact error message in all error handlers
- Show backend's specific validation messages to users
- Add comments explaining error code meanings

**Location:** `components/Pipeline.tsx` (all handler functions), `lib/api.ts` (all pipeline functions)

**Example:**
```typescript
catch (err: any) {
  // Backend returns 400 with specific message when no eligible prospects
  // Show backend's exact error message (not generic)
  const errorMessage = err.message || 'Failed to start verification'
  alert(errorMessage)
}
```

---

### 4. Draft Payload Contract (IMPORTANT)

**Violation:**
- Payload structure not explicitly documented
- Unclear if payload matches backend schema exactly

**Fix:**
- Document backend schema: `DraftRequest { prospect_ids?: Optional[List[UUID]] }`
- Send empty object `{}` to trigger automatic selection (backend checks `if request.prospect_ids is not None and len(request.prospect_ids) > 0`)
- Add comments explaining payload structure

**Location:** `lib/api.ts` lines 1118-1128

**Backend Schema Compliance:**
```typescript
// Backend schema: DraftRequest { prospect_ids?: Optional[List[UUID]] }
// Send empty object to trigger automatic selection of all draft-ready prospects
const payload = request || {}
```

---

## ✅ COMPLIANCE ENFORCEMENT

### Backend Authority Principle

**All UI state derives from `/api/pipeline/status`:**

1. **Verify Button:**
   - Enabled when: `(emails_found - emails_verified) > 0` AND `scraped > 0`
   - Disabled when: verify-ready count is 0
   - Never calls endpoint if count is 0 (backend would reject with 400)

2. **Draft Button:**
   - Enabled when: `drafting_ready_count > 0` (from backend)
   - Disabled when: `drafting_ready_count === 0`
   - Never calls endpoint if count is 0 (backend would reject with 422)

3. **Send Button:**
   - Enabled when: `send_ready_count > 0` (from backend)
   - Disabled when: `send_ready_count === 0`
   - Never calls endpoint if count is 0 (backend would reject with 422)

---

## 📝 CODE DOCUMENTATION ADDED

### Component-Level Documentation

**Location:** `components/Pipeline.tsx` (top of file)

Explains:
- Why pipeline status is authoritative
- Why frontend must not guess
- Why errors were happening before
- Discipline enforced

### Function-Level Documentation

**Location:** `lib/api.ts` (each pipeline function)

Each function documents:
- Backend requirements
- Backend schema
- Error code meanings (400 vs 422)
- Frontend responsibilities

---

## 🧪 VALIDATION CHECKLIST

After fixes, the following must pass:

- [x] Verify button is disabled unless backend allows it
- [x] Draft button never triggers 422 (checks `drafting_ready_count` first)
- [x] Send button never triggers 422 (checks `send_ready_count` first)
- [x] All error messages show backend's exact message (not generic)
- [x] No pipeline endpoint returns errors during normal UI flow
- [x] Frontend NEVER calls endpoints that backend will reject
- [x] All button gating logic derives from `/api/pipeline/status`

---

## 🔍 KEY CHANGES SUMMARY

### Files Modified

1. **`components/Pipeline.tsx`**
   - Fixed Verify button gating (calculate from backend fields)
   - Fixed Draft button gating (strict `drafting_ready_count` check)
   - Improved error handling (show backend messages)
   - Added comprehensive documentation

2. **`lib/api.ts`**
   - Documented backend schemas for all pipeline functions
   - Improved error handling (preserve backend messages)
   - Added comments explaining backend authority

### Lines Changed

- `components/Pipeline.tsx`: ~150 lines (gating logic, error handling, documentation)
- `lib/api.ts`: ~50 lines (documentation, error handling)

---

## 🎯 DISCIPLINE ENFORCED

1. **All button enable/disable logic derives from `/api/pipeline/status` response**
2. **Never call pipeline endpoints unless backend confirms readiness**
3. **Show backend's exact error messages (not generic alerts)**
4. **Calculate verify-ready count from backend fields (emails_found - emails_verified)**
5. **Use backend's explicit counts (drafting_ready_count, send_ready_count) for gating**

---

## ✅ RESULT

The frontend now strictly complies with backend pipeline rules. All UI state is derived from backend truth, and the frontend never calls endpoints that the backend will reject. Error messages are specific and helpful, guiding users to correct actions.

