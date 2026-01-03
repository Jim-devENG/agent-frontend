"""
Social Outreach Pipeline API

REUSES Website Outreach Pipeline - filters by source_type='social'.
Stage-based progression for social media outreach.

Pipeline Stages (same as website):
1. Discovery - Always unlocked
2. Profile Review - Unlocked when discovered_count > 0
3. Drafting - Unlocked when qualified_count > 0
4. Sending - Unlocked when drafted_count > 0
5. Follow-ups - Unlocked when sent_count > 0

All queries filter: source_type='social'
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone, timedelta
import logging
from pydantic import BaseModel

from app.db.database import get_db
from app.api.auth import get_current_user_optional
from app.models.prospect import Prospect, DiscoveryStatus
from app.adapters.social_discovery import (
    LinkedInDiscoveryAdapter,
    InstagramDiscoveryAdapter,
    TikTokDiscoveryAdapter,
    FacebookDiscoveryAdapter
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/social/pipeline", tags=["social-pipeline"])


# ============================================
# PIPELINE STATUS
# ============================================

@router.get("/status")
async def get_social_pipeline_status(
    platform: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[str] = Depends(get_current_user_optional)
):
    """
    Get social pipeline status.
    
    REUSES prospects table - filters by source_type='social'.
    Same pipeline stages as website outreach.
    
    Returns:
        {
            "discovered": int,      # discovery_status = 'DISCOVERED' AND source_type='social'
            "reviewed": int,        # approval_status = 'approved' AND source_type='social'
            "qualified": int,       # scrape_status = 'SCRAPED' AND source_type='social'
            "drafted": int,         # draft_status = 'drafted' AND source_type='social'
            "sent": int,            # send_status = 'sent' AND source_type='social'
            "followup_ready": int,  # sent AND last_sent < threshold AND source_type='social'
        }
    """
    # CRITICAL: Wrap entire function to prevent ANY 500 errors
    # Always return 200 with status="inactive" if schema is missing
    try:
        # CRITICAL: Check if source_type column exists
        # If migration hasn't run, return empty status instead of crashing
        column_exists = False
        try:
            from sqlalchemy import text
            # Check if column exists using raw SQL
            column_check = await db.execute(
                text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'prospects' 
                    AND column_name = 'source_type'
                """)
            )
            column_exists = column_check.fetchone() is not None
        except Exception as check_err:
            # If checking for column fails, assume it doesn't exist
            logger.warning(f"⚠️  [SOCIAL PIPELINE] Could not check for source_type column: {check_err}")
            column_exists = False
        
        if not column_exists:
            logger.warning("⚠️  [SOCIAL PIPELINE] source_type column does not exist - migration not applied")
            logger.warning("⚠️  [SOCIAL PIPELINE] Returning empty status - migration add_social_columns_to_prospects needs to run")
            return {
                "discovered": 0,
                "reviewed": 0,
                "qualified": 0,
                "drafted": 0,
                "sent": 0,
                "followup_ready": 0,
                "status": "inactive",
                "message": "Social outreach columns not initialized. Please run migration: alembic upgrade head"
            }
        
        # Base filter: only social prospects
        # Wrap in try-catch in case the column access itself fails
        try:
            social_filter = Prospect.source_type == 'social'
            
            # Add platform filter if specified
            if platform:
                platform_lower = platform.lower()
                valid_platforms = ['linkedin', 'instagram', 'facebook', 'tiktok']
                if platform_lower not in valid_platforms:
                    return {
                        "discovered": 0,
                        "reviewed": 0,
                        "qualified": 0,
                        "drafted": 0,
                        "sent": 0,
                        "followup_ready": 0,
                        "status": "inactive",
                        "message": f"Invalid platform: {platform}"
                    }
                social_filter = and_(social_filter, Prospect.source_platform == platform_lower)
        except Exception as filter_err:
            # If accessing source_type fails, return safe response
            logger.error(f"❌ [SOCIAL PIPELINE] Error accessing source_type column: {filter_err}")
            return {
                "discovered": 0,
                "reviewed": 0,
                "qualified": 0,
                "drafted": 0,
                "sent": 0,
                "followup_ready": 0,
                "status": "inactive",
                "message": "Social outreach columns not initialized. Please run migration: alembic upgrade head"
            }
        
        # Count discovered profiles
        discovered_result = await db.execute(
            select(func.count(Prospect.id)).where(
                and_(
                    social_filter,
                    Prospect.discovery_status == DiscoveryStatus.DISCOVERED.value
                )
            )
        )
        discovered_count = discovered_result.scalar() or 0
        
        # Count reviewed/approved profiles
        reviewed_result = await db.execute(
            select(func.count(Prospect.id)).where(
                and_(
                    social_filter,
                    Prospect.approval_status == 'approved'
                )
            )
        )
        reviewed_count = reviewed_result.scalar() or 0
        
        # Count qualified profiles (scraped with emails or enriched)
        qualified_result = await db.execute(
            select(func.count(Prospect.id)).where(
                and_(
                    social_filter,
                    Prospect.scrape_status.in_(['SCRAPED', 'ENRICHED'])
                )
            )
        )
        qualified_count = qualified_result.scalar() or 0
        
        # Count drafted profiles
        drafted_result = await db.execute(
            select(func.count(Prospect.id)).where(
                and_(
                    social_filter,
                    Prospect.draft_status == 'drafted'
                )
            )
        )
        drafted_count = drafted_result.scalar() or 0
        
        # Count sent profiles
        sent_result = await db.execute(
            select(func.count(Prospect.id)).where(
                and_(
                    social_filter,
                    Prospect.send_status == 'sent'
                )
            )
        )
        sent_count = sent_result.scalar() or 0
        
        # Count follow-up ready profiles (sent AND last_sent > 7 days ago or NULL)
        followup_threshold = datetime.now(timezone.utc) - timedelta(days=7)
        followup_ready_result = await db.execute(
            select(func.count(Prospect.id)).where(
                and_(
                    social_filter,
                    Prospect.send_status == 'sent',
                    or_(
                        Prospect.last_sent.is_(None),
                        Prospect.last_sent < followup_threshold
                    )
                )
            )
        )
        followup_ready_count = followup_ready_result.scalar() or 0
        
        logger.info(
            f"📊 [SOCIAL PIPELINE] Status: "
            f"discovered={discovered_count}, reviewed={reviewed_count}, "
            f"qualified={qualified_count}, drafted={drafted_count}, "
            f"sent={sent_count}, followup_ready={followup_ready_count}"
        )
        
        return {
            "discovered": discovered_count,
            "reviewed": reviewed_count,
            "qualified": qualified_count,
            "drafted": drafted_count,
            "sent": sent_count,
            "followup_ready": followup_ready_count,
            "status": "active"
        }
        
    except Exception as e:
        # CRITICAL: Never return 500 - always return safe response
        # Check if error is related to missing column
        error_str = str(e).lower()
        if 'source_type' in error_str or 'column' in error_str or 'does not exist' in error_str or 'undefinedcolumn' in error_str:
            logger.warning(f"⚠️  [SOCIAL PIPELINE] Database schema error (likely missing columns): {e}")
            logger.warning("⚠️  [SOCIAL PIPELINE] Returning safe empty status instead of 500")
            return {
                "discovered": 0,
                "reviewed": 0,
                "qualified": 0,
                "drafted": 0,
                "sent": 0,
                "followup_ready": 0,
                "status": "inactive",
                "message": "Social outreach columns not initialized. Please run migration: alembic upgrade head"
            }
        else:
            # For other errors, still return safe response but log the error
            logger.error(f"❌ [SOCIAL PIPELINE] Unexpected error computing status: {e}", exc_info=True)
            return {
                "discovered": 0,
                "reviewed": 0,
                "qualified": 0,
                "drafted": 0,
                "sent": 0,
                "followup_ready": 0,
                "status": "inactive",
                "message": f"Error computing pipeline status: {str(e)}"
            }


