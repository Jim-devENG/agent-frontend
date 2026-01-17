# API Documentation for Dashboard

## Base URL
```
http://localhost:8000/api/v1
```

## Endpoints

### 1. Get Leads
**GET** `/leads`

Get paginated list of leads/contacts.

**Query Parameters:**
- `skip` (int, default: 0) - Number of records to skip
- `limit` (int, default: 50, max: 200) - Number of records to return
- `category` (string, optional) - Filter by website category
- `has_email` (boolean, optional) - Filter by whether contact has email

**Response:**
```json
{
  "leads": [
    {
      "id": 1,
      "email": "artist@example.com",
      "phone_number": "+1-555-123-4567",
      "social_platform": "instagram",
      "social_url": "https://instagram.com/artist",
      "name": "John Artist",
      "website_id": 1,
      "website_title": "Modern Art Gallery",
      "website_url": "https://example.com",
      "website_category": "art_gallery",
      "created_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 150,
  "skip": 0,
  "limit": 50
}
```

### 2. Get Sent Emails
**GET** `/emails/sent`

Get paginated list of sent emails.

**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 50, max: 200)

**Response:**
```json
{
  "emails": [
    {
      "id": 1,
      "subject": "Collaboration Opportunity",
      "recipient_email": "artist@example.com",
      "status": "sent",
      "website_id": 1,
      "contact_id": 5,
      "website_title": "Modern Art Gallery",
      "sent_at": "2024-01-01T12:00:00Z",
      "created_at": "2024-01-01T11:00:00Z"
    }
  ],
  "total": 75,
  "skip": 0,
  "limit": 50
}
```

### 3. Get Pending Emails
**GET** `/emails/pending`

Get paginated list of pending/draft emails.

**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 50, max: 200)

**Response:**
```json
{
  "emails": [
    {
      "id": 2,
      "subject": "Collaboration Opportunity",
      "recipient_email": "gallery@example.com",
      "status": "draft",
      "website_id": 2,
      "contact_id": 10,
      "website_title": "Contemporary Gallery",
      "created_at": "2024-01-01T13:00:00Z"
    }
  ],
  "total": 25,
  "skip": 0,
  "limit": 50
}
```

### 4. Scrape URL
**POST** `/scrape-url`

Scrape a URL and return results.

**Query Parameters:**
- `url` (string, required) - URL to scrape
- `skip_quality_check` (boolean, default: false) - Bypass quality filtering

**Response:**
```json
{
  "id": 1,
  "url": "https://example.com",
  "domain": "example.com",
  "title": "Modern Art Gallery",
  "description": "Contemporary art gallery",
  "category": "art_gallery",
  "website_type": "gallery",
  "quality_score": 75,
  "is_art_related": true,
  "status": "processed",
  "created_at": "2024-01-01T12:00:00Z"
}
```

### 5. Get Statistics
**GET** `/stats`

Get comprehensive statistics for dashboard.

**Response:**
```json
{
  "leads_collected": 150,
  "emails_extracted": 120,
  "phones_extracted": 45,
  "social_links_extracted": 80,
  "outreach_sent": 75,
  "outreach_pending": 25,
  "outreach_failed": 5,
  "websites_scraped": 200,
  "websites_pending": 15,
  "websites_failed": 10,
  "jobs_completed": 150,
  "jobs_running": 2,
  "jobs_failed": 5,
  "recent_activity": {
    "leads_last_24h": 10,
    "emails_sent_last_24h": 5,
    "websites_scraped_last_24h": 8
  }
}
```

### 6. Get Job Status
**GET** `/jobs/status`

Get status of background jobs.

**Query Parameters:**
- `limit` (int, default: 20, max: 100) - Number of jobs to return
- `job_type` (string, optional) - Filter by job type
- `status` (string, optional) - Filter by status (pending, running, completed, failed)

**Response:**
```json
[
  {
    "id": 1,
    "job_type": "fetch_new_art_websites",
    "status": "completed",
    "result": {
      "discovered": 50,
      "new_websites": 30,
      "skipped": 20
    },
    "error_message": null,
    "started_at": "2024-01-01T03:00:00Z",
    "completed_at": "2024-01-01T03:15:00Z",
    "created_at": "2024-01-01T03:00:00Z"
  }
]
```

### 7. Get Latest Jobs
**GET** `/jobs/latest`

Get latest execution status for each job type.

**Response:**
```json
{
  "fetch_new_art_websites": {
    "status": "completed",
    "result": {
      "discovered": 50,
      "new_websites": 30
    },
    "error_message": null,
    "started_at": "2024-01-01T03:00:00Z",
    "completed_at": "2024-01-01T03:15:00Z",
    "created_at": "2024-01-01T03:00:00Z"
  },
  "scrape_pending_websites": {
    "status": "running",
    "result": null,
    "error_message": null,
    "started_at": "2024-01-01T09:00:00Z",
    "completed_at": null,
    "created_at": "2024-01-01T09:00:00Z"
  }
}
```

## TypeScript/Next.js Integration Example

```typescript
// lib/api.ts
const API_BASE = 'http://localhost:8000/api/v1';

export async function getLeads(skip = 0, limit = 50, category?: string) {
  const params = new URLSearchParams({
    skip: skip.toString(),
    limit: limit.toString(),
  });
  if (category) params.append('category', category);
  
  const res = await fetch(`${API_BASE}/leads?${params}`);
  return res.json();
}

export async function getStats() {
  const res = await fetch(`${API_BASE}/stats`);
  return res.json();
}

export async function getSentEmails(skip = 0, limit = 50) {
  const res = await fetch(`${API_BASE}/emails/sent?skip=${skip}&limit=${limit}`);
  return res.json();
}

export async function getPendingEmails(skip = 0, limit = 50) {
  const res = await fetch(`${API_BASE}/emails/pending?skip=${skip}&limit=${limit}`);
  return res.json();
}

export async function scrapeUrl(url: string, skipQualityCheck = false) {
  const params = new URLSearchParams({ url });
  if (skipQualityCheck) params.append('skip_quality_check', 'true');
  
  const res = await fetch(`${API_BASE}/scrape-url?${params}`, {
    method: 'POST',
  });
  return res.json();
}

export async function getJobStatus(limit = 20) {
  const res = await fetch(`${API_BASE}/jobs/status?limit=${limit}`);
  return res.json();
}

export async function getLatestJobs() {
  const res = await fetch(`${API_BASE}/jobs/latest`);
  return res.json();
}
```

## Dashboard Components Needed

1. **Stats Dashboard**
   - Display: leads_collected, emails_extracted, outreach_sent
   - Show recent_activity (last 24h)
   - Display job status indicators

2. **Leads Table**
   - Paginated table with filters
   - Columns: email, phone, social, website, category
   - Filter by category, has_email

3. **Emails Table**
   - Separate tabs for sent/pending
   - Columns: subject, recipient, status, sent_at
   - Link to website/contact

4. **Job Status Panel**
   - Show latest execution for each job type
   - Status indicators (running, completed, failed)
   - Last run time and results

5. **Scrape URL Form**
   - Input field for URL
   - Checkbox for skip_quality_check
   - Display results after scraping

