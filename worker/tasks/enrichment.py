"""
Enrichment task - processes prospect enrichment jobs using Hunter.io
"""
import asyncio
import logging
from typing import Dict, Any, List
from uuid import UUID
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, and_
import os
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add backend directory to path
backend_path = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(backend_path))

from worker.clients.hunter import HunterIOClient
from app.models.job import Job
from app.models.prospect import Prospect

load_dotenv()

logger = logging.getLogger(__name__)

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://art_outreach:art_outreach@localhost:5432/art_outreach")
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def enrich_prospects_async(job_id: str) -> Dict[str, Any]:
    """
    Async function to enrich prospects with email data from Hunter.io
    
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
            
            logger.info(f"Starting enrichment job {job_id}")
            
            # Initialize Hunter.io client
            try:
                client = HunterIOClient()
            except ValueError as e:
                logger.error(f"Hunter.io client initialization failed: {e}")
                job.status = "failed"
                job.error_message = str(e)
                await db.commit()
                return {"success": False, "error": str(e)}
            
            # Get prospects to enrich
            if prospect_ids:
                # Enrich specific prospects
                query = select(Prospect).where(
                    and_(
                        Prospect.id.in_([UUID(pid) for pid in prospect_ids]),
                        Prospect.contact_email.is_(None)  # Only those without emails
                    )
                )
            else:
                # Enrich prospects without emails, ordered by score
                query = select(Prospect).where(
                    Prospect.contact_email.is_(None)
                ).order_by(Prospect.score.desc()).limit(max_prospects)
            
            result = await db.execute(query)
            prospects = result.scalars().all()
            
            logger.info(f"Found {len(prospects)} prospects to enrich")
            
            enriched_count = 0
            emails_found = 0
            errors = []
            
            # Enrich each prospect
            for prospect in prospects:
                try:
                    domain = prospect.domain
                    if not domain:
                        logger.warning(f"Prospect {prospect.id} has no domain, skipping")
                        continue
                    
                    logger.info(f"Enriching prospect {prospect.id} for domain: {domain}")
                    
                    # Call Hunter.io
                    hunter_result = await client.domain_search(domain, limit=10)
                    
                    # Save Hunter.io payload
                    prospect.hunter_payload = hunter_result
                    
                    if hunter_result.get("success") and hunter_result.get("emails"):
                        emails = hunter_result["emails"]
                        
                        # Use the highest confidence email
                        best_email = None
                        best_confidence = 0
                        
                        for email_data in emails:
                            confidence = email_data.get("confidence_score", 0)
                            if confidence > best_confidence:
                                best_confidence = confidence
                                best_email = email_data
                        
                        if best_email and best_email.get("value"):
                            prospect.contact_email = best_email["value"]
                            prospect.contact_method = "hunter_io"
                            emails_found += 1
                            logger.info(f"✅ Found email for {domain}: {best_email['value']} (confidence: {best_confidence})")
                        else:
                            logger.info(f"No valid email found for {domain}")
                    else:
                        error_msg = hunter_result.get("error") or hunter_result.get("message", "No emails found")
                        logger.info(f"No emails found for {domain}: {error_msg}")
                    
                    enriched_count += 1
                    
                    # Rate limiting - Hunter.io has API limits
                    await asyncio.sleep(1)  # 1 second between requests
                
                except Exception as e:
                    error_msg = f"Error enriching prospect {prospect.id}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    continue
            
            # Commit all changes
            await db.commit()
            
            # Update job status
            job.status = "completed"
            job.result = {
                "prospects_enriched": enriched_count,
                "emails_found": emails_found,
                "errors": errors[:10] if errors else []  # Include first 10 errors
            }
            await db.commit()
            
            logger.info(f"Enrichment job {job_id} completed: {emails_found} emails found for {enriched_count} prospects")
            
            return {
                "success": True,
                "prospects_enriched": enriched_count,
                "emails_found": emails_found,
                "job_id": job_id
            }
        
        except Exception as e:
            logger.error(f"Error in enrichment job {job_id}: {str(e)}", exc_info=True)
            
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


def enrich_prospects_task(job_id: str) -> Dict[str, Any]:
    """
    RQ task wrapper for prospect enrichment
    
    Args:
        job_id: UUID string of the job to process
    
    Returns:
        Dictionary with results
    """
    return asyncio.run(enrich_prospects_async(job_id))

