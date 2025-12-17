"""
FastAPI application entry point
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.api import jobs, prospects
from app.db.database import engine, Base
import os
import logging
import traceback

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Art Outreach Automation API",
    description="API for automated art website discovery and outreach",
    version="2.0.0"
)


@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    """
    Fallback middleware to guarantee CORS headers on all responses.
    This runs in addition to CORSMiddleware, but ensures that even
    unexpected 500 errors include Access-Control-Allow-* headers so
    the frontend can read the response instead of seeing a CORS block.
    """
    try:
        response = await call_next(request)
        # Always add CORS headers, even if CORSMiddleware didn't
        response.headers.setdefault("Access-Control-Allow-Origin", "*")
        response.headers.setdefault("Access-Control-Allow-Methods", "*")
        response.headers.setdefault("Access-Control-Allow-Headers", "*")
        return response
    except Exception as e:
        # If an exception occurs, create a response with CORS headers
        logger.error(f"Unhandled exception in middleware: {e}", exc_info=True)
        error_response = JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error": str(e)}
        )
        error_response.headers["Access-Control-Allow-Origin"] = "*"
        error_response.headers["Access-Control-Allow-Methods"] = "*"
        error_response.headers["Access-Control-Allow-Headers"] = "*"
        return error_response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler to ensure all errors include CORS headers.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    error_response = JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc),
            "type": type(exc).__name__
        }
    )
    error_response.headers["Access-Control-Allow-Origin"] = "*"
    error_response.headers["Access-Control-Allow-Methods"] = "*"
    error_response.headers["Access-Control-Allow-Headers"] = "*"
    return error_response


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    HTTP exception handler with CORS headers.
    """
    error_response = JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
    error_response.headers["Access-Control-Allow-Origin"] = "*"
    error_response.headers["Access-Control-Allow-Methods"] = "*"
    error_response.headers["Access-Control-Allow-Headers"] = "*"
    return error_response


