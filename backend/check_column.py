"""Check if discovery_query_id column exists"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.database import engine
from sqlalchemy import text

async def check():
    async with engine.begin() as conn:
        result = await conn.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name='prospects' AND column_name='discovery_query_id'"
        ))
        row = result.fetchone()
        if row:
            print("✅ Column 'discovery_query_id' EXISTS")
        else:
            print("❌ Column 'discovery_query_id' DOES NOT EXIST")
        return bool(row)

if __name__ == "__main__":
    exists = asyncio.run(check())
    sys.exit(0 if exists else 1)

