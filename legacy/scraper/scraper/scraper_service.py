"""
Scraper service that coordinates scraping and database operations
"""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from db.models import ScrapedWebsite
from scraper.website_scraper import WebsiteScraper
from scraper.social_scraper import SocialScraper
from scraper.domain_analyzer import DomainAnalyzer
from scraper.art_detector import ArtDetector
from utils.config import settings
import logging
from datetime import datetime
from utils.activity_logger import ActivityLogger

logger = logging.getLogger(__name__)


class ScraperService:
    """Service for scraping websites and saving to database"""
    
    def __init__(self, db: Session, apply_quality_filter: bool = True):
        """
        Initialize scraper service
        
        Args:
            db: Database session
            apply_quality_filter: Whether to apply quality filtering before scraping
        """
        self.db = db
        self.website_scraper = WebsiteScraper()
        self.social_scraper = SocialScraper()
        self.domain_analyzer = DomainAnalyzer()
        self.art_detector = ArtDetector()
        self.apply_quality_filter = apply_quality_filter
        self.activity_logger = ActivityLogger(db)
    
    def scrape_website(self, url: str, skip_quality_check: bool = False) -> Optional[ScrapedWebsite]:
        """
        Scrape a website and save to database with quality filtering
        
        Args:
            url: URL to scrape
            skip_quality_check: Skip quality check (for testing or manual scraping)
            
        Returns:
            ScrapedWebsite model instance or None if failed or doesn't meet quality threshold
        """
        try:
            # Check if already scraped
            existing = self.db.query(ScrapedWebsite).filter(
                ScrapedWebsite.url == url
            ).first()
            
            if existing:
                logger.info(f"Website {url} already exists in database")
                return existing
            
            # Log domain analysis
            self.activity_logger.log_scrape_progress(url, "Analyzing domain quality")
            
            # Analyze domain quality before scraping
            domain_metrics = self.domain_analyzer.analyze_domain(url)
            
            # Apply quality filters if enabled
            if self.apply_quality_filter and not skip_quality_check:
                if not self._meets_quality_requirements(domain_metrics):
                    logger.warning(
                        f"Website {url} does not meet quality requirements. "
                        f"Quality score: {domain_metrics.get('quality_score', 0)}, "
                        f"Domain authority: {domain_metrics.get('domain_authority', 0)}, "
                        f"SSL valid: {domain_metrics.get('ssl_valid', False)}, "
                        f"Valid DNS: {domain_metrics.get('has_valid_dns', False)}"
                    )
                    # Still save the website but mark it as not meeting quality threshold
                    # This allows it to appear in the list but be filtered later if needed
                    pass  # Continue to scrape anyway, we'll mark it in the database
            
            # Log scraping
            self.activity_logger.log_scrape_progress(url, "Downloading and parsing website")
            
            # Scrape the website
            result = self.website_scraper.scrape_website(url)
            
            if result.get("status") != "success":
                logger.error(f"Failed to scrape {url}: {result.get('error')}")
                return None
            
            # Determine category
            soup = None
            if result.get("raw_html"):
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(result.get("raw_html", ""), "lxml")
            
            category = self.art_detector.get_category(
                soup, url, result.get("raw_html", "")
            ) if soup else "unknown"
            
            # Check if meets quality threshold
            meets_threshold = self.domain_analyzer.meets_quality_threshold(
                domain_metrics, settings.MIN_QUALITY_SCORE
            )
            
            # If quality filter is enabled and doesn't meet requirements, still save but mark it
            if self.apply_quality_filter and not skip_quality_check:
                if not self._meets_quality_requirements(domain_metrics):
                    meets_threshold = False
                    logger.info(f"Saving {url} but marking as not meeting quality threshold")
            
            # Save to database
            website = ScrapedWebsite(
                url=result["url"],
                domain=result["domain"],
                title=result.get("title"),
                description=result.get("description"),
                website_type=result.get("website_type", "website"),
                category=category,
                raw_html=result.get("raw_html", ""),
                extra_metadata=result.get("metadata", {}),
                is_art_related=result.get("is_art_related", False),
                # Quality metrics
                domain_authority=domain_metrics.get("domain_authority"),
                quality_score=domain_metrics.get("quality_score"),
                estimated_traffic=domain_metrics.get("estimated_traffic"),
                ssl_valid=domain_metrics.get("ssl_valid", False),
                domain_age_days=domain_metrics.get("domain_age_days"),
                has_valid_dns=domain_metrics.get("has_valid_dns", False),
                meets_quality_threshold=meets_threshold,
                status="processed"
            )
            
            self.db.add(website)
            self.db.commit()
            self.db.refresh(website)
            
            logger.info(
                f"Successfully scraped and saved {url} "
                f"(Quality: {domain_metrics.get('quality_score', 0)}, "
                f"Category: {category})"
            )
            
            # Log success
            self.activity_logger.log_scrape_success(url, website.id, website.title, category)
            
            # Automatically extract contacts after scraping
            try:
                from extractor.contact_extraction_service import ContactExtractionService
                extraction_service = ContactExtractionService(self.db)
                extraction_result = extraction_service.extract_and_store_contacts(website.id)
                
                if extraction_result and "error" not in extraction_result:
                    emails = extraction_result.get("emails_extracted", 0)
                    phones = extraction_result.get("phones_extracted", 0)
                    social = extraction_result.get("social_links_extracted", 0)
                    logger.info(
                        f"Automatically extracted contacts for {url}: "
                        f"{emails} emails, {phones} phones, {social} social links"
                    )
                else:
                    error_msg = extraction_result.get("error", "Unknown error") if extraction_result else "No result"
                    logger.warning(f"Failed to extract contacts for {url}: {error_msg}")
            except Exception as e:
                logger.warning(f"Error extracting contacts for {url}: {str(e)}")
                # Don't fail the scrape if contact extraction fails
            
            return website
            
        except Exception as e:
            logger.error(f"Error in scrape_website for {url}: {str(e)}")
            self.db.rollback()
            return None
    
    def _meets_quality_requirements(self, domain_metrics: Dict) -> bool:
        """
        Check if domain meets quality requirements
        
        Args:
            domain_metrics: Domain analysis metrics
            
        Returns:
            True if meets all requirements
        """
        # Check quality score
        quality_score = domain_metrics.get("quality_score", 0)
        if quality_score < settings.MIN_QUALITY_SCORE:
            return False
        
        # Check domain authority
        domain_authority = domain_metrics.get("domain_authority", 0)
        if domain_authority < settings.MIN_DOMAIN_AUTHORITY:
            return False
        
        # Check traffic tier
        traffic_tier = domain_metrics.get("estimated_traffic", {}).get("traffic_tier", "very_low")
        traffic_tiers = ["very_low", "low", "medium", "high", "very_high"]
        min_tier_index = traffic_tiers.index(settings.MIN_TRAFFIC_TIER)
        current_tier_index = traffic_tiers.index(traffic_tier)
        if current_tier_index < min_tier_index:
            return False
        
        # Check SSL requirement
        if settings.REQUIRE_SSL and not domain_metrics.get("ssl_valid", False):
            return False
        
        # Check DNS requirement
        if settings.REQUIRE_VALID_DNS and not domain_metrics.get("has_valid_dns", False):
            return False
        
        return True
    
    def scrape_social_media(
        self,
        username: str,
        platform: str,
        skip_quality_check: bool = True  # Social media usually has good quality
    ) -> Optional[ScrapedWebsite]:
        """
        Scrape social media profile and save to database
        
        Args:
            username: Username or handle
            platform: Platform name (instagram, tiktok, behance, pinterest)
            skip_quality_check: Skip quality check for social media (default: True)
            
        Returns:
            ScrapedWebsite model instance or None if failed
        """
        try:
            # Scrape the social media profile
            result = self.social_scraper.scrape_social_media(username, platform)
            
            if result.get("status") != "success":
                logger.error(
                    f"Failed to scrape {platform} profile {username}: "
                    f"{result.get('error')}"
                )
                return None
            
            url = result["url"]
            
            # Check if already scraped
            existing = self.db.query(ScrapedWebsite).filter(
                ScrapedWebsite.url == url
            ).first()
            
            if existing:
                logger.info(f"Social profile {url} already exists in database")
                return existing
            
            # Analyze domain (but don't filter social media by default)
            domain_metrics = self.domain_analyzer.analyze_domain(url)
            
            # Determine category
            soup = None
            if result.get("raw_html"):
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(result.get("raw_html", ""), "lxml")
            
            category = self.art_detector.get_category(
                soup, url, result.get("raw_html", "")
            ) if soup else "unknown"
            
            # Save to database
            website = ScrapedWebsite(
                url=url,
                domain=self._extract_domain(url),
                title=result.get("title", f"{platform.title()} - {username}"),
                description=result.get("description", ""),
                website_type=platform,
                category=category,
                raw_html=result.get("raw_html", ""),
                extra_metadata=result.get("metadata", {}),
                is_art_related=result.get("is_art_related", False),
                # Quality metrics
                domain_authority=domain_metrics.get("domain_authority"),
                quality_score=domain_metrics.get("quality_score"),
                estimated_traffic=domain_metrics.get("estimated_traffic"),
                ssl_valid=domain_metrics.get("ssl_valid", False),
                domain_age_days=domain_metrics.get("domain_age_days"),
                has_valid_dns=domain_metrics.get("has_valid_dns", False),
                meets_quality_threshold=True,  # Social media platforms are trusted
                status="processed"
            )
            
            self.db.add(website)
            self.db.commit()
            self.db.refresh(website)
            
            logger.info(f"Successfully scraped and saved {platform} profile {username}")
            
            # Automatically extract contacts after scraping
            try:
                from extractor.contact_extraction_service import ContactExtractionService
                extraction_service = ContactExtractionService(self.db)
                extraction_result = extraction_service.extract_and_store_contacts(website.id)
                
                if extraction_result and "error" not in extraction_result:
                    emails = extraction_result.get("emails_extracted", 0)
                    phones = extraction_result.get("phones_extracted", 0)
                    social = extraction_result.get("social_links_extracted", 0)
                    logger.info(
                        f"Automatically extracted contacts for {platform} profile {username}: "
                        f"{emails} emails, {phones} phones, {social} social links"
                    )
                else:
                    error_msg = extraction_result.get("error", "Unknown error") if extraction_result else "No result"
                    logger.warning(f"Failed to extract contacts for {platform} profile {username}: {error_msg}")
            except Exception as e:
                logger.warning(f"Error extracting contacts for {platform} profile {username}: {str(e)}")
                # Don't fail the scrape if contact extraction fails
            
            return website
            
        except Exception as e:
            logger.error(
                f"Error in scrape_social_media for {platform}/{username}: {str(e)}"
            )
            self.db.rollback()
            return None
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc

