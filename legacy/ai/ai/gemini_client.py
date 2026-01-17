"""
Google Gemini API client for generating outreach emails
"""
import google.generativeai as genai
from typing import Dict, Optional
from utils.config import settings
import logging

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for Google Gemini API"""
    
    def __init__(self):
        if settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                # Try gemini-1.5-pro first, fallback to gemini-pro
                try:
                    self.model = genai.GenerativeModel("gemini-1.5-pro")
                except:
                    self.model = genai.GenerativeModel("gemini-pro")
                logger.info("Gemini API initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini API: {str(e)}")
                self.model = None
        else:
            self.model = None
            logger.warning("GEMINI_API_KEY not configured")
    
    def generate_outreach_email(
        self,
        business_name: str,
        website_url: str,
        context: Optional[Dict] = None
    ) -> Dict[str, str]:
        """
        Generate a personalized outreach email using business context
        
        Args:
            business_name: Name of the business/artist/gallery
            website_url: URL of their website
            context: Dictionary with additional context:
                - website_summary: Summary of the website content
                - art_style: Detected art style or category
                - category: Website category (interior_decor, art_gallery, etc.)
                - description: Website description
                - metadata: Additional metadata
                
        Returns:
            Dictionary with 'subject' and 'body' keys
        """
        if not self.model:
            return {
                "subject": "Collaboration Opportunity",
                "body": f"Hello {business_name}, I would like to discuss a collaboration opportunity.",
                "error": "Gemini API key not configured"
            }
        
        prompt = self._build_outreach_prompt(business_name, website_url, context)
        
        try:
            response = self.model.generate_content(prompt)
            email_content = response.text
            
            # Parse subject and body
            subject, body = self._parse_email_response(email_content)
            
            return {
                "subject": subject,
                "body": body
            }
        except Exception as e:
            logger.error(f"Error generating email with Gemini: {str(e)}")
            return {
                "subject": f"Collaboration Opportunity with {business_name}",
                "body": f"Hello {business_name}, I would like to discuss a collaboration opportunity.",
                "error": str(e)
            }
    
    def _build_outreach_prompt(
        self,
        business_name: str,
        website_url: str,
        context: Optional[Dict]
    ) -> str:
        """Build the prompt for outreach email generation"""
        prompt = f"""Generate a professional, personalized outreach email for a collaboration opportunity.

Business/Organization Name: {business_name}
Website URL: {website_url}
"""
        
        # Add context information
        if context:
            website_summary = context.get("website_summary", "")
            art_style = context.get("art_style", context.get("category", ""))
            description = context.get("description", "")
            
            if website_summary:
                prompt += f"Website Summary: {website_summary}\n"
            
            if art_style:
                prompt += f"Detected Art Style/Category: {art_style}\n"
            
            if description:
                prompt += f"Website Description: {description}\n"
            
            # Add any additional metadata
            metadata = context.get("metadata", {})
            if metadata and isinstance(metadata, dict):
                if metadata.get("title"):
                    prompt += f"Website Title: {metadata.get('title')}\n"
        
        prompt += """
Please generate a professional outreach email with:

1. SUBJECT LINE (max 60 characters):
   - Compelling and personalized
   - Mentions the business name or their work
   - Creates curiosity or interest

2. EMAIL BODY (2-3 paragraphs):
   - Opening: Show genuine interest in their work/business
   - Middle: Mention specific aspects you noticed (art style, content, quality)
   - Closing: Propose collaboration opportunity with clear call to action
   - Tone: Professional but warm, authentic, and respectful
   - Personalization: Reference specific details from their website

Format your response EXACTLY as:
SUBJECT: [subject line here]

BODY:
[email body here - use proper paragraphs]
"""
        return prompt
    
    def _parse_email_response(self, response: str) -> tuple:
        """Parse the email response into subject and body"""
        lines = response.split("\n")
        subject = "Collaboration Opportunity"
        body_lines = []
        
        in_body = False
        for line in lines:
            line_stripped = line.strip()
            if line_stripped.upper().startswith("SUBJECT:"):
                subject = line_stripped.replace("SUBJECT:", "").replace("subject:", "").strip()
            elif line_stripped.upper().startswith("BODY:"):
                in_body = True
            elif in_body:
                body_lines.append(line)
        
        body = "\n".join(body_lines).strip()
        if not body:
            # If parsing failed, try to extract from response
            body = response
        
        return subject, body

