"""
Email template system that adapts based on website/social media details
"""
from typing import Dict, Optional, List
from db.models import ScrapedWebsite, Contact, EmailTemplate
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class EmailTemplateEngine:
    """Generates personalized email templates based on website/social media context"""
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.default_templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """Load email templates for different contexts"""
        return {
            "art_gallery": {
                "subject_templates": [
                    "Collaboration Opportunity for {business_name}",
                    "Partnership Inquiry for {business_name} Gallery",
                    "Creative Collaboration with {business_name}"
                ],
                "body_template": """Hello {recipient_name},

I hope this message finds you well. I recently discovered {business_name} and was truly impressed by {business_context}.

{personalized_intro}

I would love to explore potential collaboration opportunities. {specific_offer}

Looking forward to hearing from you.

Best regards,
{your_name}"""
            },
            "interior_decor": {
                "subject_templates": [
                    "Design Partnership Opportunity",
                    "Collaboration Inquiry for {business_name}",
                    "Creative Partnership with {business_name}"
                ],
                "body_template": """Dear {recipient_name},

I came across {business_name} and was inspired by your {business_context}.

{personalized_intro}

I believe there's potential for a mutually beneficial partnership. {specific_offer}

Would you be open to a conversation?

Warm regards,
{your_name}"""
            },
            "home_tech": {
                "subject_templates": [
                    "Tech Innovation Partnership",
                    "Collaboration Opportunity with {business_name}",
                    "Partnership Inquiry - Tech Solutions"
                ],
                "body_template": """Hi {recipient_name},

I've been following {business_name} and your work in {business_context} is impressive.

{personalized_intro}

I'd like to discuss potential collaboration opportunities. {specific_offer}

Let me know if you'd be interested in connecting.

Best,
{your_name}"""
            },
            "mom_blogs": {
                "subject_templates": [
                    "Content Collaboration Opportunity",
                    "Partnership Inquiry for {business_name}",
                    "Collaboration with {business_name}"
                ],
                "body_template": """Hello {recipient_name},

I'm a fan of {business_name} and love your content about {business_context}.

{personalized_intro}

I'd love to explore collaboration opportunities. {specific_offer}

Would love to hear your thoughts!

Best,
{your_name}"""
            },
            "nft_tech": {
                "subject_templates": [
                    "NFT/Web3 Collaboration",
                    "Partnership Opportunity in Digital Art",
                    "Innovation Partnership with {business_name}"
                ],
                "body_template": """Hi {recipient_name},

I discovered {business_name} and your work in {business_context} caught my attention.

{personalized_intro}

I'm interested in exploring collaboration in the NFT/Web3 space. {specific_offer}

Let's connect!

Best regards,
{your_name}"""
            },
            "editorial_media": {
                "subject_templates": [
                    "Media Partnership Opportunity",
                    "Content Collaboration with {business_name}",
                    "Editorial Partnership Inquiry"
                ],
                "body_template": """Dear {recipient_name},

I've been following {business_name} and appreciate your coverage of {business_context}.

{personalized_intro}

I'd like to discuss potential media partnerships. {specific_offer}

Looking forward to your response.

Best,
{your_name}"""
            },
            "holiday_family": {
                "subject_templates": [
                    "Family-Focused Collaboration",
                    "Partnership Opportunity with {business_name}",
                    "Family Content Collaboration"
                ],
                "body_template": """Hello {recipient_name},

I love what {business_name} is doing in {business_context}.

{personalized_intro}

I believe we could create something special together. {specific_offer}

Would you be open to a conversation?

Warm regards,
{your_name}"""
            },
            "default": {
                "subject_templates": [
                    "Collaboration Opportunity",
                    "Partnership Inquiry for {business_name}",
                    "Let's Connect - {business_name}"
                ],
                "body_template": """Hello {recipient_name},

I recently discovered {business_name} and was impressed by {business_context}.

{personalized_intro}

I'd love to explore potential collaboration opportunities. {specific_offer}

Looking forward to hearing from you.

Best regards,
{your_name}"""
            }
        }
    
    def get_template_for_category(self, category: Optional[str]) -> Dict:
        """Get template for a specific category - checks database first, then defaults"""
        # Try to get from database if available
        if self.db:
            try:
                # Look for active default template for this category
                db_template = self.db.query(EmailTemplate).filter(
                    EmailTemplate.category == category,
                    EmailTemplate.is_active == True,
                    EmailTemplate.is_default == True
                ).first()
                
                if db_template:
                    return {
                        "subject_templates": [db_template.subject_template],
                        "body_template": db_template.body_template
                    }
            except Exception as e:
                logger.warning(f"Error loading template from DB: {e}")
        
        # Fallback to default templates
        if category and category in self.default_templates:
            return self.default_templates[category]
        return self.default_templates["default"]
    
    def generate_context(
        self,
        website: ScrapedWebsite,
        contact: Optional[Contact] = None
    ) -> Dict[str, str]:
        """
        Generate context variables for email template
        
        Args:
            website: ScrapedWebsite instance
            contact: Optional Contact instance
            
        Returns:
            Dictionary of context variables
        """
        # Determine business name
        business_name = website.title or website.domain or website.url
        
        # Determine business context
        business_context = self._determine_business_context(website, contact)
        
        # Determine recipient name
        recipient_name = contact.name if contact and contact.name else "Team"
        
        # Determine personalized intro based on social media
        personalized_intro = self._generate_personalized_intro(website, contact)
        
        # Determine specific offer
        specific_offer = self._generate_specific_offer(website, contact)
        
        return {
            "business_name": business_name,
            "business_context": business_context,
            "recipient_name": recipient_name,
            "personalized_intro": personalized_intro,
            "specific_offer": specific_offer,
            "website_url": website.url,
            "category": website.category or "general",
            "your_name": "Your Name"  # Should be configurable
        }
    
    def _determine_business_context(
        self,
        website: ScrapedWebsite,
        contact: Optional[Contact]
    ) -> str:
        """Determine business context from website and social media"""
        context_parts = []
        
        if website.description:
            # Extract key phrases from description
            desc = website.description[:200]
            context_parts.append(desc)
        
        if contact and contact.social_platform:
            platform_context = {
                "instagram": "your Instagram presence",
                "tiktok": "your TikTok content",
                "behance": "your Behance portfolio",
                "dribbble": "your Dribbble work",
                "pinterest": "your Pinterest boards",
                "twitter": "your Twitter presence",
                "facebook": "your Facebook page",
                "linkedin": "your LinkedIn profile",
                "youtube": "your YouTube channel"
            }
            context = platform_context.get(contact.social_platform.lower(), "your social media")
            context_parts.append(context)
        
        if website.category:
            category_context = {
                "art_gallery": "your gallery's collection",
                "interior_decor": "your interior design work",
                "home_tech": "your tech innovations",
                "mom_blogs": "your blog content",
                "nft_tech": "your NFT projects",
                "editorial_media": "your editorial content",
                "holiday_family": "your family-focused content"
            }
            context = category_context.get(website.category, "your work")
            context_parts.append(context)
        
        return " and ".join(context_parts) if context_parts else "your work"
    
    def _generate_personalized_intro(
        self,
        website: ScrapedWebsite,
        contact: Optional[Contact]
    ) -> str:
        """Generate personalized introduction based on context"""
        intros = []
        
        if contact and contact.social_platform:
            platform_intros = {
                "instagram": "Your Instagram feed showcases incredible creativity.",
                "tiktok": "Your TikTok content is engaging and innovative.",
                "behance": "Your Behance portfolio demonstrates exceptional talent.",
                "dribbble": "Your Dribbble work is truly inspiring.",
                "pinterest": "Your Pinterest boards are beautifully curated.",
                "youtube": "Your YouTube channel provides valuable content."
            }
            intro = platform_intros.get(contact.social_platform.lower())
            if intro:
                intros.append(intro)
        
        if website.category:
            category_intros = {
                "art_gallery": "Your gallery's curation and artist selection is impressive.",
                "interior_decor": "Your design aesthetic and attention to detail is remarkable.",
                "home_tech": "Your innovative approach to home technology is forward-thinking.",
                "mom_blogs": "Your authentic voice and relatable content resonates with readers.",
                "nft_tech": "Your work in the NFT space is cutting-edge.",
                "editorial_media": "Your editorial perspective and coverage is insightful."
            }
            intro = category_intros.get(website.category)
            if intro:
                intros.append(intro)
        
        if not intros:
            intros.append("Your work and vision align with what I'm looking for.")
        
        return " ".join(intros)
    
    def _generate_specific_offer(
        self,
        website: ScrapedWebsite,
        contact: Optional[Contact]
    ) -> str:
        """Generate specific offer based on context"""
        if website.category == "art_gallery":
            return "I'd love to discuss potential art collaborations, exhibitions, or cross-promotional opportunities."
        elif website.category == "interior_decor":
            return "I'm interested in exploring design partnerships, product collaborations, or content creation opportunities."
        elif website.category == "home_tech":
            return "I'd like to discuss potential tech partnerships, product reviews, or innovation collaborations."
        elif website.category == "mom_blogs":
            return "I'm interested in content collaborations, sponsored posts, or brand partnerships."
        elif website.category == "nft_tech":
            return "I'd love to explore NFT collaborations, digital art partnerships, or Web3 initiatives."
        elif website.category == "editorial_media":
            return "I'm interested in editorial partnerships, content collaborations, or media opportunities."
        else:
            return "I believe we could create something valuable together through collaboration."
    
    def generate_email(
        self,
        website: ScrapedWebsite,
        contact: Optional[Contact] = None,
        custom_subject: Optional[str] = None,
        custom_body: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate email subject and body based on website/social context
        
        Args:
            website: ScrapedWebsite instance
            contact: Optional Contact instance
            custom_subject: Optional custom subject line
            custom_body: Optional custom body text
            
        Returns:
            Dictionary with 'subject' and 'body' keys
        """
        template = self.get_template_for_category(website.category)
        context = self.generate_context(website, contact)
        
        # Generate subject
        if custom_subject:
            subject = custom_subject
        else:
            import random
            subject_template = random.choice(template["subject_templates"])
            subject = subject_template.format(**context)
        
        # Generate body
        if custom_body:
            body = custom_body
        else:
            body = template["body_template"].format(**context)
        
        return {
            "subject": subject,
            "body": body,
            "context": context
        }

