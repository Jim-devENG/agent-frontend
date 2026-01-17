"""
Celery configuration for background tasks
"""
from celery import Celery
from utils.config import settings

# Create Celery app
celery_app = Celery(
    "art_outreach_scraper",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)


@celery_app.task(name='scrape_website')
def scrape_website_task(url: str):
    """
    Celery task for scraping a website
    
    Args:
        url: URL to scrape
        
    Returns:
        Scraped data
    """
    from scraper.website_scraper import WebsiteScraper
    scraper = WebsiteScraper()
    return scraper.scrape(url)


@celery_app.task(name='extract_contacts')
def extract_contacts_task(html_content: str):
    """
    Celery task for extracting contacts from HTML
    
    Args:
        html_content: HTML content to extract from
        
    Returns:
        Extracted contacts
    """
    from extractor.contact_extractor import ContactExtractor
    extractor = ContactExtractor()
    return extractor.extract_all(html_content)


@celery_app.task(name='generate_email')
def generate_email_task(artist_name: str, website_url: str, website_type: str, context: dict = None):
    """
    Celery task for generating outreach email
    
    Args:
        artist_name: Name of artist
        website_url: Website URL
        website_type: Type of website
        context: Additional context
        
    Returns:
        Generated email (subject and body)
    """
    from ai.email_generator import EmailGenerator
    generator = EmailGenerator()
    return generator.generate(artist_name, website_url, website_type, context)


@celery_app.task(name='send_email')
def send_email_task(to_email: str, subject: str, body: str):
    """
    Celery task for sending email
    
    Args:
        to_email: Recipient email
        subject: Email subject
        body: Email body
        
    Returns:
        Send result
    """
    from emailer.email_sender import EmailSender
    sender = EmailSender()
    return sender.send(to_email, subject, body)

