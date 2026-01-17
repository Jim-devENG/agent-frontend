"""
Social media link extraction
"""
import re
from typing import List, Dict
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class SocialExtractor:
    """Extract social media links from web pages"""
    
    # Platform patterns - expanded for better detection
    PLATFORM_PATTERNS = {
        "instagram": [
            r"instagram\.com/([a-zA-Z0-9_.]+)",
            r"instagr\.am/([a-zA-Z0-9_.]+)",
            r"ig\.me/([a-zA-Z0-9_.]+)"
        ],
        "tiktok": [
            r"tiktok\.com/@([a-zA-Z0-9_.]+)",
            r"vm\.tiktok\.com",
            r"tiktok\.com/user/([a-zA-Z0-9_.]+)"
        ],
        "behance": [
            r"behance\.net/([a-zA-Z0-9_.]+)"
        ],
        "dribbble": [
            r"dribbble\.com/([a-zA-Z0-9_.]+)"
        ],
        "pinterest": [
            r"pinterest\.com/([a-zA-Z0-9_.]+)",
            r"pinterest\.([a-zA-Z]{2})/([a-zA-Z0-9_.]+)"
        ],
        "twitter": [
            r"twitter\.com/([a-zA-Z0-9_.]+)",
            r"x\.com/([a-zA-Z0-9_.]+)"
        ],
        "facebook": [
            r"facebook\.com/([a-zA-Z0-9_.]+)",
            r"fb\.com/([a-zA-Z0-9_.]+)"
        ],
        "linkedin": [
            r"linkedin\.com/in/([a-zA-Z0-9_.-]+)",
            r"linkedin\.com/company/([a-zA-Z0-9_.-]+)"
        ],
        "youtube": [
            r"youtube\.com/(?:channel|c|user)/([a-zA-Z0-9_.-]+)",
            r"youtu\.be/([a-zA-Z0-9_.-]+)"
        ],
        "snapchat": [
            r"snapchat\.com/add/([a-zA-Z0-9_.]+)"
        ]
    }
    
    # Social icon class patterns (common CSS classes used for social icons)
    SOCIAL_ICON_CLASSES = [
        "fa-instagram", "fa-facebook", "fa-twitter", "fa-linkedin",
        "fa-tiktok", "fa-pinterest", "fa-youtube", "fa-snapchat",
        "social-instagram", "social-facebook", "social-twitter",
        "icon-instagram", "icon-facebook", "icon-twitter"
    ]
    
    def extract_from_html(self, html_content: str) -> Dict[str, List[str]]:
        """
        Extract social media links from HTML using regex + BeautifulSoup
        
        Args:
            html_content: HTML string
            
        Returns:
            Dictionary mapping platform names to lists of URLs/usernames
        """
        soup = BeautifulSoup(html_content, "lxml")
        social_links = {platform: [] for platform in self.PLATFORM_PATTERNS.keys()}
        
        # Extract from all links (including social icons)
        for link in soup.find_all("a", href=True):
            href = link.get("href", "")
            if href:
                # Check if link has social icon classes
                link_classes = " ".join(link.get("class", [])).lower()
                is_social_icon = any(icon_class in link_classes for icon_class in self.SOCIAL_ICON_CLASSES)
                
                # Extract social info from URL
                parsed = self._extract_social_from_url(href)
                if parsed:
                    platform, identifier = parsed
                    full_url = identifier if identifier.startswith("http") else href
                    if full_url not in social_links[platform]:
                        social_links[platform].append(full_url)
        
        # Extract from text content as well
        text_content = soup.get_text()
        for platform, patterns in self.PLATFORM_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text_content, re.IGNORECASE)
                for match in matches:
                    if len(match.groups()) > 0:
                        identifier = match.group(1)
                        if identifier not in social_links[platform]:
                            social_links[platform].append(identifier)
        
        # Extract from meta tags (Open Graph, Twitter Cards)
        for meta in soup.find_all("meta", property=True):
            property_name = meta.get("property", "").lower()
            content = meta.get("content", "")
            
            if "og:url" in property_name or "twitter:url" in property_name:
                parsed = self._extract_social_from_url(content)
                if parsed:
                    platform, identifier = parsed
                    if identifier not in social_links[platform]:
                        social_links[platform].append(identifier)
        
        # Filter out empty lists
        return {k: v for k, v in social_links.items() if v}
    
    def _extract_social_from_url(self, url: str) -> tuple:
        """
        Extract platform and identifier from URL
        
        Returns:
            Tuple of (platform, identifier) or None
        """
        url_lower = url.lower()
        
        for platform, patterns in self.PLATFORM_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, url_lower, re.IGNORECASE)
                if match:
                    if len(match.groups()) > 0:
                        return (platform, match.group(1))
                    else:
                        return (platform, url)
        
        return None

