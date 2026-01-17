"""
Outreach email sender with retry logic and database logging
"""
from typing import Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from db.models import OutreachEmail
from emailer.email_sender import EmailSender
from emailer.html_formatter import HTMLEmailFormatter
from utils.config import settings
import logging
import time

logger = logging.getLogger(__name__)


class OutreachEmailSender:
    """Send outreach emails with retry logic and database logging"""
    
    def __init__(self, db: Session, use_gmail: bool = True, max_retries: int = 3):
        """
        Initialize outreach email sender
        
        Args:
            db: Database session
            use_gmail: Use Gmail API if True, SMTP otherwise
            max_retries: Maximum number of retry attempts
        """
        self.db = db
        self.email_sender = EmailSender(use_gmail=use_gmail)
        self.html_formatter = HTMLEmailFormatter()
        self.max_retries = max_retries
    
    def send_outreach_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        website_id: int,
        contact_id: Optional[int] = None,
        use_html: bool = True,
        business_name: Optional[str] = None,
        sender_name: Optional[str] = None
    ) -> Dict:
        """
        Send outreach email with retry logic and database logging
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            website_id: ID of the scraped website
            contact_id: Optional ID of the contact
            use_html: Whether to send HTML version
            business_name: Business name for HTML formatting
            sender_name: Sender name for HTML formatting
            
        Returns:
            Dictionary with status and email record
        """
        # Create email record in database (status: pending)
        email_record = OutreachEmail(
            website_id=website_id,
            contact_id=contact_id,
            subject=subject,
            body=body,
            recipient_email=to_email,
            status="pending",
            created_at=datetime.utcnow()
        )
        self.db.add(email_record)
        self.db.commit()
        self.db.refresh(email_record)
        
        # Format HTML if requested
        html_body = None
        if use_html:
            html_body = self.html_formatter.format_as_html(
                body,
                business_name=business_name,
                sender_name=sender_name
            )
        
        # Retry logic
        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Attempting to send email to {to_email} (attempt {attempt}/{self.max_retries})")
                
                # Send email
                result = self.email_sender.send(
                    to_email=to_email,
                    subject=subject,
                    body=body,
                    html_body=html_body
                )
                
                if result.get("success"):
                    # Update email record with success
                    email_record.status = "sent"
                    email_record.sent_at = datetime.utcnow()
                    if result.get("message_id"):
                        email_record.metadata = {
                            "message_id": result.get("message_id"),
                            "thread_id": result.get("thread_id"),
                            "provider": "gmail" if self.email_sender.use_gmail else "smtp"
                        }
                    
                    self.db.commit()
                    logger.info(f"Email sent successfully to {to_email}, email_id: {email_record.id}")
                    
                    return {
                        "success": True,
                        "email_id": email_record.id,
                        "message_id": result.get("message_id"),
                        "status": "sent"
                    }
                else:
                    last_error = result.get("error", "Unknown error")
                    logger.warning(f"Email send failed (attempt {attempt}): {last_error}")
                    
                    # Wait before retry (exponential backoff)
                    if attempt < self.max_retries:
                        wait_time = 2 ** attempt  # 2, 4, 8 seconds
                        time.sleep(wait_time)
            
            except Exception as e:
                last_error = str(e)
                logger.error(f"Exception sending email (attempt {attempt}): {str(e)}")
                
                # Wait before retry
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
        
        # All retries failed - update email record
        email_record.status = "failed"
        email_record.metadata = {
            "error": last_error,
            "attempts": self.max_retries,
            "provider": "gmail" if self.email_sender.use_gmail else "smtp"
        }
        self.db.commit()
        
        logger.error(f"Failed to send email to {to_email} after {self.max_retries} attempts: {last_error}")
        
        return {
            "success": False,
            "email_id": email_record.id,
            "error": last_error,
            "status": "failed"
        }
    
    def send_bulk_outreach_emails(
        self,
        emails: list,
        use_html: bool = True
    ) -> Dict:
        """
        Send multiple outreach emails
        
        Args:
            emails: List of dictionaries with:
                - to_email: Recipient email
                - subject: Email subject
                - body: Email body
                - website_id: Website ID
                - contact_id: Optional contact ID
                - business_name: Optional business name
            use_html: Whether to send HTML version
            
        Returns:
            Dictionary with summary statistics
        """
        results = {
            "total": len(emails),
            "sent": 0,
            "failed": 0,
            "details": []
        }
        
        for email_data in emails:
            result = self.send_outreach_email(
                to_email=email_data["to_email"],
                subject=email_data["subject"],
                body=email_data["body"],
                website_id=email_data["website_id"],
                contact_id=email_data.get("contact_id"),
                use_html=use_html,
                business_name=email_data.get("business_name"),
                sender_name=email_data.get("sender_name")
            )
            
            if result.get("success"):
                results["sent"] += 1
            else:
                results["failed"] += 1
            
            results["details"].append(result)
            
            # Rate limiting - wait between emails
            time.sleep(1)
        
        logger.info(f"Bulk email send completed: {results['sent']} sent, {results['failed']} failed")
        return results