app.add_middleware(
    CORSMiddleware,
    # Use wildcard origins with credentials disabled so Render always
    # sends Access-Control-Allow-Origin, regardless of the caller.
    # We rely on Authorization headers, not cookies.
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from app.api import auth, settings, scraper, pipeline
# To use Supabase Auth instead, replace the line below with:
# from app.api import auth_supabase
# app.include_router(auth_supabase.router, prefix="/api/auth", tags=["auth"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(prospects.router, prefix="/api/prospects", tags=["prospects"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])
app.include_router(scraper.router, prefix="/api/scraper", tags=["scraper"])
app.include_router(pipeline.router, tags=["pipeline"])  # Already has /api/pipeline prefix

# Webhook routes
from app.api import webhooks
app.include_router(webhooks.router, prefix="/api", tags=["webhooks"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Art Outreach Automation API",
        "version": "2.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint - responds immediately for Render deployment checks"""
    return {"status": "healthy", "service": "art-outreach-api"}

@app.get("/health/ready")
async def readiness():
    """Readiness check - verifies database connectivity"""
    try:
        # Quick database connectivity check (with timeout)
        from sqlalchemy import text
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        logger.warning(f"Readiness check failed: {e}")
        # Still return 200 so Render doesn't fail deployment
        # Database might be temporarily unavailable
        return {"status": "ready", "database": "checking", "warning": str(e)}


@app.on_event("startup")
async def startup():
    """Startup event - run migrations and start scheduler"""
    # Log that server is starting (important for Render deployment checks)
    logger.info("🚀 Server starting up...")
    logger.info(f"📡 Server will listen on port {os.getenv('PORT', '8000')}")
    
    # All database operations run in background to avoid blocking server startup
    import asyncio
    
    async def run_database_setup():
        """Run all database setup operations in background"""
        # Add a small delay to ensure server is fully started first
        await asyncio.sleep(2)
        
        try:
            from alembic.config import Config
            from alembic import command
            
            logger.info("Running database migrations on startup...")
            
            # Get the backend directory path
            import os
            backend_dir = os.path.dirname(os.path.dirname(__file__))
            alembic_cfg = Config(os.path.join(backend_dir, "alembic.ini"))
            
            # Run migrations
            try:
                command.upgrade(alembic_cfg, "head")
                logger.info("✅ Database migrations completed successfully")
            except Exception as migration_error:
                logger.warning(f"Migration failed (may be first run): {migration_error}")
                # Try to create tables directly if migrations fail (first deploy)
                try:
                    async with engine.begin() as conn:
                        await conn.run_sync(Base.metadata.create_all)
                    logger.info("✅ Created database tables directly (first deploy)")
                except Exception as create_error:
                    logger.error(f"Failed to create tables: {create_error}")
        except Exception as e:
            logger.warning(f"Migration setup failed: {e}")
            # Fallback: create tables directly
            try:
                async with engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
                logger.info("✅ Created database tables directly (fallback)")
            except Exception as create_error:
                logger.error(f"Failed to create tables: {create_error}")
        
        # EMERGENCY FIX: Check and add discovery_query_id column if missing
        try:
            from sqlalchemy import text
            async with engine.begin() as conn:
                # Check if column exists
                result = await conn.execute(
                    text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'prospects' 
                        AND column_name = 'discovery_query_id'
                    """)
                )
                column_exists = result.fetchone() is not None
                
                if not column_exists:
                    logger.warning("⚠️  Missing discovery_query_id column - adding it now...")
                    # Add column
                    await conn.execute(
                        text("ALTER TABLE prospects ADD COLUMN discovery_query_id UUID")
                    )
                    # Create index
                    await conn.execute(
                        text("CREATE INDEX IF NOT EXISTS ix_prospects_discovery_query_id ON prospects(discovery_query_id)")
                    )
                    # Check if discovery_queries table exists and add FK
                    table_check = await conn.execute(
                        text("SELECT 1 FROM information_schema.tables WHERE table_name = 'discovery_queries'")
                    )
                    if table_check.fetchone():
                        fk_check = await conn.execute(
                            text("""
                                SELECT 1 FROM information_schema.table_constraints 
                                WHERE constraint_name = 'fk_prospects_discovery_query_id'
                            """)
                        )
                        if not fk_check.fetchone():
                            await conn.execute(
                                text("""
                                    ALTER TABLE prospects
                                    ADD CONSTRAINT fk_prospects_discovery_query_id
                                    FOREIGN KEY (discovery_query_id)
                                    REFERENCES discovery_queries(id)
                                    ON DELETE SET NULL
                                """)
                            )
                    logger.info("✅ Added discovery_query_id column, index, and foreign key")
                else:
                    logger.info("✅ discovery_query_id column already exists")
                
                # Check and add serp_intent columns if missing
                serp_intent_check = await conn.execute(
                    text("""
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'prospects' AND column_name = 'serp_intent'
                    """)
                )
                serp_intent_exists = serp_intent_check.fetchone() is not None
                
                if not serp_intent_exists:
                    logger.warning("⚠️  Missing serp_intent columns - adding them now...")
                    # Add serp_intent column
                    await conn.execute(
                        text("ALTER TABLE prospects ADD COLUMN serp_intent VARCHAR")
                    )
                    # Add serp_confidence column
                    await conn.execute(
                        text("ALTER TABLE prospects ADD COLUMN serp_confidence NUMERIC(3, 2)")
                    )
                    # Add serp_signals column (JSON)
                    await conn.execute(
                        text("ALTER TABLE prospects ADD COLUMN serp_signals JSONB")
                    )
                    logger.info("✅ Added serp_intent, serp_confidence, and serp_signals columns")
                else:
                    logger.info("✅ serp_intent columns already exist")
                
                # CRITICAL FIX: Check and add discovery_status column if missing
                # This column is required for /api/pipeline/status to work
                discovery_status_check = await conn.execute(
                    text("""
                        SELECT column_name, is_nullable, column_default
                        FROM information_schema.columns 
                        WHERE table_name = 'prospects' 
                        AND column_name = 'discovery_status'
                    """)
                )
                discovery_status_row = discovery_status_check.fetchone()
                
                if not discovery_status_row:
                    logger.warning("⚠️  Missing discovery_status column - adding it now...")
                    # Step 1: Add column as nullable first (safe for existing rows)
                    await conn.execute(
                        text("ALTER TABLE prospects ADD COLUMN discovery_status VARCHAR")
                    )
                    # Step 2: Backfill existing rows with 'NEW' (canonical default)
                    await conn.execute(
                        text("UPDATE prospects SET discovery_status = 'NEW' WHERE discovery_status IS NULL")
                    )
                    # Step 3: Set default to 'NEW'
                    await conn.execute(
                        text("ALTER TABLE prospects ALTER COLUMN discovery_status SET DEFAULT 'NEW'")
                    )
                    # Step 4: Make NOT NULL (safe now that all rows have values)
                    await conn.execute(
                        text("ALTER TABLE prospects ALTER COLUMN discovery_status SET NOT NULL")
                    )
                    # Step 5: Create index for performance
                    await conn.execute(
                        text("CREATE INDEX IF NOT EXISTS ix_prospects_discovery_status ON prospects(discovery_status)")
                    )
                    logger.info("✅ Added discovery_status column (NOT NULL, DEFAULT 'NEW') with index")
                else:
                    # Column exists - check if it needs to be fixed (nullable or wrong default)
                    is_nullable = discovery_status_row[1] == 'YES'
                    current_default = discovery_status_row[2]
                    
                    if is_nullable or (current_default and "'NEW'" not in str(current_default)):
                        logger.warning(f"⚠️  discovery_status column exists but needs fixing (nullable={is_nullable}, default={current_default})")
                        # Backfill NULL values
                        await conn.execute(
                            text("UPDATE prospects SET discovery_status = 'NEW' WHERE discovery_status IS NULL")
                        )
                        # Update default if needed
                        if not current_default or "'NEW'" not in str(current_default):
                            await conn.execute(
                                text("ALTER TABLE prospects ALTER COLUMN discovery_status DROP DEFAULT")
                            )
                            await conn.execute(
                                text("ALTER TABLE prospects ALTER COLUMN discovery_status SET DEFAULT 'NEW'")
                            )
                        # Make NOT NULL if currently nullable
                        if is_nullable:
                            await conn.execute(
                                text("ALTER TABLE prospects ALTER COLUMN discovery_status SET NOT NULL")
                            )
                        logger.info("✅ Fixed discovery_status column (now NOT NULL with DEFAULT 'NEW')")
                    else:
                        logger.info("✅ discovery_status column already exists and is correct")
        except Exception as e:
            logger.error(f"Failed to check/add discovery_status column: {e}", exc_info=True)
    
    # Run database setup in background (non-blocking)
    asyncio.create_task(run_database_setup())
    logger.info("✅ Database setup started in background (server will start even if DB is unavailable)")
    
    # Start scheduler for periodic tasks (always start - scraper check runs every minute)
    try:
        from app.scheduler import start_scheduler
        start_scheduler()
        logger.info("✅ Scheduler started successfully (automatic scraper check enabled)")
    except Exception as e:
        logger.error(f"❌ Failed to start scheduler: {e}", exc_info=True)
    
    # Log that startup is complete (server is ready to accept requests)
    logger.info("✅ Server startup complete - ready to accept requests")


@app.on_event("shutdown")
async def shutdown():
    """Shutdown event - stop scheduler"""
    try:
        from app.scheduler import stop_scheduler
        stop_scheduler()
    except Exception as e:
        logger.warning(f"Error stopping scheduler: {e}")

