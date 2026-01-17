"""
Phone number extraction from web pages
"""
import re
from typing import List, Set
from bs4 import BeautifulSoup


class PhoneExtractor:
    """Extract phone numbers from web content"""
    
    # Phone number patterns (various formats)
    PHONE_PATTERNS = [
        # US/Canada: (123) 456-7890, 123-456-7890, 123.456.7890
        re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'),
        # International: +1 123 456 7890, +44 20 1234 5678
        re.compile(r'\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'),
        # With extensions: 123-456-7890 ext 123
        re.compile(r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}[-.\s]?(?:ext|extension|x)[-.\s]?\d+', re.IGNORECASE),
        # Toll-free: 1-800-123-4567
        re.compile(r'1?[-.\s]?8[0-9]{2}[-.\s]?\d{3}[-.\s]?\d{4}'),
    ]
    
    def extract_from_html(self, html_content: str) -> List[str]:
        """
        Extract phone numbers from HTML content
        
        Args:
            html_content: HTML string
            
        Returns:
            List of unique phone numbers
        """
        phone_numbers: Set[str] = set()
        
        soup = BeautifulSoup(html_content, "lxml")
        
        # Extract from text content
        text_content = soup.get_text()
        for pattern in self.PHONE_PATTERNS:
            matches = pattern.findall(text_content)
            phone_numbers.update(matches)
        
        # Extract from tel: links
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            if href.startswith("tel:"):
                phone = href.replace("tel:", "").strip()
                if self._is_valid_phone(phone):
                    phone_numbers.add(phone)
        
        # Extract from data attributes and meta tags
        for tag in soup.find_all(attrs={"data-phone": True}):
            phone = tag.get("data-phone", "").strip()
            if self._is_valid_phone(phone):
                phone_numbers.add(phone)
        
        # Filter and normalize
        filtered_phones = [self._normalize_phone(p) for p in phone_numbers if self._is_valid_phone(p)]
        
        return list(set(filtered_phones))
    
    def extract_from_text(self, text: str) -> List[str]:
        """
        Extract phone numbers from plain text
        
        Args:
            text: Plain text string
            
        Returns:
            List of unique phone numbers
        """
        phone_numbers: Set[str] = set()
        
        for pattern in self.PHONE_PATTERNS:
            matches = pattern.findall(text)
            phone_numbers.update(matches)
        
        filtered_phones = [self._normalize_phone(p) for p in phone_numbers if self._is_valid_phone(p)]
        return list(set(filtered_phones))
    
    def _is_valid_phone(self, phone: str) -> bool:
        """Validate phone number"""
        if not phone or len(phone) < 10:
            return False
        
        # Remove common separators for validation
        digits_only = re.sub(r'[^\d+]', '', phone)
        
        # Should have at least 10 digits (US format) or start with +
        if phone.startswith('+'):
            return len(digits_only) >= 10
        else:
            return len(digits_only) >= 10 and len(digits_only) <= 15
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number format"""
        # Remove extra whitespace
        phone = phone.strip()
        
        # Remove common prefixes like "Phone:", "Tel:", etc.
        phone = re.sub(r'^(phone|tel|call|contact)[:\s]+', '', phone, flags=re.IGNORECASE)
        
        return phone

