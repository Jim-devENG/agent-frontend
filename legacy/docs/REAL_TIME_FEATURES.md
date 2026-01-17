# Real-Time Activity Tracking

## Overview

The system now includes real-time activity tracking that shows what's happening in the backend as it scrapes websites, extracts contacts, and processes data.

## Features

### 1. Activity Logging

All major operations log their progress:
- **Scraping**: Start, progress steps, completion
- **Contact Extraction**: Start, progress, results
- **Email Generation**: Template selection, AI generation
- **Background Jobs**: Start, progress, completion

### 2. Real-Time Activity Feed

The dashboard includes an Activity Feed component that:
- Shows live updates every 3 seconds
- Displays activity type (Scraping, Extracting, Email, Job)
- Shows status (info, success, warning, error)
- Includes metadata (counts, steps, URLs)
- Color-coded by status

### 3. Activity API Endpoint

```
GET /api/v1/activity?limit=50&activity_type=scrape&status=success
```

**Query Parameters:**
- `limit`: Number of activities to return (default: 50, max: 200)
- `activity_type`: Filter by type (scrape, extract, email, job)
- `status`: Filter by status (info, success, warning, error)

## What You'll See

### When Scraping a Website

1. **"Starting to scrape: [URL]"** - Scraping begins
2. **"Analyzing domain quality"** - Quality check in progress
3. **"Downloading and parsing website"** - Fetching content
4. **"Successfully scraped: [Title]"** - Scraping complete

### When Extracting Contacts

1. **"Extracting contacts from: [URL]"** - Extraction starts
2. **"Extracting from main page"** - Processing main page
3. **"Crawling contact pages"** - Finding contact pages
4. **"Found X contact pages"** - Contact pages found
5. **"Extracted X emails, Y phones, Z social links"** - Results

### Activity Types

- **scrape**: Website scraping operations
- **extract**: Contact extraction operations
- **email**: Email generation and sending
- **job**: Background job executions

### Status Colors

- **info** (blue): General information
- **success** (green): Successful operations
- **warning** (yellow): Warnings
- **error** (red): Errors

## Frontend Integration

The Activity Feed component is automatically displayed on the Overview tab and refreshes every 3 seconds to show the latest activities.

## Database

Activities are stored in the `activity_logs` table with:
- Activity type and message
- Status and metadata
- Related website/job IDs
- Timestamp

This allows you to track the full history of what the system has been doing.

