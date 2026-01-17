"""
Shared email sending service
Used by both pipeline send and manual send endpoints
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.prospect import Prospect, SendStatus
from app.models.email_log import EmailLog
from app.clients.gmail import GmailClient

logger = logging.getLogger(__name__)


async def send_prospect_email(
    prospect: Prospect,
    db: AsyncSession,
    gmail_client: Optional[GmailClient] = None
) -> Dict[str, Any]:
    """
    Send email for a single prospect using Gmail API.
    
    This is the canonical send logic used by both:
    - Pipeline send (batch)
    - Manual send (individual)
    
    Args:
        prospect: Prospect model instance
        db: Database session
        gmail_client: Optional Gmail client (will create if not provided)
        
    Returns:
        Dict with 'success' (bool) and 'message_id' or 'error'
        
    Raises:
        ValueError: If prospect is not sendable
        Exception: If Gmail send fails
    """
    # Validate prospect is sendable
    if not prospect.contact_email:
        raise ValueError("Prospect has no contact email")
    
    if not prospect.draft_subject or not prospect.draft_body:
        raise ValueError("Prospect has no draft email (draft_subject and draft_body required)")
    
    if prospect.send_status == SendStatus.SENT.value:
        raise ValueError("Email already sent for this prospect")
    
    # Get email content - use draft_body (final_body is set after sending)
    subject = prospect.draft_subject
    body = prospect.draft_body
    
    if not subject or not body:
        raise ValueError("Prospect has no draft email (draft_subject and draft_body required)")
    
    # Initialize Gmail client if not provided
    if not gmail_client:
        try:
            logger.info("🔧 [SEND] Initializing Gmail client...")
            gmail_client = GmailClient()
            
            # Verify client is properly configured
            if not gmail_client.is_configured():
                raise ValueError(
                    "Gmail client is not properly configured. "
                    "Set GMAIL_ACCESS_TOKEN or (GMAIL_REFRESH_TOKEN + GMAIL_CLIENT_ID + GMAIL_CLIENT_SECRET) environment variables."
                )
            
            # If using refresh token, test that it works
            if gmail_client.refresh_token and not gmail_client.access_token:
                logger.info("🔄 [SEND] Testing refresh token...")
                if not await gmail_client.refresh_access_token():
                    raise ValueError(
                        "Gmail refresh token is invalid or expired. "
                        "Please generate a new refresh token from Google OAuth Playground or re-authenticate."
                    )
            
            logger.info("✅ [SEND] Gmail client initialized successfully")
        except ValueError as e:
            error_msg = str(e)
            logger.error(f"❌ [SEND] Gmail client initialization failed: {error_msg}")
            raise ValueError(error_msg)
        except Exception as e:
            logger.error(f"❌ [SEND] Unexpected error initializing Gmail client: {e}", exc_info=True)
            raise ValueError(f"Gmail configuration error: {str(e)}")
    
    # Send email via Gmail API
    logger.info(f"📧 [SEND] Sending email to {prospect.contact_email} (prospect_id: {prospect.id})...")
    
    try:
        send_result = await gmail_client.send_email(
            to_email=prospect.contact_email,
            subject=subject,
            body=body
        )
    except Exception as send_err:
        logger.error(f"❌ [SEND] Gmail API call failed: {send_err}", exc_info=True)
        raise Exception(f"Failed to send email via Gmail: {send_err}")
    
    if not send_result.get("success"):
        error_msg = send_result.get('error', 'Unknown error')
        error_detail = send_result.get('error_detail', error_msg)
        status_code = send_result.get('status_code')
        
        logger.error(f"❌ [SEND] Gmail returned error: {error_msg}")
        if error_detail and error_detail != error_msg:
            logger.error(f"❌ [SEND] Error details: {error_detail}")
        
        # Provide structured error message
        full_error = f"Gmail API error: {error_msg}"
        if error_detail and error_detail != error_msg:
            full_error += f"\n\n{error_detail}"
        
        raise Exception(full_error)
    
    # Create email log
    email_log = EmailLog(
        prospect_id=prospect.id,
        subject=subject,
        body=body,
        response=send_result
    )
    db.add(email_log)
    
    # Update prospect: move draft_body to final_body, set sent_at, update status
    # Move draft to final_body after sending (preserves sent email content)
    prospect.final_body = prospect.draft_body
    
    # Clear draft after sending (but keep final_body)
    prospect.draft_body = None
    prospect.draft_subject = None
    
    prospect.last_sent = datetime.now(timezone.utc)
    prospect.send_status = SendStatus.SENT.value
    prospect.outreach_status = "sent"  # Legacy field
    
    # Increment follow-up sequence index if this is a follow-up
    if prospect.sequence_index and prospect.sequence_index > 0:
        # This is already a follow-up, increment
        prospect.sequence_index += 1
    elif prospect.thread_id and prospect.thread_id != prospect.id:
        # This is a follow-up (thread_id != own id), set sequence_index to 1
        prospect.sequence_index = 1
    
    # Commit changes
    await db.commit()
    await db.refresh(prospect)
    
    message_id = send_result.get('message_id', 'N/A')
    logger.info(f"✅ [SEND] Email sent to {prospect.contact_email} (message_id: {message_id})")
    logger.info(f"📝 [SEND] Updated prospect {prospect.id} - send_status=SENT, last_sent={prospect.last_sent}")
    
    return {
        "success": True,
        "message_id": message_id,
        "sent_at": prospect.last_sent.isoformat() if prospect.last_sent else None
    }

