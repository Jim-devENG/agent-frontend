"""
Website scraper for art-related websites with JS fallback
"""
from typing import List, Dict, Any, Optional, Tuple
from scraper.base_scraper import BaseScraper
from scraper.art_detector import ArtDetector
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import logging

logger = logging.getLogger(__name__)


class WebsiteScraper(BaseScraper):
    """Scraper for general art websites, galleries, and portfolios"""
    
    def __init__(self):
        super().__init__()
        self.art_detector = ArtDetector()
        self.playwright_browser = None
        self.playwright_context = None
    
    def scrape_website(self, url: str) -> Dict[str, Any]:
        """
        Scrape a website with HTML download and JS fallback
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary with scraped data including:
            - url, domain, title, description
            - links, metadata, raw_html
            - is_art_related, website_type
            - status, error (if failed)
        """
        try:
            # Try fetching with requests first
            soup, raw_html = self.fetch_page(url)
            
            # If that fails or returns minimal content, try Playwright
            if not soup or self._is_minimal_content(soup):
                logger.info(f"Attempting Playwright fallback for {url}")
                soup, raw_html = self._fetch_with_playwright(url)
            
            if not soup:
                return {
                    "url": url,
                    "status": "failed",
                    "error": "Failed to fetch page with both requests and Playwright"
                }
            
            # Extract all data
            metadata = self.extract_metadata(soup, url)
            links = self._extract_links(soup, url)
            website_type = self._detect_website_type(soup, url)
            
            # Detect if art-related
            text_content = soup.get_text().lower() if soup else ""
            is_art_related = self.art_detector.is_art_related(soup, url, text_content)
            
            return {
                "url": url,
                "domain": self._extract_domain(url),
                "title": metadata.get("title", ""),
                "description": metadata.get("description", ""),
                "website_type": website_type,
                "links": links,
                "metadata": metadata,
                "raw_html": raw_html or "",
                "is_art_related": is_art_related,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return {
                "url": url,
                "status": "failed",
                "error": str(e)
            }
    
    def _is_minimal_content(self, soup: BeautifulSoup) -> bool:
        """Check if page has minimal content (likely JS-rendered)"""
        if not soup:
            return True
        
        # Check if body has very little text
        body = soup.find("body")
        if not body:
            return True
        
        text_length = len(body.get_text(strip=True))
        # If less than 100 characters, likely JS-rendered
        return text_length < 100
    
    def _fetch_with_playwright(self, url: str) -> Tuple[Optional[BeautifulSoup], Optional[str]]:
        """
        Fetch page using Playwright for JS-rendered content
        
        Args:
            url: URL to fetch
            
        Returns:
            Tuple of (BeautifulSoup object, raw HTML string)
        """
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
            logger.warning("Playwright not available, skipping JS fallback")
            return None, None
        except Exception as e:
            logger.error(f"Error initializing Playwright for {url}: {str(e)}")
            return None, None
    
    def _detect_website_type(self, soup: BeautifulSoup, url: str) -> str:
        """Detect the type of website"""
        url_lower = url.lower()
        
        if "instagram.com" in url_lower:
            return "instagram"
        elif "tiktok.com" in url_lower:
            return "tiktok"
        elif "behance.net" in url_lower:
            return "behance"
        elif "dribbble.com" in url_lower:
            return "dribbble"
        elif "pinterest.com" in url_lower:
            return "pinterest"
        elif any(keyword in url_lower for keyword in ["gallery", "art-gallery", "artgallery"]):
            return "gallery"
        elif any(keyword in url_lower for keyword in ["portfolio", "portfolios"]):
            return "portfolio"
        else:
            return "website"
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        parsed = urlparse(url)
        return parsed.netloc
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all links from the page"""
        links = []
        if soup:
            seen = set()
            for tag in soup.find_all("a", href=True):
                href = tag.get("href", "")
                if href:
                    # Convert relative URLs to absolute
                    absolute_url = urljoin(base_url, href)
                    # Remove fragments and normalize
                    parsed = urlparse(absolute_url)
                    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                    if parsed.query:
                        normalized += f"?{parsed.query}"
                    
                    if normalized not in seen and normalized.startswith(("http://", "https://")):
                        seen.add(normalized)
                        links.append(normalized)
        return links
