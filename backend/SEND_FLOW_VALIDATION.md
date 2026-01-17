# Send Flow Validation Checklist

## Overview

This document validates that the unified send flow works correctly for both pipeline and manual sends.

## Architecture

### Unified Send Function

**Location**: `backend/app/services/email_sender.py`

**Function**: `send_prospect_email(prospect, db, gmail_client=None)`

**Used By**:
1. Pipeline send: `backend/app/tasks/send.py` → `process_send_job()`
2. Manual send: `backend/app/api/prospects.py` → `POST /api/prospects/{id}/send`

### Endpoints

1. **Pipeline Send**: `POST /api/pipeline/send`
   - Batch sends multiple prospects
   - Creates background job
   - Uses shared `send_prospect_email()` service

2. **Manual Send**: `POST /api/prospects/{id}/send`
   - Sends single prospect
   - Synchronous (waits for result)
   - Uses shared `send_prospect_email()` service

## Validation Checklist

### ✅ PART 1: Gmail Authentication

- [x] Gmail client initializes correctly
- [x] Refresh token logic works
- [x] Access token auto-refreshes on 401
- [x] Clear error messages for auth failures
- [x] Health check endpoint (`/api/health/gmail`) works
- [x] Defensive logging for token operations

**Test**:
```bash
# Check Gmail config
curl https://your-api.com/api/health/gmail

# Should return:
{
  "status": "configured",
  "token_refresh_test": "success",
  "ready_to_send": true
}
```

### ✅ PART 2: Unified Send Function

- [x] Single `send_prospect_email()` function exists
- [x] Used by both pipeline and manual send
- [x] Validates prospect is sendable
- [x] Creates email log
- [x] Updates prospect status correctly
- [x] Handles Gmail API errors gracefully

**Test**:
1. Create a draft via compose endpoint
2. Send via manual send endpoint
3. Verify email log created
4. Verify prospect status updated
5. Send via pipeline send endpoint
6. Verify same behavior

### ✅ PART 3: Frontend Send Button

- [x] "Send Now" button exists in draft modal
- [x] Button disabled when no draft exists
- [x] Button disabled when already sent
- [x] Button disabled when email not verified
- [x] Error messages displayed inline (not alerts)
- [x] Success messages displayed inline
- [x] Pipeline status refreshes after send

**Test**:
1. Open draft modal
2. Verify "Send Now" button appears only when draft exists
3. Click "Send Now"
4. Verify success message appears
5. Verify modal closes
6. Verify pipeline status updates

### ✅ PART 4: Error Handling

**Backend**:
- [x] Validation errors return 400
- [x] Already sent returns 409
- [x] Gmail errors return 500 with details
- [x] Clear error messages for each case

**Frontend**:
- [x] 400 errors show draft/verification issues
- [x] 409 errors show "already sent" message
- [x] 500 errors show Gmail configuration issues
- [x] Errors displayed inline (not alerts)

**Test**:
1. Try sending without draft → 400 error
2. Try sending already sent email → 409 error
3. Disable Gmail config → 500 error
4. Verify error messages are clear

### ✅ PART 5: Database Discipline

- [x] No new tables added
- [x] Uses existing `email_logs` table
- [x] Updates existing prospect fields correctly
- [x] No schema guessing
- [x] All updates committed atomically

**Test**:
1. Send email
2. Check `email_logs` table has entry
3. Check `prospects` table has `send_status = 'sent'`
4. Check `prospects` table has `last_sent` timestamp
5. Verify no orphaned records

### ✅ PART 6: Pipeline Integration

- [x] Manual sends reflected in pipeline counts
- [x] Pipeline send card unlocks when drafts exist
- [x] Pipeline send uses same send function
- [x] Job status updates correctly

**Test**:
1. Create draft
2. Verify pipeline send card unlocks
3. Send via pipeline
4. Verify counts update
5. Send manually
6. Verify counts still accurate

## End-to-End Test Scenarios

### Scenario 1: Manual Send from Draft Modal

1. **Setup**: Prospect with verified email and draft
2. **Action**: Click "Compose Email" → "Send Now"
3. **Expected**:
   - Email sent via Gmail API
   - Success message appears
   - Modal closes
   - Prospect status: `send_status = 'sent'`
   - Email log created
   - Pipeline counts update

### Scenario 2: Pipeline Batch Send

1. **Setup**: Multiple prospects with drafts
2. **Action**: Pipeline → Send card → "Start Sending"
3. **Expected**:
   - Job created
   - All eligible prospects sent
   - Job status: "completed"
   - All prospects updated
   - All email logs created
   - Pipeline counts accurate

### Scenario 3: Gmail Auth Failure

1. **Setup**: Invalid refresh token
2. **Action**: Try to send email
3. **Expected**:
   - Clear error message about Gmail config
   - Suggestion to check `/api/health/gmail`
   - No silent failures
   - Error logged with details

### Scenario 4: Validation Failures

1. **Setup**: Prospect without draft
2. **Action**: Try to send
3. **Expected**:
   - 400 error
   - Clear message: "Draft must be created first"
   - No email sent
   - No database changes

### Scenario 5: Duplicate Send Prevention

1. **Setup**: Prospect already sent
2. **Action**: Try to send again
3. **Expected**:
   - 409 error
   - Clear message: "Email already sent"
   - No duplicate sends
   - No database changes

## Success Criteria

✅ **All scenarios pass**
✅ **No duplicate sends**
✅ **No silent failures**
✅ **Clear error messages**
✅ **Database integrity maintained**
✅ **Pipeline counts accurate**
✅ **Gmail token refresh works automatically**

## Known Limitations

1. **Access Token Storage**: Access tokens are in-memory only. If server restarts, token is lost but auto-refreshes on next send.

2. **Rate Limiting**: Gmail API has rate limits. System includes 2-second delay between sends in batch mode.

3. **Token Expiry**: Refresh tokens can expire if:
   - User revokes access
   - Token not used for 6 months
   - OAuth app settings change

## Monitoring

**Key Metrics to Monitor**:
- Gmail API success rate
- Token refresh success rate
- Send job completion rate
- Error rate by type (400, 409, 500)

**Health Checks**:
- `/api/health/gmail` - Gmail configuration status
- `/api/health/schema` - Database schema validation
- Job status endpoints - Send job health

## Troubleshooting

### Issue: "Failed to obtain Gmail access token"

**Check**:
1. `/api/health/gmail` endpoint
2. Environment variables set correctly
3. Refresh token valid
4. OAuth consent screen configured

**Fix**:
1. Generate new refresh token
2. Update environment variables
3. Re-test `/api/health/gmail`

### Issue: "Email already sent" but status shows pending

**Check**:
1. Database transaction committed
2. Prospect `send_status` field
3. Email log exists

**Fix**:
1. Check database directly
2. Verify send function commits correctly
3. Check for transaction rollbacks

### Issue: Pipeline counts don't update after manual send

**Check**:
1. Frontend refresh logic
2. Pipeline status endpoint
3. Database counts

**Fix**:
1. Trigger `refreshPipelineStatus` event
2. Verify status endpoint queries correctly
3. Check frontend refresh handlers

