"""
Simple test script for the scraper
"""
from db.database import SessionLocal
from scraper.scraper_service import ScraperService
from utils.logging_config import setup_logging

# Setup logging
setup_logging()

# Create database session
db = SessionLocal()

try:
    # Initialize scraper service
    scraper_service = ScraperService(db)
    
    # Test scraping a website
    print("Testing website scraping...")
    website = scraper_service.scrape_website("https://www.behance.net")
    
    if website:
        print(f"✓ Successfully scraped: {website.url}")
        print(f"  Title: {website.title}")
        print(f"  Type: {website.website_type}")
        print(f"  Art-related: {website.is_art_related}")
    else:
        print("✗ Failed to scrape website")
    
    # Test scraping social media
    print("\nTesting social media scraping...")
    social = scraper_service.scrape_social_media("behance", "behance")
    
    if social:
        print(f"✓ Successfully scraped: {social.url}")
        print(f"  Title: {social.title}")
        print(f"  Type: {social.website_type}")
    else:
        print("✗ Failed to scrape social media")
        
finally:
    db.close()

