"""
Database configuration and session management
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment
# Render provides postgresql:// but we need postgresql+asyncpg:// for async SQLAlchemy
raw_database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://art_outreach:art_outreach@localhost:5432/art_outreach")
# Convert postgresql:// to postgresql+asyncpg:// if needed
if raw_database_url.startswith("postgresql://"):
    DATABASE_URL = raw_database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif raw_database_url.startswith("postgres://"):
    DATABASE_URL = raw_database_url.replace("postgres://", "postgresql+asyncpg://", 1)
else:
    DATABASE_URL = raw_database_url

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

