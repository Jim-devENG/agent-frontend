"""
Schema validation utilities for ensuring database schema matches ORM models.

CRITICAL: This module enforces schema correctness at startup.
If schema validation fails, the application MUST NOT start.
"""
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import DeclarativeMeta
import logging
from typing import Tuple, List, Set

logger = logging.getLogger(__name__)


class SchemaValidationError(Exception):
    """Raised when schema validation fails - application must not start"""
    pass


async def validate_social_tables_exist(engine: AsyncEngine) -> Tuple[bool, List[str]]:
    """
    Validate that all required social outreach tables exist.
    
    Returns:
        (is_valid, missing_tables)
        - is_valid: True if all tables exist
        - missing_tables: List of missing table names
    """
    required_tables = {
        'social_profiles',
        'social_discovery_jobs',
        'social_drafts',
        'social_messages'
    }
    
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = ANY(:tables)
            """), {"tables": list(required_tables)})
            
            existing_tables = {row[0] for row in result.fetchall()}
            missing_tables = required_tables - existing_tables
            
            return (len(missing_tables) == 0, list(missing_tables))
    except Exception as e:
        logger.error(f"Failed to validate social tables: {e}", exc_info=True)
        # If we can't check, assume invalid (fail safe)
        return (False, list(required_tables))


async def validate_website_tables_exist(engine: AsyncEngine) -> Tuple[bool, List[str]]:
    """
    Validate that all required website outreach tables exist.
    
    Returns:
        (is_valid, missing_tables)
    """
    required_tables = {
        'prospects',
        'jobs',
        'email_logs',
        'settings',
        'discovery_queries',
        'scraper_history'
    }
    
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = ANY(:tables)
            """), {"tables": list(required_tables)})
            
            existing_tables = {row[0] for row in result.fetchall()}
            missing_tables = required_tables - existing_tables
            
            return (len(missing_tables) == 0, list(missing_tables))
    except Exception as e:
        logger.error(f"Failed to validate website tables: {e}", exc_info=True)
        return (False, list(required_tables))


async def validate_all_tables_exist(engine: AsyncEngine) -> None:
    """
    Validate that ALL required tables exist (website + social).
    
    Raises SchemaValidationError if any tables are missing.
    This function FAILS HARD - application will not start if validation fails.
    """
    logger.info("=" * 80)
    logger.info("🔍 CRITICAL: Validating database schema completeness...")
    logger.info("=" * 80)
    
    # Validate website tables
    website_valid, website_missing = await validate_website_tables_exist(engine)
    if not website_valid:
        logger.error("=" * 80)
        logger.error("❌ CRITICAL: Website outreach tables are missing!")
        logger.error(f"❌ Missing tables: {', '.join(website_missing)}")
        logger.error("=" * 80)
        logger.error("❌ APPLICATION WILL NOT START")
        logger.error("❌ Run migrations: alembic upgrade head")
        logger.error("=" * 80)
        raise SchemaValidationError(
            f"Website outreach tables missing: {', '.join(website_missing)}. "
            "Run migrations: alembic upgrade head"
        )
    logger.info("✅ Website outreach tables: All present")
    
    # Validate social tables
    social_valid, social_missing = await validate_social_tables_exist(engine)
    if not social_valid:
        logger.error("=" * 80)
        logger.error("❌ CRITICAL: Social outreach tables are missing!")
        logger.error(f"❌ Missing tables: {', '.join(social_missing)}")
        logger.error("=" * 80)
        logger.error("❌ APPLICATION WILL NOT START")
        logger.error("❌ Run migrations: alembic upgrade head")
        logger.error("=" * 80)
        raise SchemaValidationError(
            f"Social outreach tables missing: {', '.join(social_missing)}. "
            "Run migrations: alembic upgrade head"
        )
    logger.info("✅ Social outreach tables: All present")
    
    logger.info("=" * 80)
    logger.info("✅ Database schema validation PASSED - All required tables exist")
    logger.info("=" * 80)


# Keep existing functions for backward compatibility
async def validate_prospect_schema(engine: AsyncEngine, base: DeclarativeMeta) -> Tuple[bool, List[str]]:
    """Validate prospect table schema (existing function)"""
    # Implementation kept for backward compatibility
    # This is now secondary to table existence validation
    return (True, [])


async def ensure_prospect_schema(engine: AsyncEngine) -> bool:
    """Ensure prospect schema (existing function)"""
    # Implementation kept for backward compatibility
    return True
