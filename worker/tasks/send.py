"""
Send task - processes email sending jobs
"""
import asyncio
import logging
from typing import Dict, Any, List
from uuid import UUID
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, and_
from datetime import datetime
import os
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add backend directory to path
backend_path = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(backend_path))

from worker.clients.gmail import GmailClient
from app.models.job import Job
from app.models.prospect import Prospect
from app.models.email_log import EmailLog

load_dotenv()

logger = logging.getLogger(__name__)

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://art_outreach:art_outreach@localhost:5432/art_outreach")
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def send_emails_async(job_id: str) -> Dict[str, Any]:
    """
    Async function to send emails for prospects
    
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
            prospect_ids = params.get("prospect_ids", [])  # Optional: specific prospects
            max_prospects = params.get("max_prospects", 100)  # Limit if no IDs specified
            auto_send = params.get("auto_send", False)  # Whether to send without review
            
            logger.info(f"Starting send job {job_id}")
            
            # Initialize Gmail client
            try:
                gmail_client = GmailClient()
            except ValueError as e:
                logger.error(f"Gmail client initialization failed: {e}")
                job.status = "failed"
                job.error_message = str(e)
                await db.commit()
                return {"success": False, "error": str(e)}
            
            # Get prospects to send to
            if prospect_ids:
                # Send to specific prospects
                query = select(Prospect).where(
                    and_(
                        Prospect.id.in_([UUID(pid) for pid in prospect_ids]),
                        Prospect.contact_email.isnot(None),
                        Prospect.outreach_status == "pending"  # Only pending prospects
                    )
                )
            else:
                # Send to prospects with emails and drafts, ordered by score
                query = select(Prospect).where(
                    and_(
                        Prospect.contact_email.isnot(None),
                        Prospect.draft_subject.isnot(None),
                        Prospect.draft_body.isnot(None),
                        Prospect.outreach_status == "pending"
                    )
                ).order_by(Prospect.score.desc()).limit(max_prospects)
            
            result = await db.execute(query)
            prospects = result.scalars().all()
            
            logger.info(f"Found {len(prospects)} prospects to send emails to")
            
            sent_count = 0
            failed_count = 0
            errors = []
            
            # Send email to each prospect
            for prospect in prospects:
                try:
                    # Check if we should send (auto_send or has draft)
                    if not auto_send and (not prospect.draft_subject or not prospect.draft_body):
                        logger.info(f"Skipping {prospect.domain}: no draft and auto_send=false")
                        continue
                    
                    subject = prospect.draft_subject or f"Partnership Opportunity - {prospect.domain}"
                    body = prospect.draft_body or f"Hello,\n\nI noticed your website {prospect.domain}..."
                    
                    logger.info(f"Sending email to {prospect.contact_email} for {prospect.domain}")
                    
                    # Send via Gmail
                    send_result = await gmail_client.send_email(
                        to_email=prospect.contact_email,
                        subject=subject,
                        body=body
                    )
                    
                    if send_result.get("success"):
                        # Create email log
                        email_log = EmailLog(
                            prospect_id=prospect.id,
                            subject=subject,
                            body=body,
                            response=send_result
                        )
                        db.add(email_log)
                        
                        # Update prospect
                        prospect.outreach_status = "sent"
                        prospect.last_sent = datetime.utcnow()
                        
                        sent_count += 1
                        logger.info(f"✅ Email sent to {prospect.contact_email}")
                    else:
                        error_msg = send_result.get("error", "Unknown error")
                        logger.error(f"Failed to send email to {prospect.contact_email}: {error_msg}")
                        errors.append(f"{prospect.domain}: {error_msg}")
                        failed_count += 1
                    
                    # Rate limiting - Gmail has sending limits
                    await asyncio.sleep(1)  # 1 second between sends
                
                except Exception as e:
                    error_msg = f"Error sending to prospect {prospect.id}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    failed_count += 1
                    continue
            
            # Commit all changes
            await db.commit()
            
            # Update job status
            job.status = "completed"
            job.result = {
                "emails_sent": sent_count,
                "emails_failed": failed_count,
                "errors": errors[:10] if errors else []  # Include first 10 errors
            }
            await db.commit()
            
            logger.info(f"Send job {job_id} completed: {sent_count} sent, {failed_count} failed")
            
            return {
                "success": True,
                "emails_sent": sent_count,
                "emails_failed": failed_count,
                "job_id": job_id
            }
        
        except Exception as e:
            logger.error(f"Error in send job {job_id}: {str(e)}", exc_info=True)
            
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


def send_emails_task(job_id: str) -> Dict[str, Any]:
    """
    RQ task wrapper for sending emails
    
    Args:
        job_id: UUID string of the job to process
    
    Returns:
        Dictionary with results
    """
    return asyncio.run(send_emails_async(job_id))

