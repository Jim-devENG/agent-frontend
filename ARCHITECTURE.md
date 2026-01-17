# Production Architecture - Art Outreach Automation System

## Overview
This document outlines the production-ready architecture for rebuilding the art outreach automation system with proper separation of concerns, scalability, and maintainability.

## Architecture Components

### 1. Frontend (Vercel)
- **Tech**: Next.js 14+ with TypeScript
- **Purpose**: Dashboard, job controls, prospect list, manual inputs, test-run tools
- **Deployment**: Vercel (automatic from GitHub)
- **Root Directory**: `frontend/`

### 2. Backend API (Render)
- **Tech**: FastAPI (Python) with async/await
- **Purpose**: REST API endpoints for job management, prospect listing, email composition/sending
- **Deployment**: Render Web Service

### 3. Worker Service (Render)
- **Tech**: Python with RQ (Redis Queue) or Celery
- **Purpose**: Background workers for scraping, enrichment, email sending
- **Deployment**: Render Background Worker

### 4. Queue/Broker
- **Tech**: Redis
- **Purpose**: Job queue for background tasks
- **Deployment**: Render Redis or Upstash Redis

### 5. Database
- **Tech**: PostgreSQL
- **Purpose**: Store prospects, jobs, email logs, audit trails
- **Deployment**: Render PostgreSQL or Supabase

### 6. Third-Party APIs
- **DataForSEO**: Website discovery and on-page crawling
- **Hunter.io**: Email enrichment
- **Google Gemini**: Email composition
- **Gmail API**: Email sending via OAuth2

## Data Model

### Prospects Table
```sql
CREATE TABLE prospects (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  domain text NOT NULL,
  page_url text,
  page_title text,
  contact_email text,
  contact_method text,
  da_est numeric,
  score numeric,
  outreach_status text DEFAULT 'pending', -- pending/sent/replied/accepted/rejected
  last_sent timestamptz,
  followups_sent int DEFAULT 0,
  dataforseo_payload jsonb,
  hunter_payload jsonb,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);
```

### Jobs Table
```sql
CREATE TABLE jobs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid,
  job_type text NOT NULL, -- discover, enrich, compose, send
  params jsonb,
  status text DEFAULT 'pending', -- pending/running/completed/failed
  result jsonb,
  error_message text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);
```

### Email Logs Table
```sql
CREATE TABLE email_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  prospect_id uuid REFERENCES prospects(id),
  subject text,
  body text,
  response jsonb,
  sent_at timestamptz DEFAULT now()
);
```

## API Endpoints

### Job Management
- `POST /api/jobs/discover` - Start discovery job
- `GET /api/jobs/{id}/status` - Get job status
- `GET /api/jobs` - List all jobs

### Prospects
- `GET /api/prospects` - List prospects with filters
- `GET /api/prospects/{id}` - Get prospect details
- `POST /api/prospects/{id}/compose` - Compose email for prospect
- `POST /api/prospects/{id}/send` - Send email to prospect

## Worker Tasks

1. **Discovery Worker**: Calls DataForSEO SERP API, parses results, saves prospects
2. **Enrichment Worker**: Calls Hunter.io for email lookup
3. **Scoring Worker**: Calculates prospect scores
4. **Compose Worker**: Calls Gemini to generate email content
5. **Send Worker**: Sends emails via Gmail API
6. **Follow-up Worker**: Schedules and sends follow-up emails

## Environment Variables

### Backend/Worker
```
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
DATAFORSEO_LOGIN=...
DATAFORSEO_PASSWORD=...
HUNTER_IO_API_KEY=...
GEMINI_API_KEY=...
GMAIL_CLIENT_ID=...
GMAIL_CLIENT_SECRET=...
GMAIL_REFRESH_TOKEN=...
JWT_SECRET_KEY=...
```

### Frontend
```
NEXT_PUBLIC_API_BASE_URL=https://your-backend.onrender.com/api
```

## Deployment

### Render Services
1. **Backend API**: Web Service, Python, FastAPI
2. **Worker**: Background Worker, Python, RQ worker
3. **PostgreSQL**: Managed Database
4. **Redis**: Managed Redis

### Vercel
- Connect GitHub repo
- Set root directory to `frontend/`
- Configure environment variables
- Auto-deploy on push to main

## Development Workflow

1. Local development with Docker Compose (Postgres + Redis)
2. Run migrations: `alembic upgrade head`
3. Start backend: `uvicorn backend.main:app --reload`
4. Start worker: `rq worker`
5. Start frontend: `cd frontend && npm run dev`

## Testing Strategy

- Unit tests for core logic (parsing, scoring, compose)
- Integration tests with mocked APIs
- End-to-end tests with test domains
- CI/CD with GitHub Actions

