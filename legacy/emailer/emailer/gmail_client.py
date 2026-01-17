"""
Gmail API client for sending emails
"""
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional
from utils.config import settings
import os
import logging

logger = logging.getLogger(__name__)


class GmailClient:
    """Client for sending emails via Gmail API"""
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    
    def __init__(self):
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API"""
        creds = None
        
        # Check for existing token
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        
        # If no valid credentials, use refresh token from settings
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            elif settings.GMAIL_REFRESH_TOKEN:
                # Use refresh token to get new credentials
                creds = Credentials(
                    token=None,
                    refresh_token=settings.GMAIL_REFRESH_TOKEN,
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=settings.GMAIL_CLIENT_ID,
                    client_secret=settings.GMAIL_CLIENT_SECRET
                )
                creds.refresh(Request())
            
            # Save credentials for next run
            if creds:
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
        
        if creds:
            self.service = build('gmail', 'v1', credentials=creds)
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None,
        html_body: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Send an email via Gmail API with HTML support
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            from_email: Sender email (uses authenticated account if not provided)
            html_body: Optional HTML version of the email body
            
        Returns:
            Dictionary with status and message_id
        """
        if not self.service:
            return {
                "success": False,
                "error": "Gmail API not authenticated"
            }
        
        try:
            # Create multipart message if HTML is provided
            if html_body:
                message = MIMEMultipart('alternative')
                message.attach(MIMEText(body, 'plain'))
                message.attach(MIMEText(html_body, 'html'))
            else:
                message = MIMEText(body)
            
            message['to'] = to_email
            message['subject'] = subject
            if from_email:
                message['from'] = from_email
            
            raw_message = base64.urlsafe_b64encode(
                message.as_bytes()
            ).decode('utf-8')
            
            send_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            logger.info(f"Email sent successfully to {to_email}, message_id: {send_message.get('id')}")
            
            return {
                "success": True,
                "message_id": send_message.get('id'),
                "thread_id": send_message.get('threadId')
            }
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

