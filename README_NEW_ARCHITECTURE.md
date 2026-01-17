# Art Outreach Automation System - New Architecture

## Overview

This is a complete rebuild of the art outreach automation system with a production-ready architecture featuring:

- **Separated concerns**: Backend API, Worker service, Frontend
- **Scalable queue system**: Redis-based job queue
- **Production database**: PostgreSQL instead of SQLite
- **Proper async processing**: Background workers for heavy tasks
- **Modern stack**: FastAPI + Next.js + PostgreSQL + Redis

## Repository Structure

```
.
├── backend/          # FastAPI backend API
├── worker/           # RQ worker service for background jobs
├── frontend/         # Next.js frontend dashboard
├── infra/            # Infrastructure configs (Docker, etc.)
└── ARCHITECTURE.md   # Detailed architecture documentation
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional, for local dev)

### Local Development

1. **Start infrastructure** (PostgreSQL + Redis):
```bash
cd infra
docker-compose up -d
```

2. **Setup Backend**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload
```

3. **Setup Worker**:
```bash
cd worker
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
rq worker --url redis://localhost:6379/0
```

4. **Setup Frontend**:
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

See individual README files in each directory for required environment variables.

## Deployment

### Render (Backend + Worker)

1. Create PostgreSQL database on Render
2. Create Redis instance on Render
3. Deploy backend as Web Service
4. Deploy worker as Background Worker
5. Set all environment variables in Render dashboard

### Vercel (Frontend)

1. Connect GitHub repository
2. Set root directory to `frontend-new/`
3. Configure environment variables
4. Deploy automatically

## Migration from Old System

The old system (monolithic FastAPI + SQLite) is preserved in the root directory. To migrate:

1. Export data from SQLite database
2. Import into PostgreSQL using migration scripts
3. Update API endpoints to match new structure
4. Test thoroughly before switching

## Development Phases

This rebuild follows a phased approach:

- **Phase 0**: Repository scaffolding ✅
- **Phase 1**: API & Database (in progress)
- **Phase 2**: Ingestion worker
- **Phase 3**: Enrichment
- **Phase 4**: Scoring
- **Phase 5**: Compose & Gemini
- **Phase 6**: Send
- **Phase 7**: Follow-ups & Replies
- **Phase 8**: Frontend
- **Phase 9**: Deploy & Infrastructure

## Testing

Run tests for each component:

```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd frontend-new && npm test

# Worker tests
cd worker && pytest
```

## CI/CD

GitHub Actions automatically:
- Runs tests on push/PR
- Lints code
- Builds frontend
- (Future) Deploys to Render/Vercel

## Support

For issues or questions, see:
- `ARCHITECTURE.md` for detailed architecture
- Individual README files in each directory
- GitHub Issues for bug reports

