"""
SMTP client for sending emails
"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional
from utils.config import settings
import logging

logger = logging.getLogger(__name__)


class SMTPClient:
    """Client for sending emails via SMTP"""
    
    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.username = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None,
        html_body: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Send an email via SMTP with HTML support
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            from_email: Sender email (uses configured SMTP_USER if not provided)
            html_body: Optional HTML version of the email body
            
        Returns:
            Dictionary with status
        """
        if not self.username or not self.password:
            return {
                "success": False,
                "error": "SMTP credentials not configured"
            }
        
        from_email = from_email or self.username
        
        try:
            message = MIMEMultipart('alternative')
            message['From'] = from_email
            message['To'] = to_email
            message['Subject'] = subject
            
            # Add plain text version
            message.attach(MIMEText(body, 'plain'))
            
            # Add HTML version if provided
            if html_body:
                message.attach(MIMEText(html_body, 'html'))
            
            await aiosmtplib.send(
                message,
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                start_tls=True
            )
            
            logger.info(f"Email sent successfully to {to_email} via SMTP")
            
            return {
                "success": True
            }
        except Exception as e:
            logger.error(f"Error sending email to {to_email} via SMTP: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_email_sync(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None,
        html_body: Optional[str] = None
    ) -> Dict[str, any]:
        """Synchronous version of send_email"""
        import asyncio
        return asyncio.run(self.send_email(to_email, subject, body, from_email, html_body))

