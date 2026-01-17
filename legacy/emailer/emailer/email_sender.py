"""
Unified email sender interface
"""
from typing import Dict, Optional
from utils.config import settings
from emailer.gmail_client import GmailClient
from emailer.smtp_client import SMTPClient
import logging

logger = logging.getLogger(__name__)


class EmailSender:
    """Unified interface for sending emails via Gmail API or SMTP"""
    
    def __init__(self, use_gmail: bool = None):
        """
        Initialize email sender
        
        Args:
            use_gmail: If True, use Gmail API; if False, use SMTP; if None, auto-detect
        """
        # Auto-detect based on available credentials
        if use_gmail is None:
            has_gmail = bool(settings.GMAIL_CLIENT_ID and settings.GMAIL_CLIENT_SECRET)
            has_smtp = bool(settings.SMTP_USER and settings.SMTP_PASSWORD)
            use_gmail = has_gmail and not has_smtp  # Prefer Gmail if both available
        
        self.use_gmail = use_gmail
        if use_gmail:
            try:
                self.gmail_client = GmailClient()
                self.smtp_client = None
            except Exception as e:
                logger.warning(f"Gmail client initialization failed: {str(e)}, falling back to SMTP")
                self.gmail_client = None
                self.smtp_client = SMTPClient()
                self.use_gmail = False
        else:
            self.gmail_client = None
            self.smtp_client = SMTPClient()
    
    def send(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None,
        html_body: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Send an email with optional HTML body
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            from_email: Sender email
            html_body: Optional HTML version of the email
            
        Returns:
            Dictionary with status
        """
        if self.use_gmail and self.gmail_client:
            return self.gmail_client.send_email(to_email, subject, body, from_email, html_body)
        elif self.smtp_client:
            return self.smtp_client.send_email_sync(to_email, subject, body, from_email, html_body)
        else:
            return {
                "success": False,
                "error": "Email client not properly configured"
            }

