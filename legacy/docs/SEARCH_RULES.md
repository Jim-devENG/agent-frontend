# Search Rules and Discovery Configuration

This document outlines the search rules, queries, and discovery configuration for the Autonomous Art Outreach Scraper.

## Search Sources

The system uses multiple sources to discover websites:

1. **DuckDuckGo Search** (Primary - No API key required)
   - Uses `duckduckgo-search` library
   - Falls back to HTML scraping if library unavailable
   - Searches 10 random queries per run (from 30+ total queries)
   - Rate limit: 1 second delay between queries

2. **Seed List** (`seed_websites.txt`)
   - Manual list of URLs (one per line)
   - Loaded from project root directory
   - All URLs from seed list are added to discovered websites

3. **Google Search** (Optional - Requires API key)
   - Currently not implemented
   - Requires: `GOOGLE_SEARCH_API_KEY` and `GOOGLE_SEARCH_ENGINE_ID`
   - Would use Google Custom Search API

4. **Bing Search** (Optional - Requires API key)
   - Currently not implemented
   - Requires: `BING_SEARCH_API_KEY`
   - Would use Bing Search API

## Search Queries by Category

The system searches for 7 target categories with specific queries:

### 1. Art Gallery (`art_gallery`)
- "art gallery website"
- "contemporary art gallery"
- "modern art gallery"
- "online art gallery"
- "art exhibition space"

### 2. Interior Decor (`interior_decor`)
- "interior design blog"
- "interior decorator website"
- "home design blog"
- "interior design portfolio"
- "home decor blog"

### 3. Home Tech (`home_tech`)
- "home tech blog"
- "smart home blog"
- "home automation blog"
- "tech for home"
- "home technology review"

### 4. Mom Blogs (`mom_blogs`)
- "mom blog"
- "parenting blog"
- "family lifestyle blog"
- "mommy blog"
- "family blog"

### 5. NFT Tech (`nft_tech`)
- "NFT art platform"
- "NFT marketplace"
- "digital art platform"
- "crypto art gallery"
- "blockchain art"

### 6. Editorial Media (`editorial_media`)
- "editorial media house"
- "lifestyle magazine"
- "design magazine"
- "art publication"
- "creative magazine"

### 7. Holiday/Family (`holiday_family`)
- "holiday family website"
- "family travel blog"
- "holiday planning blog"
- "family activities blog"
- "seasonal decor blog"

**Total: 35 search queries** (5 queries × 7 categories)

## Search Execution Rules

1. **Query Selection**: 
   - All 35 queries are shuffled randomly
   - Only 10 queries are executed per discovery run
   - This prevents overwhelming the system and avoids rate limits

2. **Results per Query**:
   - Each query returns up to 5 results
   - Maximum 50 unique URLs per discovery run (10 queries × 5 results)

3. **Rate Limiting**:
   - 1 second delay between queries
   - Prevents being blocked by search engines

4. **Deduplication**:
   - URLs are deduplicated across all sources
   - Same URL from different queries/sources is only stored once

## Discovery Schedule

The discovery job runs based on configuration:

- **Default**: Weekly (Monday at 3 AM)
- **Configurable**: Can be set to run at custom intervals (e.g., every 10 seconds, 1 minute, etc.)
- **Setting**: Controlled by `search_interval_seconds` in `AppSettings` table
- **Manual Trigger**: Can be triggered manually via API endpoint `/api/v1/discovery/search-now`

## Quality Filtering

When websites are discovered, they are:

1. **Saved to `discovered_websites` table** immediately
   - URL, domain, title, snippet
   - Source (duckduckgo, seed_list, etc.)
   - Search query that found it
   - Predicted category

2. **Scraped** (if not already scraped)
   - Quality filters are **disabled** during discovery to ensure all discovered websites are scraped
   - Quality metrics are still calculated and stored
   - `meets_quality_threshold` flag indicates if quality requirements are met

3. **Contact Extraction** (after scraping)
   - Contacts are extracted immediately after scraping
   - Extracts: emails, phone numbers, social links, contact forms
   - Crawls contact pages: `/contact`, `/about`, `/support`, `/info`, `/team`

## Quality Thresholds

Quality filtering thresholds (can be adjusted in `utils/config.py`):

- `MIN_QUALITY_SCORE`: 20 (0-100)
- `MIN_DOMAIN_AUTHORITY`: 10 (0-100)
- `MIN_TRAFFIC_TIER`: 1 (1-5)
- `REQUIRE_SSL`: False
- `REQUIRE_VALID_DNS`: True

**Note**: During discovery, quality filtering is disabled to ensure all discovered websites are saved. Quality metrics are still calculated for reference.

## Automation Jobs Schedule

1. **Fetch New Art Websites** (Discovery)
   - Frequency: Configurable (default: weekly)
   - Runs: Based on `search_interval_seconds` setting

2. **Scrape Pending Websites**
   - Frequency: Every 6 hours
   - Processes: Websites with status "pending"

3. **Extract and Store Contacts**
   - Frequency: Every 4 hours
   - Processes: Scraped websites without contacts

4. **Generate AI Emails**
   - Frequency: Every 2 hours
   - Processes: Contacts without outreach emails

5. **Send Emails If Not Sent**
   - Frequency: Every hour
   - Processes: Generated emails with status "draft"

## Manual Operations

You can manually trigger:

1. **Discovery**: `POST /api/v1/discovery/search-now`
2. **Scrape URL**: `POST /api/v1/scrape-url?url=<URL>`
3. **Extract Contacts**: `POST /api/v1/websites/{id}/extract-contacts`

## Configuration Files

- **Search Queries**: `jobs/website_discovery.py` (lines 167-210)
- **Quality Thresholds**: `utils/config.py`
- **Schedule**: `jobs/scheduler.py`
- **Seed List**: `seed_websites.txt` (project root)

