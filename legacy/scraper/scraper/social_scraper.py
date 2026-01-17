"""
Social media scraper for Instagram, TikTok, Behance, Pinterest
"""
from typing import Dict, Any, Optional
from scraper.base_scraper import BaseScraper
from scraper.art_detector import ArtDetector
from bs4 import BeautifulSoup
import logging
import re

logger = logging.getLogger(__name__)


class SocialScraper(BaseScraper):
    """Scraper for social media platforms"""
    
    def __init__(self):
        super().__init__()
        self.art_detector = ArtDetector()
    
    def scrape_social_media(self, username: str, platform: str) -> Dict[str, Any]:
        """
        Scrape social media profile
        
        Args:
            username: Username or handle
            platform: Platform name (instagram, tiktok, behance, pinterest)
            
        Returns:
            Dictionary with scraped data
        """
        platform = platform.lower()
        
        if platform == "instagram":
            return self.scrape_instagram(username)
        elif platform == "tiktok":
            return self.scrape_tiktok(username)
        elif platform == "behance":
            return self.scrape_behance(username)
        elif platform == "pinterest":
            return self.scrape_pinterest(username)
        else:
            return {
                "username": username,
                "platform": platform,
                "status": "failed",
                "error": f"Unsupported platform: {platform}"
            }
    
    def scrape_instagram(self, username: str) -> Dict[str, Any]:
        """Scrape Instagram profile"""
        url = f"https://www.instagram.com/{username}/"
        return self._scrape_social_platform(url, "instagram", username)
    
    def scrape_tiktok(self, username: str) -> Dict[str, Any]:
        """Scrape TikTok profile"""
        # Remove @ if present
        username = username.lstrip("@")
        url = f"https://www.tiktok.com/@{username}"
        return self._scrape_social_platform(url, "tiktok", username)
    
    def scrape_behance(self, username: str) -> Dict[str, Any]:
        """Scrape Behance profile"""
        url = f"https://www.behance.net/{username}"
        return self._scrape_social_platform(url, "behance", username)
    
    def scrape_pinterest(self, username: str) -> Dict[str, Any]:
        """Scrape Pinterest profile"""
        url = f"https://www.pinterest.com/{username}/"
        return self._scrape_social_platform(url, "pinterest", username)
    
    def _scrape_social_platform(
        self,
        url: str,
        platform: str,
        username: str
    ) -> Dict[str, Any]:
        """
        Scrape a social media platform using Playwright for JS-rendered content
        
        Args:
            url: URL to scrape
            platform: Platform name
            username: Username/handle
            
        Returns:
            Dictionary with scraped data
        """
        try:
            # Try regular fetch first
            soup, raw_html = self.fetch_page(url)
            
            # Social media sites are usually JS-rendered, so use Playwright
            if not soup or self._is_minimal_content(soup):
                soup, raw_html = self._fetch_with_playwright(url)
            
            if not soup:
                return {
                    "url": url,
                    "username": username,
                    "platform": platform,
                    "status": "failed",
                    "error": "Failed to fetch page"
                }
            
            # Extract metadata
            metadata = self.extract_metadata(soup, url)
            
            # Extract platform-specific data
            platform_data = self._extract_platform_data(soup, platform)
            
            # Detect if art-related
            text_content = soup.get_text().lower() if soup else ""
            is_art_related = self.art_detector.is_art_related(soup, url, text_content)
            
            return {
                "url": url,
                "username": username,
                "platform": platform,
                "title": metadata.get("title", ""),
                "description": metadata.get("description", ""),
                "metadata": {**metadata, **platform_data},
                "raw_html": raw_html or "",
                "is_art_related": is_art_related,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error scraping {platform} profile {username}: {str(e)}")
            return {
                "url": url,
                "username": username,
                "platform": platform,
                "status": "failed",
                "error": str(e)
            }
    
    def _is_minimal_content(self, soup: BeautifulSoup) -> bool:
        """Check if page has minimal content"""
        if not soup:
            return True
        
        body = soup.find("body")
        if not body:
            return True
        
        text_length = len(body.get_text(strip=True))
        return text_length < 100
    
    def _fetch_with_playwright(self, url: str) -> tuple:
        """Fetch page using Playwright"""
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                try:
                    page.goto(url, wait_until="networkidle", timeout=30000)
                    raw_html = page.content()
                    soup = BeautifulSoup(raw_html, "lxml")
                    browser.close()
                    return soup, raw_html
                except Exception as e:
                    logger.error(f"Playwright error for {url}: {str(e)}")
                    browser.close()
                    return None, None
        except ImportError:
            logger.warning("Playwright not available")
            return None, None
        except Exception as e:
            logger.error(f"Error initializing Playwright: {str(e)}")
            return None, None
    
    def _extract_platform_data(self, soup: BeautifulSoup, platform: str) -> Dict[str, Any]:
        """Extract platform-specific data"""
        data = {}
        
        if platform == "instagram":
            # Try to extract follower count, bio, etc.
            scripts = soup.find_all("script", type="application/ld+json")
            for script in scripts:
                try:
                    import json
                    json_data = json.loads(script.string)
                    if isinstance(json_data, dict):
                        data.update(json_data)
                except:
                    pass
            
            # Extract from meta tags
            bio = soup.find("meta", property="og:description")
            if bio:
                data["bio"] = bio.get("content", "")
        
        elif platform == "behance":
            # Behance specific extraction
            # Look for project counts, follower counts in the HTML
            stats = soup.find_all("span", class_=re.compile(".*stat.*", re.I))
            if stats:
                data["stats"] = [s.get_text(strip=True) for s in stats]
        
        elif platform == "pinterest":
            # Pinterest specific extraction
            # Look for board counts, pin counts
            pass
        
        elif platform == "tiktok":
            # TikTok specific extraction
            # Look for follower counts, video counts
            pass
        
        return data
