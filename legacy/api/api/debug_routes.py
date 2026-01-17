"""
Debug routes to help diagnose scraping issues
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import ScrapedWebsite, Contact, ScrapingJob
from sqlalchemy import desc, func
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/debug/websites")
async def debug_websites(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Debug endpoint to see all websites in database"""
    websites = db.query(ScrapedWebsite).order_by(desc(ScrapedWebsite.created_at)).limit(limit).all()
    
    return {
        "total": len(websites),
        "websites": [
            {
                "id": w.id,
                "url": w.url,
                "title": w.title,
                "category": w.category,
                "status": w.status,
                "quality_score": w.quality_score,
                "meets_quality_threshold": w.meets_quality_threshold,
                "is_art_related": w.is_art_related,
                "created_at": w.created_at.isoformat() if w.created_at else None,
                "has_html": bool(w.raw_html),
                "html_length": len(w.raw_html) if w.raw_html else 0,
                "contact_count": len(w.contacts) if w.contacts else 0
            }
            for w in websites
        ]
    }


@router.get("/debug/contacts")
async def debug_contacts(
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Debug endpoint to see all contacts in database"""
    contacts = db.query(Contact).order_by(desc(Contact.created_at)).limit(limit).all()
    
    return {
        "total": len(contacts),
        "contacts": [
            {
                "id": c.id,
                "email": c.email,
                "phone": c.phone_number,
                "social_platform": c.social_platform,
                "social_url": c.social_url,
                "website_id": c.website_id,
                "website_url": c.website.url if c.website else None,
                "created_at": c.created_at.isoformat() if c.created_at else None
            }
            for c in contacts
        ]
    }


@router.get("/debug/jobs")
async def debug_jobs(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Debug endpoint to see recent jobs"""
    jobs = db.query(ScrapingJob).order_by(desc(ScrapingJob.created_at)).limit(limit).all()
    
    return {
        "total": len(jobs),
        "jobs": [
            {
                "id": j.id,
                "job_type": j.job_type,
                "status": j.status,
                "result": j.result,
                "error_message": j.error_message,
                "started_at": j.started_at.isoformat() if j.started_at else None,
                "completed_at": j.completed_at.isoformat() if j.completed_at else None,
                "created_at": j.created_at.isoformat() if j.created_at else None
            }
            for j in jobs
        ]
    }


@router.get("/debug/stats")
async def debug_stats(db: Session = Depends(get_db)):
    """Debug endpoint to see database statistics"""
    total_websites = db.query(ScrapedWebsite).count()
    websites_with_contacts = db.query(ScrapedWebsite).filter(
        ScrapedWebsite.contacts.any()
    ).count()
    websites_with_html = db.query(ScrapedWebsite).filter(
        ScrapedWebsite.raw_html.isnot(None),
        ScrapedWebsite.raw_html != ""
    ).count()
    websites_meeting_quality = db.query(ScrapedWebsite).filter(
        ScrapedWebsite.meets_quality_threshold == True
    ).count()
    websites_failed_quality = db.query(ScrapedWebsite).filter(
        ScrapedWebsite.meets_quality_threshold == False
    ).count()
    
    total_contacts = db.query(Contact).count()
    contacts_with_email = db.query(Contact).filter(Contact.email.isnot(None)).count()
    contacts_with_phone = db.query(Contact).filter(Contact.phone_number.isnot(None)).count()
    contacts_with_social = db.query(Contact).filter(Contact.social_platform.isnot(None)).count()
    
    # Status breakdown
    status_breakdown = db.query(
        ScrapedWebsite.status,
        func.count(ScrapedWebsite.id).label('count')
    ).group_by(ScrapedWebsite.status).all()
    
    # Category breakdown
    category_breakdown = db.query(
        ScrapedWebsite.category,
        func.count(ScrapedWebsite.id).label('count')
    ).group_by(ScrapedWebsite.category).all()
    
    return {
        "websites": {
            "total": total_websites,
            "with_contacts": websites_with_contacts,
            "with_html": websites_with_html,
            "meeting_quality": websites_meeting_quality,
            "failed_quality": websites_failed_quality,
            "status_breakdown": {s: c for s, c in status_breakdown},
            "category_breakdown": {c: count for c, count in category_breakdown if c}
        },
        "contacts": {
            "total": total_contacts,
            "with_email": contacts_with_email,
            "with_phone": contacts_with_phone,
            "with_social": contacts_with_social
        }
    }

