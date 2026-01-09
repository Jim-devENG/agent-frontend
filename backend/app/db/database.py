"""
Database configuration and session management

ISOLATED: Engine creation is lazy to prevent conflicts with Alembic imports.
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
import os
import sys
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass  # Continue without .env if it has issues
import logging

logger = logging.getLogger(__name__)

# Database URL from environment
# Render provides postgresql:// but we need postgresql+asyncpg:// for async SQLAlchemy
raw_database_url = os.getenv("DATABASE_URL")

if not raw_database_url:
    logger.warning("DATABASE_URL environment variable not set! Using default local database.")
    raw_database_url = "postgresql+asyncpg://art_outreach:art_outreach@localhost:5432/art_outreach"

# Log database URL info (without exposing password)
if raw_database_url:
    # Mask password in URL for logging
    safe_url = raw_database_url
    if "@" in safe_url:
        parts = safe_url.split("@")
        if ":" in parts[0]:
            user_pass = parts[0].split(":")
            if len(user_pass) >= 2:
                safe_url = f"{user_pass[0]}:****@{parts[1]}"
    logger.info(f"📊 DATABASE_URL: {safe_url}")
else:
    logger.warning("⚠️  DATABASE_URL environment variable not set!")

# Convert postgresql:// to postgresql+asyncpg:// if needed
if raw_database_url.startswith("postgresql://"):
    DATABASE_URL = raw_database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    logger.info("Converted postgresql:// to postgresql+asyncpg://")
elif raw_database_url.startswith("postgres://"):
    DATABASE_URL = raw_database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    logger.info("Converted postgres:// to postgresql+asyncpg://")
else:
    DATABASE_URL = raw_database_url
    logger.info("Using DATABASE_URL as-is (already in correct format)")

# Supabase requires SSL connections - add SSL parameters if not present
# Check if this is a Supabase connection (contains .supabase.co)
if ".supabase.co" in DATABASE_URL and "sslmode" not in DATABASE_URL:
    # Add SSL parameters for Supabase
    if "?" in DATABASE_URL:
        DATABASE_URL += "&sslmode=require"
    else:
        DATABASE_URL += "?sslmode=require"
    logger.info("Added SSL parameters for Supabase connection")

# Log connection details (without password)
if "@" in DATABASE_URL:
    try:
        # Extract host and port for logging
        parts = DATABASE_URL.split("@")
        if len(parts) > 1:
            host_port_db = parts[1]
            if "/" in host_port_db:
                host_port = host_port_db.split("/")[0]
                logger.info(f"Attempting to connect to database at: {host_port}")
    except Exception:
        pass

# CRITICAL: Lazy engine initialization to prevent conflicts with Alembic
# Alembic imports this module but uses its own sync engine
# We detect Alembic context and delay engine creation

_engine_instance = None
_engine_lock = None

def _get_engine():
    """Get or create the async engine - lazy initialization"""
    global _engine_instance, _engine_lock
    if _engine_instance is None:
        import threading
        if _engine_lock is None:
            _engine_lock = threading.Lock()
        with _engine_lock:
            if _engine_instance is None:
                _engine_instance = create_async_engine(
                    DATABASE_URL,
                    echo=False,  # Set to False in production (was True for debugging)
                    future=True,
                    pool_pre_ping=True,
                    pool_size=10,
                    max_overflow=20
                )
    return _engine_instance

# Check if we're being imported by Alembic
# Alembic runs as a script, so sys.argv[0] will contain 'alembic'
_is_alembic_context = (
    len(sys.argv) > 0 and 'alembic' in sys.argv[0].lower()
) or any('alembic' in str(arg).lower() for arg in sys.argv)

if _is_alembic_context:
    # Being imported by Alembic - don't create engine
    # Create a proxy that will create engine on first use (but Alembic won't use it)
    class EngineProxy:
        """Proxy for engine that creates it lazily - Alembic won't use this"""
        def __getattr__(self, name):
            return getattr(_get_engine(), name)
        def __call__(self, *args, **kwargs):
            return _get_engine()(*args, **kwargs)
        def __enter__(self):
            return _get_engine().__enter__()
        def __exit__(self, *args):
            return _get_engine().__exit__(*args)
    engine = EngineProxy()
else:
    # Normal application import - create engine immediately
    engine = _get_engine()

# Create async session factory
# Use lazy engine access for session factory
_session_factory_instance = None
_session_factory_lock = None

def _get_session_factory():
    """Get or create the session factory"""
    global _session_factory_instance, _session_factory_lock
    if _session_factory_instance is None:
        import threading
        if _session_factory_lock is None:
            _session_factory_lock = threading.Lock()
        with _session_factory_lock:
            if _session_factory_instance is None:
                _session_factory_instance = async_sessionmaker(
                    _get_engine(),
                    class_=AsyncSession,
                    expire_on_commit=False,
                    autocommit=False,
                    autoflush=False
                )
    return _session_factory_instance

if _is_alembic_context:
    # For Alembic, create a proxy (but Alembic won't use it)
    class SessionFactoryProxy:
        def __call__(self, *args, **kwargs):
            return _get_session_factory()(*args, **kwargs)
        def __getattr__(self, name):
            return getattr(_get_session_factory(), name)
    AsyncSessionLocal = SessionFactoryProxy()
else:
    AsyncSessionLocal = _get_session_factory()

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database session
    """
    try:
        async with AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Database session error: {e}", exc_info=True)
                raise
            finally:
                await session.close()
    except Exception as e:
        logger.error(f"Failed to create database session: {e}", exc_info=True)
        logger.error(f"DATABASE_URL is set: {bool(os.getenv('DATABASE_URL'))}")
        if "@" in DATABASE_URL:
            try:
                parts = DATABASE_URL.split("@")
                if len(parts) > 1:
                    host_port = parts[1].split("/")[0]
                    logger.error(f"Attempted to connect to: {host_port}")
            except Exception:
                pass
        raise
