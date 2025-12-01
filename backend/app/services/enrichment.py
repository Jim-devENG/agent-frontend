"""
Standalone enrichment service
Can be called from discovery or as a separate job
Returns: { email: str, confidence: float, source: str } or None
"""
import logging
import time
from typing import Optional, Dict, Any
from app.clients.hunter import HunterIOClient

logger = logging.getLogger(__name__)


async def enrich_prospect_email(domain: str, name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Enrich a prospect's email using Hunter.io
    
    Args:
        domain: Domain name (e.g., "example.com")
        name: Optional contact name for better matching
        
    Returns:
        Dict with { email: str, confidence: float, source: str } or None if no email found
        
    Raises:
        Exception with full stack trace if enrichment fails
    """
    start_time = time.time()
    logger.info(f"🔍 [ENRICHMENT] Starting enrichment for domain: {domain}, name: {name or 'N/A'}")
    logger.info(f"📥 [ENRICHMENT] Input - domain: {domain}, name: {name}")
    
    try:
        # Initialize Hunter client
        try:
            hunter_client = HunterIOClient()
            logger.info(f"✅ [ENRICHMENT] Hunter.io client initialized")
        except ValueError as e:
            error_msg = f"Hunter.io not configured: {e}"
            logger.error(f"❌ [ENRICHMENT] {error_msg}")
            raise ValueError(error_msg) from e
        
        # Call Hunter.io API
        try:
            hunter_result = await hunter_client.domain_search(domain)
            api_time = (time.time() - start_time) * 1000
            logger.info(f"⏱️  [ENRICHMENT] Hunter.io API call completed in {api_time:.0f}ms")
        except Exception as api_err:
            api_time = (time.time() - start_time) * 1000
            error_msg = f"Hunter.io API call failed after {api_time:.0f}ms: {str(api_err)}"
            logger.error(f"❌ [ENRICHMENT] {error_msg}", exc_info=True)
            raise Exception(error_msg) from api_err
        
        # Process response
        if not hunter_result.get("success"):
            error_msg = hunter_result.get('error', 'Unknown error')
            logger.warning(f"⚠️  [ENRICHMENT] Hunter.io returned error: {error_msg}")
            return None
        
        emails = hunter_result.get("emails", [])
        if not emails or len(emails) == 0:
            logger.info(f"⚠️  [ENRICHMENT] No emails found for {domain}")
            return None
        
        # Get best email (highest confidence)
        best_email = None
        best_confidence = 0
        for email_data in emails:
            confidence = email_data.get("confidence_score", 0)
            if confidence > best_confidence:
                best_confidence = confidence
                best_email = email_data
        
        if not best_email or not best_email.get("value"):
            logger.warning(f"⚠️  [ENRICHMENT] No valid email value in response for {domain}")
            return None
        
        email_value = best_email["value"]
        total_time = (time.time() - start_time) * 1000
        
        result = {
            "email": email_value,
            "confidence": best_confidence,
            "source": "hunter_io"
        }
        
        logger.info(f"✅ [ENRICHMENT] Enriched {domain} in {total_time:.0f}ms")
        logger.info(f"📤 [ENRICHMENT] Output - email: {email_value}, confidence: {best_confidence}, source: hunter_io")
        
        return result
        
    except Exception as e:
        total_time = (time.time() - start_time) * 1000
        error_msg = f"Enrichment failed for {domain} after {total_time:.0f}ms: {str(e)}"
        logger.error(f"❌ [ENRICHMENT] {error_msg}", exc_info=True)
        # Re-raise with full context
        raise Exception(error_msg) from e

