# Backend API Integration Verification Guide

## Overview
This document explains how the backend uses Hunter.io and DataForSEO APIs in real-time during scraping and discovery.

## API Integration Status

### 1. Hunter.io API Integration ✅
**Purpose**: Find email addresses for domains in real-time

**Where it's used**:
- `extractor/enhanced_email_extractor.py` - Main email extraction
- `extractor/contact_extraction_service.py` - Contact extraction service
- `scraper/scraper_service.py` - Automatic contact extraction after scraping

**Flow**:
1. When a website is scraped, `scraper_service.scrape_website()` is called
2. After scraping, `ContactExtractionService.extract_and_store_contacts()` is automatically called
3. This uses `EnhancedEmailExtractor.extract_all_emails()` which:
   - Extracts emails from HTML (main page, footer, header, forms)
   - **Calls Hunter.io API in real-time** for the domain
   - Validates all emails (filters false positives like `hero@2x.jpg`)
   - Returns emails with source tracking (`hunter_io`, `html`, `footer`, etc.)

**Configuration**:
- Set `HUNTER_IO_API_KEY` in `.env` file
- API key: `ba71410fc6c6dcec6df42333e933a40bdf2fa1cb`

**Verification**:
- Check logs for: `🔍 Using Hunter.io API for REAL-TIME email extraction`
- Check logs for: `✅ Hunter.io found X email(s)`
- Emails with `source: "hunter_io"` in database

### 2. DataForSEO API Integration ✅
**Purpose**: Search Google SERP for website discovery in real-time

**Where it's used**:
- `jobs/website_discovery.py` - Website discovery process
- `extractor/dataforseo_client.py` - DataForSEO API client

**Flow**:
1. When discovery is triggered (manual or automatic), `discover_art_websites()` is called
2. For each search query, it checks if DataForSEO is configured
3. If configured, **calls DataForSEO SERP API in real-time** instead of DuckDuckGo
4. Returns high-quality search results with domain metrics
5. Filters duplicates and saves new websites

**Configuration**:
- Set `DATAFORSEO_LOGIN` and `DATAFORSEO_PASSWORD` in `.env`
- Login: `jeremiah@liquidcanvas.art`
- Password: `b85d55cf567939e7`

**Verification**:
- Check logs for: `✅ DataForSEO API configured - Using REAL-TIME Google SERP API`
- Check logs for: `🌐 Making REAL-TIME DataForSEO API call for query: '...'`
- Check logs for: `✅ DataForSEO REAL-TIME API call successful: Found X result(s)`
- Websites with `source: "dataforseo"` in database

## Manual Scraper Flow

### Endpoint: `/api/v1/scrape-url?url=...`

**Complete Flow**:
1. **Scrape Website** (`scraper_service.scrape_website()`)
   - Fetches HTML content
   - Extracts metadata (title, description, etc.)
   - Saves to `ScrapedWebsite` table

2. **Extract Contacts** (`ContactExtractionService.extract_and_store_contacts()`)
   - Uses `EnhancedEmailExtractor` which:
     - Extracts from HTML (main page, footer, header, forms)
     - **Calls Hunter.io API** for domain email lookup
     - Uses Playwright for JavaScript-rendered emails (if available)
     - Validates all emails
   - Extracts phone numbers
   - Extracts social media links
   - Saves to `Contact` table with source tracking

3. **Return Results**
   - Website data
   - All extracted contacts with sources

**APIs Used**:
- ✅ Hunter.io (for email finding)
- ❌ DataForSEO (not used in manual scrape, only in discovery)

## Discovery Flow

### Endpoint: `/api/v1/discovery/search-now?location=...&categories=...`

**Complete Flow**:
1. **Generate Search Queries** (`utils/location_search.py`)
   - Based on selected locations and categories
   - Generates location-specific queries

2. **Search for Websites** (`WebsiteDiscovery.discover_art_websites()`)
   - For each query:
     - **Calls DataForSEO SERP API** (if configured) OR
     - Falls back to DuckDuckGo (if DataForSEO not configured)
   - Collects all unique URLs

3. **Filter Duplicates**
   - Checks existing URLs in database
   - Only saves new websites

4. **Scrape Discovered Websites**
   - For each new website:
     - Scrapes website (same as manual scrape)
     - **Automatically extracts contacts** (uses Hunter.io)

**APIs Used**:
- ✅ DataForSEO (for website discovery)
- ✅ Hunter.io (for email extraction during scraping)

## Testing APIs

### Test Script
Run the comprehensive test script:
```bash
python test_backend_apis.py
```

This will test:
1. Hunter.io API connection and functionality
2. DataForSEO API connection and functionality
3. Contact extraction with APIs
4. Website discovery with DataForSEO

### Diagnostic Endpoint
Check API status via API:
```bash
GET /api/v1/diagnostic/api-status
```

Returns:
- Hunter.io configuration and test results
- DataForSEO configuration and test results

## Common Issues

### Issue: APIs not being called
**Symptoms**:
- No logs showing API calls
- No emails from Hunter.io
- No DataForSEO results

**Solutions**:
1. Check `.env` file has correct API keys
2. Check logs for configuration warnings
3. Run diagnostic endpoint: `/api/v1/diagnostic/api-status`
4. Verify API keys are valid (test with test script)

### Issue: Same websites every time
**Symptoms**:
- Discovery finds same URLs
- No new websites added

**Solutions**:
1. Deduplication is working correctly (this is expected)
2. Try different locations/categories
3. Wait for new websites to appear in search results
4. Check if DataForSEO is returning results

### Issue: No emails extracted
**Symptoms**:
- Websites scraped but no contacts
- No emails in database

**Solutions**:
1. Check if Hunter.io is configured and working
2. Check logs for extraction errors
3. Verify website has contact information
4. Check if emails are being filtered as false positives

## Verification Checklist

- [ ] Hunter.io API key configured in `.env`
- [ ] DataForSEO credentials configured in `.env`
- [ ] Test script passes all tests
- [ ] Diagnostic endpoint shows APIs working
- [ ] Logs show API calls during scraping
- [ ] Emails with `hunter_io` source in database
- [ ] Websites with `dataforseo` source in database
- [ ] Manual scrape extracts contacts
- [ ] Discovery finds new websites

## Next Steps

1. **Run test script** to verify all APIs:
   ```bash
   python test_backend_apis.py
   ```

2. **Check diagnostic endpoint**:
   ```bash
   curl https://your-backend-url/api/v1/diagnostic/api-status
   ```

3. **Test manual scrape** with a real website:
   ```bash
   curl -X POST "https://your-backend-url/api/v1/scrape-url?url=https://example.com" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

4. **Check logs** for API usage:
   - Look for `🔍 Using Hunter.io API`
   - Look for `🌐 Making REAL-TIME DataForSEO API call`
   - Look for `✅ Hunter.io found X email(s)`
   - Look for `✅ DataForSEO REAL-TIME API call successful`

## Summary

✅ **Hunter.io**: Integrated and used during contact extraction (real-time)
✅ **DataForSEO**: Integrated and used during website discovery (real-time)
✅ **Manual Scraper**: Uses Hunter.io for email extraction
✅ **Discovery**: Uses DataForSEO for website search, Hunter.io for email extraction

All APIs are called in **real-time** during the scraping/discovery process, not cached or mocked.

