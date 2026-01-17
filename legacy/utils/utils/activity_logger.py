"""
Activity logger for real-time activity tracking
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from db.models import ActivityLog, ScrapedWebsite, ScrapingJob
import logging

logger = logging.getLogger(__name__)


class ActivityLogger:
    """Logs activities for real-time dashboard updates"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log(
        self,
        activity_type: str,
        message: str,
        status: str = "info",
        website_id: Optional[int] = None,
        job_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log an activity
        
        Args:
            activity_type: Type of activity (scrape, extract, email, job)
            message: Activity message
            status: Status (info, success, warning, error)
            website_id: Related website ID
            job_id: Related job ID
            metadata: Additional metadata
        """
        try:
            activity = ActivityLog(
                activity_type=activity_type,
                message=message,
                status=status,
                website_id=website_id,
                job_id=job_id,
                extra_data=metadata or {}
            )
            self.db.add(activity)
            self.db.commit()
            logger.info(f"[{activity_type}] {message}")
        except Exception as e:
            logger.error(f"Failed to log activity: {e}")
            self.db.rollback()
    
    def log_scrape_start(self, url: str, website_id: Optional[int] = None):
        """Log scraping start"""
        self.log(
            activity_type="scrape",
            message=f"Starting to scrape: {url}",
            status="info",
            website_id=website_id,
            metadata={"url": url, "action": "start"}
        )
    
    def log_scrape_progress(self, url: str, step: str, website_id: Optional[int] = None):
        """Log scraping progress"""
        self.log(
            activity_type="scrape",
            message=f"Scraping {url}: {step}",
            status="info",
            website_id=website_id,
            metadata={"url": url, "step": step}
        )
    
    def log_scrape_success(
        self,
        url: str,
        website_id: int,
        title: Optional[str] = None,
        category: Optional[str] = None
    ):
        """Log successful scrape"""
        self.log(
            activity_type="scrape",
            message=f"Successfully scraped: {title or url}",
            status="success",
            website_id=website_id,
            metadata={
                "url": url,
                "title": title,
                "category": category,
                "action": "complete"
            }
        )
    
    def log_extraction_start(self, website_id: int, url: str):
        """Log contact extraction start"""
        self.log(
            activity_type="extract",
            message=f"Extracting contacts from: {url}",
            status="info",
            website_id=website_id,
            metadata={"url": url, "action": "start"}
        )
    
    def log_extraction_progress(
        self,
        website_id: int,
        step: str,
        count: Optional[int] = None
    ):
        """Log extraction progress"""
        metadata = {"step": step}
        if count is not None:
            metadata["count"] = count
        
        self.log(
            activity_type="extract",
            message=f"Extracting {step}" + (f": {count} found" if count else ""),
            status="info",
            website_id=website_id,
            metadata=metadata
        )
    
    def log_extraction_success(
        self,
        website_id: int,
        emails: int,
        phones: int,
        social: int
    ):
        """Log successful extraction"""
        self.log(
            activity_type="extract",
            message=f"Extracted {emails} emails, {phones} phones, {social} social links",
            status="success",
            website_id=website_id,
            metadata={
                "emails": emails,
                "phones": phones,
                "social": social,
                "action": "complete"
            }
        )
    
    def log_job_start(self, job_type: str, job_id: int, target: Optional[str] = None):
        """Log job start"""
        self.log(
            activity_type="job",
            message=f"Starting {job_type}" + (f": {target}" if target else ""),
            status="info",
            job_id=job_id,
            metadata={"job_type": job_type, "target": target, "action": "start"}
        )
    
    def log_job_progress(self, job_type: str, job_id: int, message: str, count: Optional[int] = None):
        """Log job progress"""
        metadata = {"job_type": job_type, "message": message}
        if count is not None:
            metadata["count"] = count
        
        self.log(
            activity_type="job",
            message=f"{job_type}: {message}" + (f" ({count} items)" if count else ""),
            status="info",
            job_id=job_id,
            metadata=metadata
        )
    
    def log_job_success(self, job_type: str, job_id: int, result: Dict[str, Any]):
        """Log job success"""
        self.log(
            activity_type="job",
            message=f"Completed {job_type}",
            status="success",
            job_id=job_id,
            metadata={"job_type": job_type, "result": result, "action": "complete"}
        )

