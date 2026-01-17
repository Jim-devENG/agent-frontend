"""
Reply handler task - checks for email replies and updates prospect status
"""
import asyncio
import logging
from typing import Dict, Any, List
from uuid import UUID
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, and_, or_
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add backend directory to path
backend_path = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(backend_path))

from worker.clients.gmail import GmailClient
from app.models.prospect import Prospect
from app.models.email_log import EmailLog

load_dotenv()

logger = logging.getLogger(__name__)

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://art_outreach:art_outreach@localhost:5432/art_outreach")
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def check_replies_async() -> Dict[str, Any]:
    """
    Check Gmail for replies to sent emails and update prospect status
    
    Returns:
        Dictionary with results
    """
    async with AsyncSessionLocal() as db:
        try:
            # Initialize Gmail client
            try:
                gmail_client = GmailClient()
            except ValueError as e:
                logger.error(f"Gmail client initialization failed: {e}")
                return {"success": False, "error": str(e)}
            
            # Get prospects with sent emails
            query = select(Prospect).where(
                and_(
                    Prospect.outreach_status == "sent",
                    Prospect.contact_email.isnot(None)
                )
            )
            
            result = await db.execute(query)
            prospects = result.scalars().all()
            
            logger.info(f"Checking for replies to {len(prospects)} prospects")
            
            replied_count = 0
            errors = []
            
            # Check each prospect for replies
            for prospect in prospects:
                try:
                    # Get email logs for this prospect
                    email_logs_query = select(EmailLog).where(
                        EmailLog.prospect_id == prospect.id
                    ).order_by(EmailLog.sent_at.desc())
                    
                    email_logs_result = await db.execute(email_logs_query)
                    email_logs = email_logs_result.scalars().all()
                    
                    if not email_logs:
                        continue
                    
                    # Check for replies using Gmail API
                    # Search for emails from this contact
                    from_email = prospect.contact_email
                    
                    # Use Gmail API to search for replies
                    # This is a simplified version - in production, use Gmail webhooks or better search
                    search_query = f'from:{from_email} in:inbox'
                    
                    # For now, we'll use a simple approach:
                    # Check if there are any new emails from this contact since we sent
                    # In production, implement proper Gmail search API or webhooks
                    
                    # Placeholder: In production, implement Gmail search
                    # For now, we'll mark this as a TODO
                    logger.debug(f"Checking for replies from {from_email} for prospect {prospect.domain}")
                    
                    # TODO: Implement actual Gmail search/thread checking
                    # This would require:
                    # 1. Getting thread ID from sent email
                    # 2. Checking thread for new messages
                    # 3. Detecting if it's a reply
                    # 4. Updating prospect status
                    
                except Exception as e:
                    error_msg = f"Error checking replies for prospect {prospect.id}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    continue
            
            await db.commit()
            
            logger.info(f"Reply check completed: {replied_count} replies found")
            
            return {
                "success": True,
                "replied_count": replied_count,
                "errors": errors[:10] if errors else []
            }
        
        except Exception as e:
            logger.error(f"Error in reply check: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}


def check_replies_task() -> Dict[str, Any]:
    """
    RQ task wrapper for checking replies
    
    Returns:
        Dictionary with results
    """
    return asyncio.run(check_replies_async())


async def process_reply_async(prospect_id: str, reply_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a detected reply and update prospect status
    
    Args:
        prospect_id: UUID string of the prospect
        reply_data: Dictionary with reply information
    
    Returns:
        Dictionary with results
    """
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(Prospect).where(Prospect.id == UUID(prospect_id)))
            prospect = result.scalar_one_or_none()
            
            if not prospect:
                return {"success": False, "error": "Prospect not found"}
            
            # Update prospect status
            prospect.outreach_status = "replied"
            
            # Store reply data in extra metadata (if we add that field)
            # For now, just update status
            
            await db.commit()
            
            logger.info(f"✅ Updated prospect {prospect.domain} status to 'replied'")
            
            return {
                "success": True,
                "prospect_id": prospect_id,
                "status": "replied"
            }
        
        except Exception as e:
            logger.error(f"Error processing reply for prospect {prospect_id}: {str(e)}")
            return {"success": False, "error": str(e)}

