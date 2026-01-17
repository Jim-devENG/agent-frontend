"""
Follow-up task - sends follow-up emails to prospects
"""
import asyncio
import logging
from typing import Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, and_
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add backend directory to path
backend_path = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(backend_path))

from worker.clients.gmail import GmailClient
from worker.clients.gemini import GeminiClient
from app.models.job import Job
from app.models.prospect import Prospect
from app.models.email_log import EmailLog

load_dotenv()

logger = logging.getLogger(__name__)

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://art_outreach:art_outreach@localhost:5432/art_outreach")
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def send_followups_async(job_id: str) -> Dict[str, Any]:
    """
    Async function to send follow-up emails
    
    Args:
        job_id: UUID of the job to process
    
    Returns:
        Dictionary with results
    """
    async with AsyncSessionLocal() as db:
        try:
            # Get job
            result = await db.execute(select(Job).where(Job.id == UUID(job_id)))
            job = result.scalar_one_or_none()
            
            if not job:
                logger.error(f"Job {job_id} not found")
                return {"success": False, "error": "Job not found"}
            
            # Update job status
            job.status = "running"
            await db.commit()
            
            params = job.params or {}
            days_since_sent = params.get("days_since_sent", 7)  # Default: 7 days
            max_followups = params.get("max_followups", 3)  # Default: max 3 follow-ups
            max_prospects = params.get("max_prospects", 100)
            
            logger.info(f"Starting follow-up job {job_id}: days_since_sent={days_since_sent}, max_followups={max_followups}")
            
            # Initialize clients
            try:
                gmail_client = GmailClient()
                gemini_client = GeminiClient()
            except ValueError as e:
                logger.error(f"Client initialization failed: {e}")
                job.status = "failed"
                job.error_message = str(e)
                await db.commit()
                return {"success": False, "error": str(e)}
            
            # Calculate cutoff date
            cutoff_date = datetime.utcnow() - timedelta(days=days_since_sent)
            
            # Get prospects that need follow-ups
            query = select(Prospect).where(
                and_(
                    Prospect.outreach_status == "sent",
                    Prospect.last_sent.isnot(None),
                    Prospect.last_sent <= cutoff_date,
                    Prospect.followups_sent < max_followups,
                    Prospect.contact_email.isnot(None)
                )
            ).order_by(Prospect.last_sent.asc()).limit(max_prospects)
            
            result = await db.execute(query)
            prospects = result.scalars().all()
            
            logger.info(f"Found {len(prospects)} prospects needing follow-ups")
            
            sent_count = 0
            failed_count = 0
            errors = []
            
            # Send follow-up to each prospect
            for prospect in prospects:
                try:
                    logger.info(f"Sending follow-up #{prospect.followups_sent + 1} to {prospect.contact_email} for {prospect.domain}")
                    
                    # Compose follow-up email using Gemini
                    # Extract snippet from DataForSEO payload
                    page_snippet = None
                    if prospect.dataforseo_payload:
                        page_snippet = prospect.dataforseo_payload.get("description") or prospect.dataforseo_payload.get("snippet")
                    
                    # Compose follow-up email
                    followup_result = await gemini_client.compose_email(
                        domain=prospect.domain,
                        page_title=prospect.page_title,
                        page_url=prospect.page_url,
                        page_snippet=page_snippet
                    )
                    
                    if not followup_result.get("success"):
                        error_msg = followup_result.get("error", "Failed to compose follow-up")
                        logger.error(f"Failed to compose follow-up for {prospect.domain}: {error_msg}")
                        errors.append(f"{prospect.domain}: {error_msg}")
                        failed_count += 1
                        continue
                    
                    # Modify subject to indicate it's a follow-up
                    subject = followup_result.get("subject", "")
                    if not subject.startswith("Re:") and not subject.lower().startswith("follow-up"):
                        subject = f"Re: {subject}"
                    
                    body = followup_result.get("body", "")
                    
                    # Add follow-up context to body
                    followup_body = f"""Hello,

I wanted to follow up on my previous email about potential collaboration opportunities.

{body}

Looking forward to hearing from you.

Best regards"""
                    
                    # Send via Gmail
                    send_result = await gmail_client.send_email(
                        to_email=prospect.contact_email,
                        subject=subject,
                        body=followup_body
                    )
                    
                    if send_result.get("success"):
                        # Create email log
                        email_log = EmailLog(
                            prospect_id=prospect.id,
                            subject=subject,
                            body=followup_body,
                            response=send_result
                        )
                        db.add(email_log)
                        
                        # Update prospect
                        prospect.followups_sent += 1
                        prospect.last_sent = datetime.utcnow()
                        
                        sent_count += 1
                        logger.info(f"✅ Follow-up sent to {prospect.contact_email}")
                    else:
                        error_msg = send_result.get("error", "Unknown error")
                        logger.error(f"Failed to send follow-up to {prospect.contact_email}: {error_msg}")
                        errors.append(f"{prospect.domain}: {error_msg}")
                        failed_count += 1
                    
                    # Rate limiting
                    await asyncio.sleep(2)  # 2 seconds between follow-ups
                
                except Exception as e:
                    error_msg = f"Error sending follow-up to prospect {prospect.id}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    failed_count += 1
                    continue
            
            # Commit all changes
            await db.commit()
            
            # Update job status
            job.status = "completed"
            job.result = {
                "followups_sent": sent_count,
                "followups_failed": failed_count,
                "errors": errors[:10] if errors else []
            }
            await db.commit()
            
            logger.info(f"Follow-up job {job_id} completed: {sent_count} sent, {failed_count} failed")
            
            return {
                "success": True,
                "followups_sent": sent_count,
                "followups_failed": failed_count,
                "job_id": job_id
            }
        
        except Exception as e:
            logger.error(f"Error in follow-up job {job_id}: {str(e)}", exc_info=True)
            
            # Update job status to failed
            try:
                result = await db.execute(select(Job).where(Job.id == UUID(job_id)))
                job = result.scalar_one_or_none()
                if job:
                    job.status = "failed"
                    job.error_message = str(e)
                    await db.commit()
            except:
                pass
            
            return {"success": False, "error": str(e)}


def send_followups_task(job_id: str) -> Dict[str, Any]:
    """
    RQ task wrapper for sending follow-ups
    
    Args:
        job_id: UUID string of the job to process
    
    Returns:
        Dictionary with results
    """
    return asyncio.run(send_followups_async(job_id))

