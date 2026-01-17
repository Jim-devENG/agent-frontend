"""
OpenAI API client for generating outreach emails
"""
from openai import OpenAI
from typing import Dict, Optional
from utils.config import settings


class OpenAIClient:
    """Client for OpenAI API"""
    
    def __init__(self):
        if settings.OPENAI_API_KEY:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.AI_MODEL
        else:
            self.client = None
            self.model = None
    
    def generate_outreach_email(
        self,
        artist_name: str,
        website_url: str,
        website_type: str,
        context: Optional[Dict] = None
    ) -> Dict[str, str]:
        """
        Generate a personalized outreach email
        
        Args:
            artist_name: Name of the artist/creator
            website_url: URL of their website/profile
            website_type: Type of website (gallery, portfolio, instagram, etc.)
            context: Additional context about the website/artist
            
        Returns:
            Dictionary with 'subject' and 'body' keys
        """
        if not self.client:
            return {
                "subject": "Collaboration Opportunity",
                "body": "Hello, I would like to discuss a collaboration opportunity.",
                "error": "OpenAI API key not configured"
            }
        
        prompt = self._build_prompt(artist_name, website_url, website_type, context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional email writer specializing in art collaboration outreach."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            email_content = response.choices[0].message.content
            subject, body = self._parse_email_response(email_content)
            
            return {
                "subject": subject,
                "body": body
            }
        except Exception as e:
            return {
                "subject": "Collaboration Opportunity",
                "body": "Hello, I would like to discuss a collaboration opportunity.",
                "error": str(e)
            }
    
    def _build_prompt(
        self,
        artist_name: str,
        website_url: str,
        website_type: str,
        context: Optional[Dict]
    ) -> str:
        """Build the prompt for email generation"""
        prompt = f"""Generate a professional, personalized outreach email for an art collaboration opportunity.

Artist/Creator Name: {artist_name}
Website/Profile: {website_url}
Platform Type: {website_type}
"""
        if context:
            prompt += f"Additional Context: {context}\n"
        
        prompt += """
Please generate:
1. A compelling subject line (max 60 characters)
2. A personalized email body (2-3 paragraphs) that:
   - Shows genuine interest in their work
   - Mentions specific aspects of their art/portfolio
   - Proposes a collaboration opportunity
   - Is professional but warm and authentic
   - Includes a clear call to action

Format your response as:
SUBJECT: [subject line]

BODY:
[email body]
"""
        return prompt
    
    def _parse_email_response(self, response: str) -> tuple:
        """Parse the email response into subject and body"""
        lines = response.split("\n")
        subject = "Collaboration Opportunity"
        body_lines = []
        
        in_body = False
        for line in lines:
            if line.startswith("SUBJECT:"):
                subject = line.replace("SUBJECT:", "").strip()
            elif line.startswith("BODY:"):
                in_body = True
            elif in_body:
                body_lines.append(line)
        
        body = "\n".join(body_lines).strip()
        if not body:
            body = response
        
        return subject, body

