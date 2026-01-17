# Phase 2 Complete - Ingestion Worker

## ✅ What's Been Built

### 1. DataForSEO Client (`worker/clients/dataforseo.py`)
- Async HTTP client for DataForSEO API
- SERP Google Organic search
- On-page crawling task submission
- Result polling with retry logic
- Location code mapping (USA, Canada, UK, Germany, France, Europe)

### 2. Discovery Task (`worker/tasks/discovery.py`)
- RQ task that processes discovery jobs
- Calls DataForSEO API for each search query
- Parses results and creates Prospect records
- Deduplicates by domain
- Updates job status (pending → running → completed/failed)
- Saves DataForSEO payload for reference

### 3. RQ Worker (`worker/worker.py`)
- Worker entry point
- Connects to Redis queue
- Processes jobs from `discovery` queue
- Can run multiple workers for scaling

### 4. Backend Integration
- Updated `POST /api/jobs/discover` to queue RQ tasks
- Jobs are automatically picked up by workers
- Status can be checked via `GET /api/jobs/{id}/status`

## 🔄 How It Works

1. **User creates discovery job** via `POST /api/jobs/discover`
2. **Backend creates Job record** in database with status "pending"
3. **Backend queues RQ task** to Redis `discovery` queue
4. **Worker picks up task** and calls `discover_websites_task(job_id)`
5. **Task processes job**:
   - Generates search queries from keywords + categories
   - Calls DataForSEO API for each query
   - Parses results and creates Prospect records
   - Updates job status to "completed" or "failed"
6. **User checks status** via `GET /api/jobs/{id}/status`

## 📁 Project Structure

```
worker/
├── clients/
│   └── dataforseo.py      # DataForSEO API client
├── tasks/
│   └── discovery.py        # Discovery task implementation
├── worker.py              # RQ worker entry point
├── requirements.txt
└── README.md
```

## 🚀 Next Steps

**Phase 3**: Implement Hunter enrichment worker
- Process prospects without emails
- Call Hunter.io API for email lookup
- Update prospect records with contact emails

## ⚙️ Configuration

Required environment variables:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `DATAFORSEO_LOGIN` - DataForSEO email
- `DATAFORSEO_PASSWORD` - DataForSEO password/token

## 🧪 Testing

To test locally:
1. Start PostgreSQL and Redis (via Docker Compose)
2. Start backend: `cd backend && uvicorn app.main:app --reload`
3. Start worker: `cd worker && python worker.py`
4. Create discovery job via API
5. Watch worker process the job

