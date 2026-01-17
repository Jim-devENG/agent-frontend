"""
Email generator that uses either OpenAI or Gemini, with template-based fallback
"""
from typing import Dict, Optional
from sqlalchemy.orm import Session
from utils.config import settings
from ai.openai_client import OpenAIClient
from ai.gemini_client import GeminiClient
from ai.email_templates import EmailTemplateEngine
from db.models import ScrapedWebsite, Contact, EmailTemplate
import re


class EmailGenerator:
    """Unified interface for generating emails using different AI providers"""
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.openai_client = OpenAIClient()
        self.gemini_client = GeminiClient()
        self.template_engine = EmailTemplateEngine(db)
        self.default_provider = settings.AI_MODEL.split("-")[0] if settings.AI_MODEL else "openai"
    
    def generate(
        self,
        artist_name: str,
        website_url: str,
        website_type: str,
        context: Optional[Dict] = None,
        provider: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate outreach email using specified or default provider (legacy method)
        
        Args:
            artist_name: Name of the artist/creator
            website_url: URL of their website/profile
            website_type: Type of website
            context: Additional context
            provider: 'openai' or 'gemini', defaults to configured model
            
        Returns:
            Dictionary with 'subject' and 'body' keys
        """
        provider = provider or self.default_provider
        
        if provider.lower() == "gemini":
            # Adapt context for new method signature
            adapted_context = context or {}
            if website_type:
                adapted_context["category"] = website_type
                adapted_context["art_style"] = website_type
            return self.gemini_client.generate_outreach_email(
                artist_name, website_url, adapted_context
            )
        else:
            return self.openai_client.generate_outreach_email(
                artist_name, website_url, website_type, context
            )
    
    def generate_outreach_email(
        self,
        business_name: str,
        website_url: str,
        context: Optional[Dict] = None,
        provider: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate outreach email using business context (new method)
        
        Args:
            business_name: Name of the business/artist/gallery
            website_url: URL of their website
            context: Dictionary with:
                - website_summary: Summary of website content
                - art_style: Detected art style or category
                - category: Website category
                - description: Website description
                - metadata: Additional metadata
            provider: 'openai' or 'gemini', defaults to configured model
            
        Returns:
            Dictionary with 'subject' and 'body' keys
        """
        provider = provider or self.default_provider
        
        if provider.lower() == "gemini":
            return self.gemini_client.generate_outreach_email(
                business_name, website_url, context
            )
        else:
            # For OpenAI, adapt the context
            adapted_context = context or {}
            return self.openai_client.generate_outreach_email(
                business_name,
                website_url,
                adapted_context.get("category", "website"),
                context
            )
    
    def generate_from_website(
        self,
        website: ScrapedWebsite,
        contact: Optional[Contact] = None,
        use_ai: bool = True,
        template_name: Optional[str] = None,
        provider: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate email from website and contact data using templates or AI
        
        Args:
            website: ScrapedWebsite instance
            contact: Optional Contact instance
            use_ai: Whether to use AI (True) or templates (False)
            template_name: Optional template name to use (if not using AI)
            provider: 'openai' or 'gemini', defaults to configured model
            
        Returns:
            Dictionary with 'subject' and 'body' keys
        """
        # Try to use database template first if not using AI
        if not use_ai and self.db:
            template = None
            if template_name:
                # Use specific template
                template = self.db.query(EmailTemplate).filter(
                    EmailTemplate.name == template_name,
                    EmailTemplate.is_active == True
                ).first()
            else:
                # Use default template for category
                category = website.category or "default"
                template = self.db.query(EmailTemplate).filter(
                    EmailTemplate.category == category,
                    EmailTemplate.is_active == True,
                    EmailTemplate.is_default == True
                ).first()
            
            if template:
                # Render template with variables
                return self._render_template(template, website, contact)
        
        if use_ai:
            # Use AI with website context
            context = {
                "website_summary": website.description or "",
                "art_style": website.category or "general",
                "category": website.category or "general",
                "description": website.description or "",
                "metadata": website.extra_metadata or {}
            }
            
            business_name = website.title or website.domain or website.url
            return self.generate_outreach_email(
                business_name,
                website.url,
                context,
                provider
            )
        else:
            # Fallback to template engine
            return self.template_engine.generate_email(website, contact)
    
    def _render_template(self, template: EmailTemplate, website: ScrapedWebsite, contact: Optional[Contact]) -> Dict[str, str]:
        """Render a template with variables"""
        # Prepare variables
        variables = {
            "business_name": website.title or website.domain or "Business",
            "recipient_name": contact.name if contact else "Team",
            "business_context": website.description or "your work",
            "personalized_intro": self._generate_personalized_intro(website, contact),
            "specific_offer": self._generate_specific_offer(website),
            "website_url": website.url,
            "category": website.category or "general",
            "social_platform": contact.social_platform if contact else None,
            "your_name": "Your Name"  # TODO: Make configurable
        }
        
        # Render subject
        subject = template.subject_template
        for key, value in variables.items():
            if value:
                subject = subject.replace(f"{{{key}}}", str(value))
        
        # Render body
        body = template.body_template
        for key, value in variables.items():
            if value:
                body = body.replace(f"{{{key}}}", str(value))
        
        return {
            "subject": subject,
            "body": body
        }
    
    def _generate_personalized_intro(self, website: ScrapedWebsite, contact: Optional[Contact]) -> str:
        """Generate a personalized introduction based on context"""
        category = website.category or "general"
        intros = {
            "art_gallery": "I specialize in connecting artists with new audiences through innovative digital campaigns.",
            "interior_decor": "I work with interior designers to showcase their work through digital storytelling.",
            "home_tech": "I help tech-forward home brands reach their target audience through creative marketing.",
            "mom_blogs": "I collaborate with family-focused content creators to expand their reach.",
            "nft_tech": "I work with NFT platforms to connect creators with collectors.",
            "editorial_media": "I partner with media houses to enhance their digital presence.",
            "holiday_family": "I help family-oriented brands create meaningful connections with their audience."
        }
        return intros.get(category, "I specialize in helping businesses grow through strategic partnerships.")
    
    def _generate_specific_offer(self, website: ScrapedWebsite) -> str:
        """Generate a specific offer based on category"""
        category = website.category or "general"
        offers = {
            "art_gallery": "I believe our services could significantly enhance your outreach and artist visibility. Would you be open to a brief chat next week to explore potential synergies?",
            "interior_decor": "I'd love to discuss how we can help showcase your design portfolio to a wider audience. Are you available for a quick call this week?",
            "home_tech": "I think we could create some exciting opportunities to showcase your innovative products. Would you be interested in exploring a collaboration?",
            "mom_blogs": "I'd love to help you reach more families with your valuable content. Could we schedule a brief conversation?",
            "nft_tech": "I believe we could help connect your platform with the right creators and collectors. Would you be open to a discussion?",
            "editorial_media": "I'd like to explore how we can enhance your digital presence and reach. Are you available for a call?",
            "holiday_family": "I think we could create meaningful campaigns that resonate with families. Would you be interested in learning more?"
        }
        return offers.get(category, "I'd love to explore how we can work together. Would you be open to a brief conversation?")

