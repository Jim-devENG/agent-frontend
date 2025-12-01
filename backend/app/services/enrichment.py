"""
Standalone enrichment service
Can be called from discovery or as a separate job.

Returns a dict compatible with the frontend EnrichmentResult shape
for successful lookups:

{
    "email": str,
    "name": str | None,
    "company": str | None,
    "confidence": float,
    "domain": str,
    "success": bool,
    "source": str | None,
    "error": str | None,
}

or None when no email candidate could be found.
"""
import logging
import time
from typing import Optional, Dict, Any
from app.clients.hunter import HunterIOClient

logger = logging.getLogger(__name__)


async def enrich_prospect_email(domain: str, name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Enrich a prospect's email using Hunter.io.

    This service is intentionally low‑level and is used by both discovery and
    the direct enrichment API.

    Returns a normalized dict on success (see module docstring) or None when
    no usable email candidate is found.
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
        best_confidence = 0.0
        for email_data in emails:
            if not isinstance(email_data, dict):
                continue
            confidence = float(email_data.get("confidence_score", 0) or 0)
            if confidence > best_confidence:
                best_confidence = confidence
                best_email = email_data
        
        if not best_email or not best_email.get("value"):
            logger.warning(f"⚠️  [ENRICHMENT] No valid email value in response for {domain}")
            return None
        
        email_value = best_email["value"]
        # Build a simple display name from first/last name if present
        first_name = best_email.get("first_name") or ""
        last_name = best_email.get("last_name") or ""
        full_name = f"{first_name} {last_name}".strip() or None
        company = best_email.get("company")
        
        total_time = (time.time() - start_time) * 1000
        
        result: Dict[str, Any] = {
            "email": email_value,
            "name": full_name,
            "company": company,
            "confidence": best_confidence,
            "domain": domain,
            "success": True,
            "source": "hunter_io",
            "error": None,
        }
        
        logger.info(f"✅ [ENRICHMENT] Enriched {domain} in {total_time:.0f}ms")
        logger.info(
            "📤 [ENRICHMENT] Output - email=%s, name=%s, company=%s, confidence=%.1f, source=%s",
            email_value,
            full_name,
            company,
            best_confidence,
            "hunter_io",
        )
        
        return result
        
    except Exception as e:
        total_time = (time.time() - start_time) * 1000
        error_msg = f"Enrichment failed for {domain} after {total_time:.0f}ms: {str(e)}"
        logger.error(f"❌ [ENRICHMENT] {error_msg}", exc_info=True)
        # Re-raise with full context
        raise Exception(error_msg) from e

