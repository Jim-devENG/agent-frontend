"""
FastAPI routes for the Autonomous Art Outreach Scraper
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from pydantic import BaseModel, HttpUrl, ConfigDict

from db.database import get_db
from db.models import ScrapedWebsite, Contact, OutreachEmail, ScrapingJob
from ai.email_generator import EmailGenerator

router = APIRouter()


# Pydantic models for request/response
class ScrapeRequest(BaseModel):
    url: HttpUrl
    website_type: Optional[str] = None


class ScrapeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    url: str
    domain: Optional[str]
    title: Optional[str]
    description: Optional[str]
    website_type: Optional[str]
    category: Optional[str]
    is_art_related: Optional[bool]
    domain_authority: Optional[int]
    quality_score: Optional[int]
    estimated_traffic: Optional[Dict]
    ssl_valid: Optional[bool]
    meets_quality_threshold: Optional[bool]
    status: str


class ContactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: Optional[str]
    phone_number: Optional[str]
    social_platform: Optional[str]
    social_url: Optional[str]
    contact_page_url: Optional[str]
    name: Optional[str]


class EmailRequest(BaseModel):
    website_id: int
    contact_id: Optional[int] = None
    recipient_email: str
    subject: str
    body: str


class EmailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    subject: str
    recipient_email: str
    status: str


# Routes
@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_website(
    request: ScrapeRequest,
    background_tasks: BackgroundTasks,
    skip_quality_check: bool = False,
    db: Session = Depends(get_db)
):
    """
    Scrape a website and store results
    
    Query params:
    - skip_quality_check: Set to true to bypass quality filtering
    """
    from scraper.scraper_service import ScraperService
    
    scraper_service = ScraperService(db)
    website = scraper_service.scrape_website(
        str(request.url),
        skip_quality_check=skip_quality_check
    )
    
    if not website:
        raise HTTPException(
            status_code=400,
            detail="Failed to scrape website or website does not meet quality requirements. "
                   "Check logs for details. Use skip_quality_check=true to bypass quality filter."
        )
    
    # Note: Contact extraction is now automatic in scrape_website()
    # No need to extract separately here
    
    return website


@router.get("/websites", response_model=List[ScrapeResponse])
async def list_websites(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all scraped websites"""
    websites = db.query(ScrapedWebsite).offset(skip).limit(limit).all()
    return websites


@router.get("/websites/{website_id}/contacts", response_model=List[ContactResponse])
async def get_website_contacts(
    website_id: int,
    db: Session = Depends(get_db)
):
    """Get contacts for a specific website"""
    contacts = db.query(Contact).filter(Contact.website_id == website_id).all()
    return contacts


@router.post("/websites/{website_id}/extract-contacts")
async def extract_contacts(
    website_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Manually trigger contact extraction for a website"""
    from extractor.contact_extraction_service import ContactExtractionService
    
    website = db.query(ScrapedWebsite).filter(ScrapedWebsite.id == website_id).first()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")
    
    # Use background task for extraction
    background_tasks.add_task(extract_contacts_for_website, website_id, db)
    
    return {
        "message": "Contact extraction started",
        "website_id": website_id,
        "status": "processing"
    }


@router.post("/scrape/social", response_model=ScrapeResponse)
async def scrape_social_media(
    username: str,
    platform: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Scrape a social media profile and store results"""
    from scraper.scraper_service import ScraperService
    
    valid_platforms = ["instagram", "tiktok", "behance", "pinterest"]
    if platform.lower() not in valid_platforms:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid platform. Must be one of: {', '.join(valid_platforms)}"
        )
    
    scraper_service = ScraperService(db)
    website = scraper_service.scrape_social_media(username, platform.lower())
    
    if not website:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to scrape {platform} profile {username}. Check logs for details."
        )
    
    # Extract contacts in background
    background_tasks.add_task(extract_contacts_for_website, website.id, db)
    
    return website


@router.post("/emails/generate")
async def generate_email(
    website_id: int,
    contact_id: Optional[int] = None,
    provider: Optional[str] = None,
    use_ai: bool = Query(True, description="Use AI (True) or templates (False)"),
    template_name: Optional[str] = Query(None, description="Specific template name to use (if use_ai=False)"),
    db: Session = Depends(get_db)
):
    """
    Generate an outreach email using AI or templates based on website/social context
    
    Email format is determined by:
    - Website category (art_gallery, interior_decor, home_tech, etc.)
    - Social media platform (if contact has social links)
    - Website description and metadata
    - Custom templates (if template_name is provided)
    
    Query params:
    - use_ai: Use AI generation (True) or template-based (False)
    - template_name: Specific template name to use (if use_ai=False)
    - provider: 'openai' or 'gemini' (only if use_ai=True)
    """
    website = db.query(ScrapedWebsite).filter(ScrapedWebsite.id == website_id).first()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")
    
    contact = None
    if contact_id:
        contact = db.query(Contact).filter(Contact.id == contact_id).first()
    
    generator = EmailGenerator(db=db)
    
    # Use the new method that adapts based on website/social context
    email_data = generator.generate_from_website(
        website=website,
        contact=contact,
        use_ai=use_ai,
        provider=provider
    )
    
    return {
        **email_data,
        "website_id": website_id,
        "contact_id": contact_id,
        "method": "ai" if use_ai else "template",
        "category": website.category,
        "social_platform": contact.social_platform if contact else None
    }


@router.post("/emails/send", response_model=EmailResponse)
async def send_email(
    request: EmailRequest,
    use_gmail: bool = True,
    use_html: bool = True,
    db: Session = Depends(get_db)
):
    """
    Send an outreach email with retry logic and database logging
    
    Query params:
    - use_gmail: Use Gmail API (True) or SMTP (False)
    - use_html: Send HTML formatted email (True) or plain text (False)
    """
    from emailer.outreach_email_sender import OutreachEmailSender
    
    website = db.query(ScrapedWebsite).filter(ScrapedWebsite.id == request.website_id).first()
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")
    
    sender = OutreachEmailSender(db, use_gmail=use_gmail)
    
    result = sender.send_outreach_email(
        to_email=request.recipient_email,
        subject=request.subject,
        body=request.body,
        website_id=request.website_id,
        contact_id=request.contact_id,
        use_html=use_html,
        business_name=website.title
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Failed to send email after retries")
        )
    
    # Get the email record from database
    email = db.query(OutreachEmail).filter(OutreachEmail.id == result["email_id"]).first()
    
    return email


@router.get("/emails", response_model=List[EmailResponse])
async def list_emails(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all sent emails"""
    emails = db.query(OutreachEmail).offset(skip).limit(limit).all()
    return emails


# Helper functions
def extract_contacts_for_website(website_id: int, db: Session):
    """Extract contacts for a website (background task)"""
    from extractor.contact_extraction_service import ContactExtractionService
    
    website = db.query(ScrapedWebsite).filter(ScrapedWebsite.id == website_id).first()
    if not website:
        return
    
    # Use raw HTML if available, otherwise fetch again
    if website.raw_html:
        html_content = website.raw_html
    else:
        from scraper.website_scraper import WebsiteScraper
        scraper = WebsiteScraper()
        soup, raw_html = scraper.fetch_page(website.url)
        html_content = raw_html or ""
    
    if html_content:
        service = ContactExtractionService(db)
        service.extract_and_save(website_id, html_content, website.url)

