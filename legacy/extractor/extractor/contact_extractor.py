"""
Contact information extraction (combines email, phone, social, and forms)
"""
from typing import Dict, List
from extractor.email_extractor import EmailExtractor
from extractor.phone_extractor import PhoneExtractor
from extractor.social_extractor import SocialExtractor
from extractor.contact_form_extractor import ContactFormExtractor


class ContactExtractor:
    """Extract all contact information from web pages"""
    
    def __init__(self):
        self.email_extractor = EmailExtractor()
        self.phone_extractor = PhoneExtractor()
        self.social_extractor = SocialExtractor()
        self.form_extractor = ContactFormExtractor()
    
    def extract_all(self, html_content: str) -> Dict:
        """
        Extract all contact information from HTML
        
        Args:
            html_content: HTML string
            
        Returns:
            Dictionary with emails, phone numbers, social links, contact forms, and contact page URLs
        """
        emails = self.email_extractor.extract_from_html(html_content)
        phone_numbers = self.phone_extractor.extract_from_html(html_content)
        social_links = self.social_extractor.extract_from_html(html_content)
        contact_forms = self.form_extractor.extract_contact_forms(html_content)
        
        # Extract contact page URLs
        contact_pages = self._extract_contact_pages(html_content)
        
        return {
            "emails": emails,
            "phone_numbers": phone_numbers,
            "social_links": social_links,
            "contact_forms": contact_forms,
            "contact_pages": contact_pages
        }
    
    def _extract_contact_pages(self, html_content: str) -> List[str]:
        """Extract links to contact pages"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, "lxml")
        contact_pages = []
        
        contact_keywords = ["contact", "about", "reach", "connect", "get-in-touch", "support", "info", "team"]
        
        for link in soup.find_all("a", href=True):
            href = link.get("href", "").lower()
            text = link.get_text().lower()
            
            if any(keyword in href or keyword in text for keyword in contact_keywords):
                contact_pages.append(link.get("href"))
        
        return list(set(contact_pages))