# ============================================
# STAGE 1: DISCOVERY
# ============================================

class SocialDiscoveryRequest(BaseModel):
    platform: str  # linkedin, facebook, instagram, tiktok
    categories: List[str]
    locations: List[str]
    keywords: List[str] = []
    parameters: dict = {}  # Platform-specific parameters
    max_results: Optional[int] = 100


class SocialDiscoveryResponse(BaseModel):
    success: bool
    job_id: UUID
    message: str
    profiles_count: int


@router.post("/discover", response_model=SocialDiscoveryResponse)
async def discover_profiles(
    request: SocialDiscoveryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[str] = Depends(get_current_user_optional)
):
    """
    STAGE 1: Discover social profiles using adapter pattern.
    
    Always unlocked - this is the entry point.
    Uses platform-specific adapters to normalize results into Prospect objects.
    """
    # Validate platform
    platform = request.platform.lower()
    valid_platforms = ['linkedin', 'instagram', 'facebook', 'tiktok']
    if platform not in valid_platforms:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid platform. Must be one of: {valid_platforms}"
        )
    
    # Validate required fields
    if not request.categories:
        raise HTTPException(status_code=400, detail="At least one category is required")
    if not request.locations:
        raise HTTPException(status_code=400, detail="At least one location is required")
    
    logger.info(f"🔍 [SOCIAL PIPELINE STAGE 1] Discovery request for {platform}")
    
    try:
        # Select adapter based on platform
        adapter_map = {
            'linkedin': LinkedInDiscoveryAdapter(),
            'instagram': InstagramDiscoveryAdapter(),
            'facebook': FacebookDiscoveryAdapter(),
            'tiktok': TikTokDiscoveryAdapter(),
        }
        
        adapter = adapter_map[platform]
        
        # Prepare adapter parameters (platform-specific)
        adapter_params = {
            'categories': request.categories,
            'locations': request.locations,
            'keywords': request.keywords,
            'max_results': request.max_results or 100,
            **request.parameters  # Platform-specific parameters
        }
        
        # Run discovery using adapter
        prospects = await adapter.discover(adapter_params, db)
        
        # Save prospects to database
        for prospect in prospects:
            # Ensure source_type is set
            prospect.source_type = 'social'
            prospect.source_platform = platform
            prospect.discovery_status = DiscoveryStatus.DISCOVERED.value
            prospect.approval_status = 'PENDING'
            prospect.scrape_status = 'DISCOVERED'
            db.add(prospect)
        
        await db.commit()
        
        logger.info(f"✅ [SOCIAL PIPELINE STAGE 1] Discovered {len(prospects)} profiles for {platform}")
        
        # Create a job record (using existing Job model for consistency)
        from app.models import Job
        job = Job(
            job_type="social_discover",
            params={
                "platform": platform,
                "categories": request.categories,
                "locations": request.locations,
                "keywords": request.keywords,
                "prospects_count": len(prospects),
                **request.parameters
            },
            status="completed",
            result={"prospects_count": len(prospects)}
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)
        
        return SocialDiscoveryResponse(
            success=True,
            job_id=job.id,
            message=f"Discovered {len(prospects)} profiles for {platform}",
            profiles_count=len(prospects)
        )
        
    except Exception as e:
        logger.error(f"❌ [SOCIAL PIPELINE STAGE 1] Error: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to discover profiles: {str(e)}")


