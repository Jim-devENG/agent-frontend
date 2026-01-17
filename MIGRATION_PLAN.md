# Migration Plan - Old to New Architecture

## Current Situation
- Old monolithic codebase in root directory
- New architecture structure created: `backend/`, `worker/`, `frontend-new/`, `infra/`

## Options

### Option 1: Archive Old Code (Recommended)
Move all old code to `legacy/` folder to keep it for reference but start fresh with new architecture.

**Pros:**
- Clean slate for new architecture
- Old code preserved for reference
- No confusion between old and new

**Cons:**
- Need to rebuild everything from scratch
- Can't reuse existing code directly

### Option 2: Migrate Incrementally
Move useful parts of old code into new structure, refactor as needed.

**Pros:**
- Reuse existing logic (API clients, scrapers, etc.)
- Faster development
- Less code to rewrite

**Cons:**
- More complex migration
- Need to refactor old code to fit new architecture

### Option 3: Keep Both (Current State)
Keep old code in root, build new in subdirectories, switch when ready.

**Pros:**
- Can run both systems
- Gradual transition
- No data loss

**Cons:**
- Confusing structure
- Duplicate code
- Harder to maintain

## Recommendation

**Option 1 (Archive)** - Start fresh with clean architecture:
1. Move old code to `legacy/` folder
2. Build new architecture from scratch
3. Migrate data when new system is ready

This ensures:
- Clean, maintainable codebase
- Proper separation of concerns
- Production-ready architecture
- No technical debt from old system

## Files to Archive

- All Python files in root (except new structure)
- `frontend/` (old frontend)
- `api/`, `db/`, `extractor/`, `scraper/`, `jobs/`, `utils/`, `ai/`, `emailer/`
- Old config files, scripts, documentation
- SQLite database (will migrate to PostgreSQL)

## Files to Keep

- `.git/` (version control)
- `.github/` (CI/CD)
- `backend/`, `worker/`, `frontend-new/`, `infra/` (new structure)
- `ARCHITECTURE.md`, `README_NEW_ARCHITECTURE.md` (new docs)
- `.gitignore`, `requirements.txt` (will update for new structure)

## Next Steps

1. Create `legacy/` directory
2. Move old code to `legacy/`
3. Clean up root directory
4. Start building new architecture in clean structure

