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
    "status": str | None,  # "rate_limited", "pending_retry", etc.
}

or None when no email candidate could be found.
"""
import logging
import time
import re
import httpx
from typing import Optional, Dict, Any
from app.clients.hunter import HunterIOClient

logger = logging.getLogger(__name__)


def _extract_emails_from_html(html_content: str) -> list[str]:
    """
    Extract email addresses from HTML content using regex.
    Simple fallback when Hunter.io fails.
    """
    emails = set()
    
    # Standard email regex
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    
    # Extract from text
    found_emails = email_pattern.findall(html_content)
    emails.update(found_emails)
    
    # Filter out common false positives
    filtered = []
    for email in emails:
        email_lower = email.lower()
        # Skip common false positives
        if any(skip in email_lower for skip in ['example.com', 'test@', 'noreply', 'no-reply', '@sentry', '@wix']):
            continue
        filtered.append(email)
    
    return filtered


async def _scrape_email_from_url(url: str) -> Optional[str]:
    """
    Scrape email from a website URL using local HTML parsing.
    Returns first valid email found, or None.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            html = response.text
            
            emails = _extract_emails_from_html(html)
            if emails:
                # Return the first email (usually the most relevant)
                return emails[0]
    except Exception as e:
        logger.debug(f"Local email scraping failed for {url}: {e}")
    
    return None


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
        
        # Process response - handle rate limits specially
        if not hunter_result.get("success"):
            error_msg = hunter_result.get('error', 'Unknown error')
            status = hunter_result.get('status')
            
            # Handle rate limit - return special status, DO NOT return None
            if status == "rate_limited":
                logger.warning(f"⚠️  [ENRICHMENT] Hunter.io rate limited for {domain}")
                # Try local scraping fallback
                try:
                    # Try to scrape from domain's homepage
                    homepage_url = f"https://{domain}"
                    local_email = await _scrape_email_from_url(homepage_url)
                    if local_email:
                        logger.info(f"✅ [ENRICHMENT] Local scraping found email for {domain}: {local_email}")
                        return {
                            "email": local_email,
                            "name": None,
                            "company": None,
                            "confidence": 50.0,  # Lower confidence for local scraping
                            "domain": domain,
                            "success": True,
                            "source": "local_scraping",
                            "error": None,
                            "status": None,
                        }
                    else:
                        # No email found locally, mark for retry
                        logger.warning(f"⚠️  [ENRICHMENT] No email found via local scraping for {domain}, marking for retry")
                        return {
                            "email": None,
                            "name": None,
                            "company": None,
                            "confidence": 0.0,
                            "domain": domain,
                            "success": False,
                            "source": None,
                            "error": "Rate limited and local scraping found no email",
                            "status": "pending_retry",
                        }
                except Exception as scrape_err:
                    logger.warning(f"⚠️  [ENRICHMENT] Local scraping failed for {domain}: {scrape_err}, marking for retry")
                    return {
                        "email": None,
                        "name": None,
                        "company": None,
                        "confidence": 0.0,
                        "domain": domain,
                        "success": False,
                        "source": None,
                        "error": f"Rate limited and local scraping failed: {scrape_err}",
                        "status": "pending_retry",
                    }
            
            # For other errors, try local scraping fallback
            logger.warning(f"⚠️  [ENRICHMENT] Hunter.io returned error: {error_msg}, trying local scraping fallback")
            try:
                homepage_url = f"https://{domain}"
                local_email = await _scrape_email_from_url(homepage_url)
                if local_email:
                    logger.info(f"✅ [ENRICHMENT] Local scraping found email for {domain}: {local_email}")
                    return {
                        "email": local_email,
                        "name": None,
                        "company": None,
                        "confidence": 50.0,
                        "domain": domain,
                        "success": True,
                        "source": "local_scraping",
                        "error": None,
                        "status": None,
                    }
            except Exception as scrape_err:
                logger.debug(f"Local scraping fallback failed for {domain}: {scrape_err}")
            
            # If local scraping also fails, mark for retry instead of returning None
            logger.warning(f"⚠️  [ENRICHMENT] All enrichment methods failed for {domain}, marking for retry")
            return {
                "email": None,
                "name": None,
                "company": None,
                "confidence": 0.0,
                "domain": domain,
                "success": False,
                "source": None,
                "error": error_msg,
                "status": "pending_retry",
            }
        
        emails = hunter_result.get("emails", [])
        if not emails or len(emails) == 0:
            logger.info(f"⚠️  [ENRICHMENT] No emails found for {domain} via Hunter.io, trying local scraping")
            # Try local scraping fallback
            try:
                homepage_url = f"https://{domain}"
                local_email = await _scrape_email_from_url(homepage_url)
                if local_email:
                    logger.info(f"✅ [ENRICHMENT] Local scraping found email for {domain}: {local_email}")
                    return {
                        "email": local_email,
                        "name": None,
                        "company": None,
                        "confidence": 50.0,
                        "domain": domain,
                        "success": True,
                        "source": "local_scraping",
                        "error": None,
                        "status": None,
                    }
            except Exception as scrape_err:
                logger.debug(f"Local scraping fallback failed for {domain}: {scrape_err}")
            
            # Mark for retry instead of returning None
            logger.warning(f"⚠️  [ENRICHMENT] No emails found for {domain}, marking for retry")
            return {
                "email": None,
                "name": None,
                "company": None,
                "confidence": 0.0,
                "domain": domain,
                "success": False,
                "source": None,
                "error": "No emails found via Hunter.io or local scraping",
                "status": "pending_retry",
            }
        
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