# ============================================
# STAGE 2: PROFILE REVIEW
# ============================================

class ProfileReviewRequest(BaseModel):
    profile_ids: List[UUID]
    action: str  # "qualify" or "reject"


@router.post("/review")
async def review_profiles(
    request: ProfileReviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[str] = Depends(get_current_user_optional)
):
    """
    STAGE 2: Review and approve/reject social profiles.
    
    REUSES website approval logic - filters by source_type='social'.
    Unlocked when discovered_count > 0.
    """
    if request.action not in ["qualify", "reject"]:
        raise HTTPException(status_code=400, detail="Action must be 'qualify' or 'reject'")
    
    if not request.profile_ids:
        raise HTTPException(status_code=400, detail="At least one profile ID is required")
    
    logger.info(f"📋 [SOCIAL PIPELINE STAGE 2] Reviewing {len(request.profile_ids)} profiles: {request.action}")
    
    try:
        # Get social prospects
        result = await db.execute(
            select(Prospect).where(
                and_(
                    Prospect.id.in_(request.profile_ids),
                    Prospect.source_type == 'social'
                )
            )
        )
        prospects = result.scalars().all()
        
        if len(prospects) != len(request.profile_ids):
            logger.warning(f"⚠️  Only found {len(prospects)} of {len(request.profile_ids)} requested profiles")
        
        updated_count = 0
        
        # Map action to approval_status (reuse website logic)
        if request.action == "qualify":
            # Qualify = approve (same as website outreach)
            for prospect in prospects:
                prospect.approval_status = "approved"
                updated_count += 1
        else:
            # Reject = rejected
            for prospect in prospects:
                prospect.approval_status = "rejected"
                updated_count += 1
        
        await db.commit()
        
        logger.info(f"✅ [SOCIAL PIPELINE STAGE 2] Updated {updated_count} profiles: {request.action}")
        
        return {
            "success": True,
            "updated": updated_count,
            "action": request.action,
            "message": f"Updated {updated_count} profile(s) - {request.action}"
        }
        
    except Exception as e:
        logger.error(f"❌ [SOCIAL PIPELINE STAGE 2] Error: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to review profiles: {str(e)}")


