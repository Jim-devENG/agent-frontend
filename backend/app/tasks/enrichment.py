"""
Enrichment task - finds emails for prospects using Hunter.io
Runs directly in backend (no external worker needed for free tier)
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.models.prospect import Prospect
from app.models.job import Job
from app.clients.hunter import HunterIOClient

logger = logging.getLogger(__name__)


async def process_enrichment_job(job_id: str) -> Dict[str, Any]:
    """
    Process enrichment job to find emails for prospects using Hunter.io
    
    Args:
        job_id: UUID of the job to process
        
    Returns:
        Dict with job results or error
    """
    async with AsyncSessionLocal() as db:
        try:
            # Get job
            from sqlalchemy import select
            result = await db.execute(select(Job).where(Job.id == job_id))
            job = result.scalar_one_or_none()
            
            if not job:
                logger.error(f"❌ Enrichment job {job_id} not found")
                return {"error": "Job not found"}
            
            job.status = "running"
            await db.commit()
            await db.refresh(job)
            
            logger.info(f"🔍 Starting enrichment job {job_id}...")
            
            # Get job parameters
            params = job.params or {}
            prospect_ids = params.get("prospect_ids")
            max_prospects = params.get("max_prospects", 100)
            
            # Build query for prospects without emails
            query = select(Prospect).where(
                Prospect.contact_email.is_(None),
                Prospect.outreach_status == "pending"
            )
            
            if prospect_ids:
                query = query.where(Prospect.id.in_([UUID(pid) for pid in prospect_ids]))
            
            query = query.limit(max_prospects)
            
            result = await db.execute(query)
            prospects = result.scalars().all()
            
            logger.info(f"🔍 Found {len(prospects)} prospects to enrich...")
            
            if len(prospects) == 0:
                job.status = "completed"
                job.result = {
                    "prospects_enriched": 0,
                    "prospects_failed": 0,
                    "total_processed": 0,
                    "message": "No prospects found without emails"
                }
                await db.commit()
                return {
                    "job_id": job_id,
                    "status": "completed",
                    "prospects_enriched": 0,
                    "message": "No prospects to enrich"
                }
            
            # Initialize Hunter client
            try:
                hunter_client = HunterIOClient()
            except ValueError as e:
                job.status = "failed"
                job.error_message = f"Hunter.io not configured: {e}"
                await db.commit()
                logger.error(f"❌ Hunter.io client initialization failed: {e}")
                return {"error": str(e)}
            
            enriched_count = 0
            failed_count = 0
            no_email_count = 0
            
            # Enrich each prospect with comprehensive logging
            import time
            enrichment_start_time = time.time()
            
            for idx, prospect in enumerate(prospects, 1):
                prospect_start_time = time.time()
                try:
                    domain = prospect.domain
                    prospect_id = str(prospect.id)
                    
                    logger.info(f"🔍 [ENRICHMENT] [{idx}/{len(prospects)}] Starting enrichment for {domain} (id: {prospect_id})")
                    logger.info(f"📥 [ENRICHMENT] Input - domain: {domain}, prospect_id: {prospect_id}")
                    
                    # Call Hunter.io with error handling
                    try:
                        hunter_result = await hunter_client.domain_search(domain)
                        hunter_time = (time.time() - prospect_start_time) * 1000
                        logger.info(f"⏱️  [ENRICHMENT] Hunter.io API call completed in {hunter_time:.0f}ms")
                    except Exception as hunter_err:
                        hunter_time = (time.time() - prospect_start_time) * 1000
                        logger.error(f"❌ [ENRICHMENT] Hunter.io API call failed after {hunter_time:.0f}ms: {hunter_err}", exc_info=True)
                        hunter_result = {"success": False, "error": str(hunter_err), "domain": domain}
                    
                    # Process Hunter.io response
                    if hunter_result.get("success") and hunter_result.get("emails"):
                        emails = hunter_result["emails"]
                        if emails and len(emails) > 0:
                            # Get best email (highest confidence)
                            best_email = None
                            best_confidence = 0
                            for email_data in emails:
                                confidence = email_data.get("confidence_score", 0)
                                if confidence > best_confidence:
                                    best_confidence = confidence
                                    best_email = email_data
                            
                            if best_email and best_email.get("value"):
                                email_value = best_email["value"]
                                prospect.contact_email = email_value
                                prospect.contact_method = "hunter_io"
                                prospect.hunter_payload = hunter_result
                                enriched_count += 1
                                total_time = (time.time() - prospect_start_time) * 1000
                                logger.info(f"✅ [ENRICHMENT] [{idx}/{len(prospects)}] Enriched {domain} in {total_time:.0f}ms")
                                logger.info(f"📤 [ENRICHMENT] Output - email: {email_value}, confidence: {best_confidence}, source: hunter_io")
                            else:
                                logger.warning(f"⚠️  [ENRICHMENT] [{idx}/{len(prospects)}] Email object missing 'value' for {domain}")
                                prospect.hunter_payload = hunter_result
                                no_email_count += 1
                        else:
                            logger.info(f"⚠️  [ENRICHMENT] [{idx}/{len(prospects)}] No emails in response for {domain}")
                            prospect.hunter_payload = hunter_result
                            no_email_count += 1
                    else:
                        error_msg = hunter_result.get('error', 'Unknown error')
                        logger.warning(f"❌ [ENRICHMENT] [{idx}/{len(prospects)}] Hunter.io failed for {domain}: {error_msg}")
                        prospect.hunter_payload = hunter_result
                        failed_count += 1
                    
                    await db.commit()
                    await db.refresh(prospect)
                    
                    # Rate limiting (1 request per second to respect Hunter.io limits)
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    total_time = (time.time() - prospect_start_time) * 1000
                    logger.error(f"❌ [ENRICHMENT] [{idx}/{len(prospects)}] Error enriching {prospect.domain} after {total_time:.0f}ms: {e}", exc_info=True)
                    logger.error(f"📤 [ENRICHMENT] Output - error: {str(e)}, stack_trace: {type(e).__name__}")
                    failed_count += 1
                    continue
            
            total_enrichment_time = (time.time() - enrichment_start_time) * 1000
            logger.info(f"⏱️  [ENRICHMENT] Total enrichment time: {total_enrichment_time:.0f}ms")
            
            # Update job status
            job.status = "completed"
            job.result = {
                "prospects_enriched": enriched_count,
                "prospects_failed": failed_count,
                "prospects_no_email": no_email_count,
                "total_processed": len(prospects)
            }
            await db.commit()
            
            logger.info(f"✅ Enrichment job {job_id} completed:")
            logger.info(f"   📊 Enriched: {enriched_count}, Failed: {failed_count}, No Email: {no_email_count}")
            
            return {
                "job_id": job_id,
                "status": "completed",
                "prospects_enriched": enriched_count,
                "prospects_failed": failed_count,
                "prospects_no_email": no_email_count,
                "total_processed": len(prospects)
            }
            
        except Exception as e:
            logger.error(f"❌ Enrichment job {job_id} failed: {e}", exc_info=True)
            try:
                result = await db.execute(select(Job).where(Job.id == job_id))
                job = result.scalar_one_or_none()
                if job:
                    job.status = "failed"
                    job.error_message = str(e)
                    await db.commit()
            except:
                pass
            return {"error": str(e)}

