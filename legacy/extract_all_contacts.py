"""
Script to extract contacts for all scraped websites that don't have contacts yet
"""
from db.database import SessionLocal
from db.models import ScrapedWebsite, Contact
from extractor.contact_extraction_service import ContactExtractionService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_contacts_for_all():
    """Extract contacts for all scraped websites without contacts"""
    db = SessionLocal()
    try:
        # Get all scraped websites
        all_websites = db.query(ScrapedWebsite).all()
        logger.info(f"Found {len(all_websites)} scraped websites")
        
        # Find websites without contacts
        websites_with_contacts = db.query(Contact.website_id).distinct().all()
        website_ids_with_contacts = {w[0] for w in websites_with_contacts}
        
        websites_without_contacts = [
            w for w in all_websites 
            if w.id not in website_ids_with_contacts
        ]
        
        logger.info(f"Found {len(websites_without_contacts)} websites without contacts")
        
        if not websites_without_contacts:
            logger.info("All websites already have contacts extracted!")
            return
        
        extraction_service = ContactExtractionService(db)
        
        total_emails = 0
        total_phones = 0
        total_social = 0
        processed = 0
        failed = 0
        
        for website in websites_without_contacts:
            try:
                logger.info(f"Processing website {website.id}: {website.url}")
                result = extraction_service.extract_and_store_contacts(website.id)
                
                if result and "error" not in result:
                    emails = result.get("emails_extracted", 0)
                    phones = result.get("phones_extracted", 0)
                    social = result.get("social_links_extracted", 0)
                    
                    total_emails += emails
                    total_phones += phones
                    total_social += social
                    processed += 1
                    
                    logger.info(
                        f"  ✓ Extracted: {emails} emails, {phones} phones, {social} social links"
                    )
                else:
                    failed += 1
                    error_msg = result.get("error", "Unknown error") if result else "No result"
                    logger.warning(f"  ✗ Failed: {error_msg}")
            except Exception as e:
                failed += 1
                logger.error(f"  ✗ Error processing {website.url}: {str(e)}")
        
        logger.info("=" * 60)
        logger.info("Extraction Summary:")
        logger.info(f"  Processed: {processed}")
        logger.info(f"  Failed: {failed}")
        logger.info(f"  Total Emails: {total_emails}")
        logger.info(f"  Total Phones: {total_phones}")
        logger.info(f"  Total Social Links: {total_social}")
        logger.info("=" * 60)
        
    finally:
        db.close()

if __name__ == "__main__":
    extract_contacts_for_all()

