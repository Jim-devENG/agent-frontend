# Verification Status & Progress Guide

## How to Know if Verification is Running

When you click **"Start Verification"**, here's what happens and how to track it:

### 1. **Immediate Feedback**
- ✅ Success alert shows:
  - Number of emails being verified
  - Job ID for tracking
  - What happens during verification

### 2. **Verification Card Status**
The Verification card shows:
- **Button Text Changes:**
  - `"Starting..."` → When job is pending
  - `"Verifying..."` → When job is running
  - `"View Verified"` → When verification is complete

- **Job Status Badge:**
  - 🟡 **Yellow badge "running"** → Verification in progress
  - 🟢 **Green badge "completed"** → Verification finished
  - 🔴 **Red badge "failed"** → Verification error (check error message)

### 3. **Real-time Status Updates**
- Status refreshes every 10 seconds automatically
- Card shows: `"🔄 Verification in progress..."` when running
- Card shows: `"✅ Verification completed!"` when done
- Verified count updates automatically when job completes

### 4. **Jobs Tab**
- Go to **Jobs tab** to see detailed verification job status
- Shows:
  - Job ID
  - Status (pending/running/completed/failed)
  - Created time
  - Error messages (if failed)
  - Job parameters (prospect IDs being verified)

---

## What Verification Does

### Backend Process:
1. **Finds scraped emails** that need verification:
   - `scrape_status IN ('SCRAPED', 'ENRICHED')`
   - `contact_email IS NOT NULL`
   - `verification_status != 'verified'`

2. **Verifies each email** using Snov.io API:
   - Checks if email exists and is valid
   - Calculates confidence score
   - Updates `verification_status` to `'verified'` or `'unverified'`

3. **Updates prospect records:**
   - Sets `verification_status = 'verified'` (or `'unverified'`)
   - Sets `verification_confidence` score
   - Stores Snov.io response in `verification_payload`

### Result:
- ✅ **Verified emails** → Ready for drafting (`drafting_ready_count` increases)
- ❌ **Unverified emails** → Marked as unverified (won't be drafted)

---

## Verification → Leads Flow

**Important:** Verification doesn't automatically create "leads". Here's the actual flow:

1. **Scraping** → Extracts emails from websites
   - Sets `scrape_status = 'SCRAPED'` or `'ENRICHED'`
   - Sets `contact_email` (if found)

2. **Verification** → Verifies scraped emails
   - Sets `verification_status = 'verified'` (if valid)
   - Makes prospects ready for **drafting**

3. **Drafting** → Generates email drafts
   - Requires: `verification_status = 'verified'` AND `contact_email IS NOT NULL`
   - Creates draft subject and body

4. **Sending** → Sends emails via Gmail
   - Requires: verified + drafted + not sent

**Note:** "Leads" is a separate stage (`stage = 'LEAD'`) that requires manual promotion. Verification makes prospects ready for drafting, which is the next step in the pipeline.

---

## Troubleshooting

### Verification Not Starting?
- Check: Are there scraped emails? (`emails_found > 0`)
- Check: Are emails already verified? (`emails_verified` count)
- Check: Button shows "No Prospects Ready" → All emails already verified

### Verification Stuck?
- Check Jobs tab for job status
- Look for error messages in job details
- Refresh pipeline status manually

### Verified Count Not Updating?
- Wait 10 seconds for auto-refresh
- Click "Refresh" button manually
- Check Jobs tab to see if job completed

---

## Visual Indicators

| Status | Badge Color | Button Text | Description |
|--------|-------------|-------------|-------------|
| Pending | Gray | "Starting..." | Job queued, not started yet |
| Running | Yellow | "Verifying..." | Actively verifying emails |
| Completed | Green | "View Verified" | All emails verified |
| Failed | Red | "Start Verification" | Error occurred (check Jobs tab) |

---

## Expected Behavior

1. **Click "Start Verification"**
   - ✅ Alert shows job started
   - ✅ Button changes to "Verifying..."
   - ✅ Yellow badge appears
   - ✅ Status text shows "🔄 Verification in progress..."

2. **During Verification**
   - ✅ Job status badge shows "running"
   - ✅ Status text updates every 10 seconds
   - ✅ Can check Jobs tab for details

3. **After Completion**
   - ✅ Badge changes to "completed" (green)
   - ✅ Button changes to "View Verified"
   - ✅ Verified count increases
   - ✅ Status text shows "✅ Verification completed!"
   - ✅ Drafting card unlocks (if verified count > 0)

