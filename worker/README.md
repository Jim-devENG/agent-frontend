# Worker Service

Background worker service using RQ (Redis Queue) for processing jobs.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables (create `.env` file):
```
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/art_outreach
REDIS_URL=redis://localhost:6379/0
DATAFORSEO_LOGIN=your_email@example.com
DATAFORSEO_PASSWORD=your_password
```

4. Start Redis (if not using managed service):
```bash
redis-server
```

5. Start the worker:
```bash
python worker.py
```

## Worker Types

- **Discovery Worker**: Processes DataForSEO discovery jobs
  - Queue: `discovery`
  - Task: `discover_websites_task`

## Project Structure

```
worker/
├── tasks/
│   └── discovery.py        # DataForSEO discovery tasks
├── clients/
│   └── dataforseo.py      # DataForSEO API client
├── worker.py              # RQ worker entry point
├── requirements.txt
└── README.md
```

## Running Workers

### Single Worker
```bash
python worker.py
```

### Multiple Workers (for scaling)
```bash
# Terminal 1
python worker.py

# Terminal 2
python worker.py

# Terminal 3
python worker.py
```

## Monitoring

Check Redis queue status:
```bash
redis-cli
> LLEN rq:queue:discovery
> LRANGE rq:queue:discovery 0 -1
```

## Integration with Backend

The backend API queues jobs to Redis, and workers pick them up automatically. No manual coordination needed.
