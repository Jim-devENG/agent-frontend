"""
Scoring task - calculates and updates prospect scores
"""
import asyncio
import logging
from typing import Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
import os
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add backend directory to path
backend_path = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(backend_path))

from worker.services.scoring import ProspectScorer
from app.models.job import Job
from app.models.prospect import Prospect

load_dotenv()

logger = logging.getLogger(__name__)

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://art_outreach:art_outreach@localhost:5432/art_outreach")
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def score_prospects_async(job_id: str) -> Dict[str, Any]:
    """
    Async function to calculate and update prospect scores
    
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
            max_prospects = params.get("max_prospects", 1000)  # Limit if no IDs specified
            
            logger.info(f"Starting scoring job {job_id}")
            
            # Initialize scorer
            scorer = ProspectScorer()
            
            # Get prospects to score
            if prospect_ids:
                # Score specific prospects
                query = select(Prospect).where(
                    Prospect.id.in_([UUID(pid) for pid in prospect_ids])
                )
            else:
                # Score all prospects (or up to limit)
                query = select(Prospect).limit(max_prospects)
            
            result = await db.execute(query)
            prospects = result.scalars().all()
            
            logger.info(f"Found {len(prospects)} prospects to score")
            
            scored_count = 0
            errors = []
            
            # Score each prospect
            for prospect in prospects:
                try:
                    # Extract email confidence from Hunter.io payload
                    email_confidence = None
                    if prospect.hunter_payload and prospect.hunter_payload.get("emails"):
                        emails = prospect.hunter_payload["emails"]
                        if emails:
                            email_confidence = emails[0].get("confidence_score")
                    
                    # Calculate score
                    new_score = scorer.calculate_score(
                        domain_authority=float(prospect.da_est) if prospect.da_est else None,
                        has_email=bool(prospect.contact_email),
                        email_confidence=email_confidence,
                        page_title=prospect.page_title,
                        page_url=prospect.page_url,
                        categories=None,  # Can be extracted from dataforseo_payload if needed
                        dataforseo_payload=prospect.dataforseo_payload,
                        hunter_payload=prospect.hunter_payload
                    )
                    
                    # Update prospect score
                    old_score = prospect.score
                    prospect.score = new_score
                    
                    scored_count += 1
                    
                    if old_score != new_score:
                        logger.debug(f"Updated score for {prospect.domain}: {old_score} → {new_score}")
                
                except Exception as e:
                    error_msg = f"Error scoring prospect {prospect.id}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    continue
            
            # Commit all changes
            await db.commit()
            
            # Update job status
            job.status = "completed"
            job.result = {
                "prospects_scored": scored_count,
                "errors": errors[:10] if errors else []  # Include first 10 errors
            }
            await db.commit()
            
            logger.info(f"Scoring job {job_id} completed: {scored_count} prospects scored")
            
            return {
                "success": True,
                "prospects_scored": scored_count,
                "job_id": job_id
            }
        
        except Exception as e:
            logger.error(f"Error in scoring job {job_id}: {str(e)}", exc_info=True)
            
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


def score_prospects_task(job_id: str) -> Dict[str, Any]:
    """
    RQ task wrapper for prospect scoring
    
    Args:
        job_id: UUID string of the job to process
    
    Returns:
        Dictionary with results
    """
    return asyncio.run(score_prospects_async(job_id))

