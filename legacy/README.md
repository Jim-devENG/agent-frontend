# Legacy Codebase

This directory contains the old monolithic codebase that has been archived.

## What's Here

- **api/**: Old FastAPI routes
- **db/**: Old SQLite database models
- **extractor/**: Email/contact extraction logic
- **scraper/**: Website scraping logic
- **jobs/**: Background job scheduling
- **utils/**: Utility functions
- **ai/**: AI email generation
- **emailer/**: Email sending logic
- **frontend/**: Old Next.js frontend
- **docs/**: Old documentation files

## Why Archived?

The old codebase was monolithic with:
- SQLite database (not production-ready)
- Mixed concerns (API + workers in same process)
- No proper queue system
- Difficult to scale

## New Architecture

The new architecture is being built in:
- `backend/`: FastAPI backend API
- `worker/`: RQ worker service
- `frontend-new/`: Next.js frontend
- `infra/`: Infrastructure configs

## Migration Notes

If you need to reference old code:
- API clients (Hunter.io, DataForSEO) can be reused
- Scraping logic can be adapted
- Email extraction logic can be ported
- Database migration scripts needed for SQLite → PostgreSQL

## Status

This code is preserved for reference only. The new architecture should be built from scratch following the architecture document.