# ============================================
# STAGE 3: DRAFTING
# ============================================

class DraftRequest(BaseModel):
    profile_ids: List[UUID]
    is_followup: bool = False


@router.post("/draft")
async def create_drafts(
    request: DraftRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[str] = Depends(get_current_user_optional)
):
    """
    STAGE 3: Create drafts for social profiles.
    
    REUSES website drafting logic - filters by source_type='social'.
    Unlocked when qualified_count > 0.
    Drafts are saved to prospect.draft_body and prospect.draft_subject.
    """
    if not request.profile_ids:
        raise HTTPException(status_code=400, detail="At least one profile ID is required")
    
    logger.info(f"📝 [SOCIAL PIPELINE STAGE 3] Creating drafts for {len(request.profile_ids)} profiles")
    
    try:
        # Get approved social prospects (reuse website approval logic)
        result = await db.execute(
            select(Prospect).where(
                and_(
                    Prospect.id.in_(request.profile_ids),
                    Prospect.source_type == 'social',
                    Prospect.approval_status == 'approved'
                )
            )
        )
        prospects = result.scalars().all()
        
        if len(prospects) == 0:
            raise HTTPException(
                status_code=400,
                detail="No approved social profiles found. Profiles must be approved before drafting."
            )
        
        # Reuse website drafting task
        # Create a job for drafting
        from app.models import Job
        job = Job(
            job_type="social_draft",
            params={
                "prospect_ids": [str(p.id) for p in prospects],
                "is_followup": request.is_followup,
                "pipeline_mode": True
            },
            status="pending"
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)
        
        # Start drafting task (reuse existing drafting logic)
        from app.tasks.drafting import draft_prospects_async
        import asyncio
        from app.task_manager import register_task
        
        task = asyncio.create_task(draft_prospects_async(str(job.id)))
        register_task(str(job.id), task)
        
        logger.info(f"✅ [SOCIAL PIPELINE STAGE 3] Drafting job {job.id} started for {len(prospects)} profiles")
        
        return {
            "success": True,
            "job_id": job.id,
            "drafts_created": 0,  # Will be updated by task
            "message": f"Drafting job started for {len(prospects)} profiles"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [SOCIAL PIPELINE STAGE 3] Error: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create drafts: {str(e)}")


# ============================================
# STAGE 4: SENDING
# ============================================

class SendRequest(BaseModel):
    profile_ids: List[UUID]


@router.post("/send")
async def send_messages(
    request: SendRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[str] = Depends(get_current_user_optional)
):
    """
    STAGE 4: Send messages to social profiles.
    
    REUSES website sending logic - filters by source_type='social'.
    Unlocked when drafted_count > 0.
    Requires draft to exist (draft_subject and draft_body).
    """
    if not request.profile_ids:
        raise HTTPException(status_code=400, detail="At least one profile ID is required")
    
    logger.info(f"📧 [SOCIAL PIPELINE STAGE 4] Sending messages to {len(request.profile_ids)} profiles")
    
    try:
        # Get drafted social prospects (reuse website logic)
        result = await db.execute(
            select(Prospect).where(
                and_(
                    Prospect.id.in_(request.profile_ids),
                    Prospect.source_type == 'social',
                    Prospect.draft_status == 'drafted',
                    Prospect.draft_subject.isnot(None),
                    Prospect.draft_body.isnot(None)
                )
            )
        )
        prospects = result.scalars().all()
        
        if len(prospects) == 0:
            raise HTTPException(
                status_code=400,
                detail="No drafted social profiles found. Profiles must be drafted before sending."
            )
        
        # Reuse website sending task
        from app.models import Job
        job = Job(
            job_type="social_send",
            params={
                "prospect_ids": [str(p.id) for p in prospects],
                "pipeline_mode": True
            },
            status="pending"
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)
        
        # Start sending task (reuse existing sending logic)
        from app.tasks.send import process_send_job
        import asyncio
        from app.task_manager import register_task
        
        task = asyncio.create_task(process_send_job(str(job.id)))
        register_task(str(job.id), task)
        
        logger.info(f"✅ [SOCIAL PIPELINE STAGE 4] Sending job {job.id} started for {len(prospects)} profiles")
        
        return {
            "success": True,
            "job_id": job.id,
            "messages_sent": 0,  # Will be updated by task
            "message": f"Sending job started for {len(prospects)} profiles"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [SOCIAL PIPELINE STAGE 4] Error: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to send messages: {str(e)}")


# ============================================
# STAGE 5: FOLLOW-UPS
# ============================================

@router.post("/followup")
async def create_followups(
    request: DraftRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[str] = Depends(get_current_user_optional)
):
    """
    STAGE 5: Create follow-up drafts for social profiles that have sent messages.
    
    REUSES website follow-up logic - filters by source_type='social'.
    Unlocked when sent_count > 0.
    Automatically generates follow-up using Gemini (reuses website drafting).
    """
    if not request.profile_ids:
        raise HTTPException(status_code=400, detail="At least one profile ID is required")
    
    logger.info(f"🔄 [SOCIAL PIPELINE STAGE 5] Creating follow-ups for {len(request.profile_ids)} profiles")
    
    try:
        # Get sent social prospects (reuse website logic)
        result = await db.execute(
            select(Prospect).where(
                and_(
                    Prospect.id.in_(request.profile_ids),
                    Prospect.source_type == 'social',
                    Prospect.send_status == 'sent',
                    Prospect.last_sent.isnot(None)
                )
            )
        )
        prospects = result.scalars().all()
        
        if len(prospects) == 0:
            raise HTTPException(
                status_code=400,
                detail="No sent social profiles found. Profiles must have sent messages before follow-ups."
            )
        
        # Reuse website drafting task with is_followup=True
        from app.models import Job
        job = Job(
            job_type="social_draft",
            params={
                "prospect_ids": [str(p.id) for p in prospects],
                "is_followup": True,
                "pipeline_mode": True
            },
            status="pending"
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)
        
        # Start drafting task (reuse existing drafting logic with follow-up mode)
        from app.tasks.drafting import draft_prospects_async
        import asyncio
        from app.task_manager import register_task
        
        task = asyncio.create_task(draft_prospects_async(str(job.id)))
        register_task(str(job.id), task)
        
        logger.info(f"✅ [SOCIAL PIPELINE STAGE 5] Follow-up drafting job {job.id} started for {len(prospects)} profiles")
        
        return {
            "success": True,
            "job_id": job.id,
            "followups_created": 0,  # Will be updated by task
            "message": f"Follow-up drafting job started for {len(prospects)} profiles"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [SOCIAL PIPELINE STAGE 5] Error: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create follow-ups: {str(e)}")

