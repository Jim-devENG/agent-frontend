# Why Are 0 Prospects Being Saved?

## Common Reasons

### 1. **All Domains Already Exist in Database** (Most Common)
The discovery job checks if a domain already exists before saving. If you've run discovery jobs before, many domains might already be in your database.

**How to check:**
- Look at the job results: Check "Skipped (Existing)" count
- If this number is high, it means domains were found but already exist

**Solution:**
- This is normal behavior - the system prevents duplicates
- Try different search queries, locations, or categories to find NEW domains
- Or wait for new websites to appear in search results

### 2. **All Domains Are Duplicates Within the Same Job**
If the same domain appears multiple times in search results, only the first one is saved.

**How to check:**
- Look at job results: Check "Skipped (Duplicates)" count
- This shows how many duplicate domains were found in the same job

**Solution:**
- This is also normal - prevents saving the same domain multiple times
- Try more diverse search queries to get different domains

### 3. **Enrichment Failing (But Should Still Save)**
Even if Hunter.io fails to find emails, prospects should still be saved (without email, marked for retry).

**How to check:**
- Look at backend logs for enrichment errors
- Check if you see messages like "Saving {domain} without email (will retry enrichment later)"
- If you see "Skipping {domain} - no email and no retry needed", that's a bug

**Solution:**
- The code should save prospects even without email
- If you see skipping messages, there might be a bug

### 4. **Database Commit Failing**
If the database commit fails, prospects won't be saved even if they're added to the session.

**How to check:**
- Look for error messages in logs like "Failed to commit prospects"
- Check database connection issues

**Solution:**
- Check database connectivity
- Check database permissions
- Look for transaction errors in logs

## How to Diagnose Your Specific Issue

### Step 1: Check Job Results
Look at your discovery job results and check these numbers:
- **Results Found**: How many domains were discovered
- **Prospects Saved**: How many were actually saved (should be > 0)
- **Skipped (Duplicates)**: How many were duplicates in the same job
- **Skipped (Existing)**: How many already exist in database

### Step 2: Check Backend Logs
Look for these log messages:

**Good signs (prospects being saved):**
```
💾 [DISCOVERY] Saving prospect {domain} with email {email}
💾 [DISCOVERY] Saving prospect {domain} without email (retry pending)
💾 Saved new prospect: {domain} - {title} (email: {email})
💾 Committed {count} new prospects to database
```

**Bad signs (prospects being skipped):**
```
⏭️ Skipping existing domain in database: {domain}
⏭️ Skipping duplicate domain in this job: {domain}
⏭️ [DISCOVERY] Skipping {domain} - no email and no retry needed  ← BUG if you see this
```

### Step 3: Check Your Database
Query your database to see if prospects exist:
```sql
SELECT COUNT(*) FROM prospects WHERE discovery_query_id = '{your_job_id}';
SELECT domain, contact_email, contact_method FROM prospects ORDER BY created_at DESC LIMIT 10;
```

## Most Likely Cause

**If you see:**
- Results Found: 1018
- Prospects Saved: 0
- Skipped (Existing): 340
- Skipped (Duplicates): 497

**This means:**
- 1018 domains were discovered
- 340 already exist in your database (normal - prevents duplicates)
- 497 were duplicates within the same job (normal - prevents saving same domain twice)
- 181 were processed but 0 were saved (this is the problem)

**The 181 remaining domains should have been saved**, even without emails. If they weren't, there might be:
1. A bug in the save logic
2. Database commit failing
3. All 181 failed enrichment AND the retry logic isn't working

## Quick Fix to Test

Try running a discovery job with:
- **Different locations** (e.g., try "australia", "japan" instead of "usa", "uk")
- **Different categories** (e.g., try "tech_innovation" instead of "home_decor")
- **Different keywords** (e.g., try "art gallery" instead of "home decor blog")

This will find NEW domains that don't already exist in your database.

## If Still 0 Saved After Trying New Queries

If you try completely different search terms and still get 0 saved, there's likely a bug. Check:
1. Backend logs for any errors during the save process
2. Database connection and permissions
3. Whether the commit is actually happening

The code should save prospects even without emails - if it's not, we need to fix the bug.

