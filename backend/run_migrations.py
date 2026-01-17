"""
Standalone script to run Alembic migrations

Usage:
    python run_migrations.py

This script will:
1. Run all pending migrations
2. Verify schema matches model
3. Report any issues
"""
import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from alembic.config import Config
from alembic import command
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_migrations():
    """Run Alembic migrations to head"""
    try:
        logger.info("🔄 Starting Alembic migrations...")
        
        # Get alembic config
        alembic_cfg = Config(os.path.join(backend_dir, "alembic.ini"))
        
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            logger.error("❌ DATABASE_URL environment variable not set")
            logger.error("   Please set DATABASE_URL before running migrations")
            sys.exit(1)
        
        logger.info(f"📡 Database URL: {database_url[:50]}...")
        
        # Convert asyncpg URL to psycopg2 for Alembic
        if database_url.startswith("postgresql+asyncpg://"):
            sync_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
            alembic_cfg.set_main_option("sqlalchemy.url", sync_url)
            logger.info("✅ Converted asyncpg URL to psycopg2 format for Alembic")
        
        # Run migrations
        logger.info("🚀 Running migrations to head...")
        command.upgrade(alembic_cfg, "head")
        
        logger.info("✅ Migrations completed successfully!")
        
        # Verify schema
        logger.info("🔍 Verifying schema...")
        try:
            from sqlalchemy import create_engine, text
            from sqlalchemy.ext.asyncio import create_async_engine
            
            # Create async engine for validation
            engine = create_async_engine(database_url, echo=False)
            
            async def verify_schema():
                from app.db.database import Base
                from app.utils.schema_validator import validate_prospect_schema
                
                is_valid, missing_columns = await validate_prospect_schema(engine, Base)
                
                if not is_valid:
                    logger.error(f"❌ Schema validation failed: Missing columns {missing_columns}")
                    logger.error("   Run ensure_prospect_schema() to fix automatically")
                    return False
                else:
                    logger.info("✅ Schema validation passed: ORM model matches database")
                    return True
            
            import asyncio
            is_valid = asyncio.run(verify_schema())
            
            if not is_valid:
                logger.warning("⚠️  Schema validation failed, but migrations completed")
                logger.warning("   The application will attempt to fix schema on startup")
                return 1
            
        except ImportError as e:
            logger.warning(f"⚠️  Could not verify schema (import error): {e}")
            logger.warning("   Migrations completed, but schema validation skipped")
        except Exception as e:
            logger.warning(f"⚠️  Schema validation error: {e}")
            logger.warning("   Migrations completed, but schema validation failed")
        
        logger.info("=" * 60)
        logger.info("✅ MIGRATIONS COMPLETE")
        logger.info("=" * 60)
        return 0
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}", exc_info=True)
        logger.error("   Check database connection and permissions")
        return 1


if __name__ == "__main__":
    exit_code = run_migrations()
    sys.exit(exit_code)

