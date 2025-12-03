# How to Enrich Existing Prospects (Scrape Emails for Ones We Already Have)

## Problem
When discovery jobs run, many domains are skipped because they already exist in the database. These existing prospects might not have emails yet, and you want to enrich them.

## Solution
The enrichment job system has been updated to **prioritize prospects without emails**. Here's how to use it:

## Method 1: Enrich All Prospects Without Emails (Recommended)

### Via API Call:
```bash
POST /api/prospects/enrich?only_missing_emails=true&max_prospects=100
```

### Via Frontend (if you have a UI button):
The `createEnrichmentJob()` function now supports the `onlyMissingEmails` parameter:

```typescript
import { createEnrichmentJob } from '@/lib/api'

// Enrich up to 100 prospects that don't have emails
await createEnrichmentJob(undefined, 100, true)
```

## Method 2: Enrich Specific Prospects

If you know specific prospect IDs that need enrichment:

```bash
POST /api/prospects/enrich?prospect_ids=uuid1,uuid2,uuid3
```

## How It Works

1. **Prioritization**: The enrichment job automatically prioritizes prospects without emails
   - Prospects with `contact_email IS NULL` are processed first
   - Then prospects with existing emails (to improve them if better matches are found)

2. **Filtering**: If `only_missing_emails=true`:
   - Only prospects without emails are processed
   - This is perfect for enriching the ones that were skipped during discovery

3. **Rate Limiting**: 
   - 1 request per second to respect Hunter.io API limits
   - With your new Pro account (50,000/month), you can enrich many prospects

## What Happens

1. **Job Created**: An enrichment job is created and starts processing
2. **Hunter.io Lookup**: Each prospect's domain is searched via Hunter.io
3. **Email Found**: If an email is found, it's saved to `prospect.contact_email`
4. **Local Scraping Fallback**: If Hunter.io fails (rate limit, etc.), local HTML scraping is attempted
5. **Retry Marking**: If all methods fail, the prospect is marked for retry (not skipped)

## Example: Enriching 100 Existing Prospects Without Emails

```bash
curl -X POST "https://your-backend.com/api/prospects/enrich?only_missing_emails=true&max_prospects=100" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

This will:
- Find up to 100 prospects that don't have emails
- Enrich them using Hunter.io (with your new Pro account key)
- Save any emails found
- Process at 1 per second (takes ~100 seconds for 100 prospects)

## Monitoring Progress

Check the job status in your Jobs tab:
- **Status**: "running" → "completed"
- **Result**: Shows how many were enriched, failed, or had no email found

## Benefits

✅ **No Duplicates**: Enriches existing prospects instead of creating new ones  
✅ **Prioritized**: Prospects without emails are processed first  
✅ **Efficient**: Uses your Pro account's higher rate limits  
✅ **Fallback**: Local scraping if Hunter.io fails  
✅ **Safe**: Won't overwrite good emails with worse ones (compares confidence scores)

## Next Steps

1. **Run an enrichment job** with `only_missing_emails=true`
2. **Check the Jobs tab** to see progress
3. **Check your Prospects/Leads tables** - you should see emails appearing for previously empty prospects

The enrichment will automatically use your new Hunter.io Pro account key that you added to Render!

