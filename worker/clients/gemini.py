"""
Google Gemini API client for email composition
"""
import httpx
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv
import logging
import json

load_dotenv()

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for Google Gemini API"""
    
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client
        
        Args:
            api_key: Gemini API key (if None, uses GEMINI_API_KEY from env)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError("Gemini API key not configured. Set GEMINI_API_KEY")
    
    def is_configured(self) -> bool:
        """Check if client is properly configured"""
        return bool(self.api_key and self.api_key.strip())
    
    async def compose_email(
        self,
        domain: str,
        page_title: Optional[str] = None,
        page_url: Optional[str] = None,
        page_snippet: Optional[str] = None,
        contact_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compose an email using Gemini API
        
        Args:
            domain: Website domain
            page_title: Page title
            page_url: Page URL
            page_snippet: Page description/snippet
            contact_name: Contact name (if available)
        
        Returns:
            Dictionary with subject and body
        """
        url = f"{self.BASE_URL}/models/gemini-2.0-flash-exp:generateContent?key={self.api_key}"
        
        # Build context for the email
        context_parts = []
        if page_title:
            context_parts.append(f"Website Title: {page_title}")
        if domain:
            context_parts.append(f"Domain: {domain}")
        if page_snippet:
            context_parts.append(f"Description: {page_snippet}")
        if page_url:
            context_parts.append(f"URL: {page_url}")
        
        context = "\n".join(context_parts) if context_parts else f"Website: {domain}"
        
        # Create prompt for structured JSON output
        prompt = f"""You are a professional outreach specialist for an art and creative services company.

Your task is to compose a personalized outreach email to a website owner or content creator.

Context about their website:
{context}

Requirements:
1. The email must be professional, friendly, and personalized
2. It should mention something specific about their website/content
3. It should introduce our art and creative services company
4. It should be concise (2-3 short paragraphs)
5. It should include a clear call-to-action
6. It should be warm but not overly salesy

You MUST return ONLY valid JSON with this exact structure:
{{
  "subject": "Email subject line (max 60 characters)",
  "body": "Email body text (2-3 paragraphs, professional tone)"
}}

Do not include any text before or after the JSON. Return ONLY the JSON object."""

        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 1024,
                "responseMimeType": "application/json"
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                logger.info(f"Calling Gemini API to compose email for domain: {domain}")
                response = await client.post(url, json=payload)
                response.raise_for_status()
                result = response.json()
                
                # Extract content from Gemini response
                if result.get("candidates") and len(result["candidates"]) > 0:
                    candidate = result["candidates"][0]
                    if candidate.get("content") and candidate["content"].get("parts"):
                        text_content = candidate["content"]["parts"][0].get("text", "")
                        
                        # Parse JSON response
                        try:
                            email_data = json.loads(text_content)
                            
                            subject = email_data.get("subject", f"Partnership Opportunity - {domain}")
                            body = email_data.get("body", f"Hello,\n\nI noticed your website {domain}...")
                            
                            logger.info(f"✅ Gemini composed email for {domain}")
                            
                            return {
                                "success": True,
                                "subject": subject,
                                "body": body,
                                "raw_response": result
                            }
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse Gemini JSON response: {e}")
                            logger.error(f"Response text: {text_content[:200]}")
                            # Fallback to extracting from text
                            return self._extract_from_text(text_content, domain)
                    else:
                        return {
                            "success": False,
                            "error": "No content in Gemini response",
                            "domain": domain
                        }
                else:
                    error_msg = result.get("error", {}).get("message", "Unknown error")
                    return {
                        "success": False,
                        "error": error_msg,
                        "domain": domain
                    }
        
        except httpx.HTTPStatusError as e:
            logger.error(f"Gemini API HTTP error for {domain}: {e.response.status_code} - {e.response.text}")
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}: {e.response.text}",
                "domain": domain
            }
        except Exception as e:
            logger.error(f"Gemini API call failed for {domain}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "domain": domain
            }
    
    def _extract_from_text(self, text: str, domain: str) -> Dict[str, Any]:
        """
        Fallback: Extract subject and body from text if JSON parsing fails
        
        Args:
            text: Text response from Gemini
            domain: Domain name
        
        Returns:
            Dictionary with subject and body
        """
        # Try to find JSON in text
        import re
        json_match = re.search(r'\{[^{}]*"subject"[^{}]*\}', text, re.DOTALL)
        if json_match:
            try:
                email_data = json.loads(json_match.group())
                return {
                    "success": True,
                    "subject": email_data.get("subject", f"Partnership Opportunity - {domain}"),
                    "body": email_data.get("body", text)
                }
            except:
                pass
        
        # Ultimate fallback
        lines = text.strip().split('\n')
        subject = lines[0][:60] if lines else f"Partnership Opportunity - {domain}"
        body = '\n'.join(lines[1:]) if len(lines) > 1 else text
        
        return {
            "success": True,
            "subject": subject,
            "body": body
        }

