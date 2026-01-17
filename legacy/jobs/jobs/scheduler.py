"""
Background job scheduler using APScheduler - 24/7 Automation Pipeline
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from utils.config import settings
from jobs.automation_jobs import (
    fetch_new_art_websites,
    scrape_pending_websites,
    extract_and_store_contacts,
    generate_ai_email,
    send_email_if_not_sent
)
import atexit
import logging

logger = logging.getLogger(__name__)

scheduler = None


def start_scheduler():
    """Start the background job scheduler with full automation pipeline"""
    global scheduler
    
    if not settings.SCHEDULER_ENABLED:
        logger.warning("Scheduler is disabled in settings")
        return
    
    # Check if automation is enabled in database
    from db.database import SessionLocal
    from utils.app_settings import AppSettingsManager
    
    db = SessionLocal()
    try:
        settings_manager = AppSettingsManager(db)
        automation_enabled = settings_manager.get_automation_enabled()
        if not automation_enabled:
            logger.info("Automation is disabled in database - scheduler will start but jobs will check before running")
    finally:
        db.close()
    
    scheduler = BackgroundScheduler()
    
    # Get search interval from database settings (reuse existing db session)
    db2 = SessionLocal()
    try:
        settings_manager2 = AppSettingsManager(db2)
        search_interval = settings_manager2.get_search_interval_seconds()
    finally:
        db2.close()
    
    # Job 1: Fetch new art websites
    # Use interval trigger if interval is set, otherwise use weekly schedule
    if search_interval and search_interval < 86400:  # Less than 24 hours = use interval
        from apscheduler.triggers.interval import IntervalTrigger
        scheduler.add_job(
            func=fetch_new_art_websites,
            trigger=IntervalTrigger(seconds=search_interval),
            id='fetch_new_art_websites',
            name=f'Fetch New Art Websites (Every {search_interval}s)',
            replace_existing=True,
            max_instances=1
        )
        logger.info(f"Website discovery scheduled to run every {search_interval} seconds")
    else:
        # Default: Weekly on Monday at 3 AM
        scheduler.add_job(
            func=fetch_new_art_websites,
            trigger=CronTrigger(day_of_week='mon', hour=3, minute=0),
            id='fetch_new_art_websites',
            name='Fetch New Art Websites (Weekly)',
            replace_existing=True,
            max_instances=1
        )
        logger.info("Website discovery scheduled weekly (Monday 3 AM)")
    
    # Job 2: Scrape pending websites (every 6 hours)
    scheduler.add_job(
        func=scrape_pending_websites,
        trigger=IntervalTrigger(hours=6),
        id='scrape_pending_websites',
        name='Scrape Pending Websites (Every 6h)',
        replace_existing=True,
        max_instances=1
    )
    
    # Job 3: Extract and store contacts (every 4 hours)
    scheduler.add_job(
        func=extract_and_store_contacts,
        trigger=IntervalTrigger(hours=4),
        id='extract_and_store_contacts',
        name='Extract and Store Contacts (Every 4h)',
        replace_existing=True,
        max_instances=1
    )
    
    # Job 4: Generate AI emails (every 2 hours)
    scheduler.add_job(
        func=generate_ai_email,
        trigger=IntervalTrigger(hours=2),
        id='generate_ai_email',
        name='Generate AI Emails (Every 2h)',
        replace_existing=True,
        max_instances=1
    )
    
    # Job 5: Send emails if not sent (every hour)
    scheduler.add_job(
        func=send_email_if_not_sent,
        trigger=IntervalTrigger(hours=1),
        id='send_email_if_not_sent',
        name='Send Emails If Not Sent (Hourly)',
        replace_existing=True,
        max_instances=1
    )
    
    scheduler.start()
    
    # Register shutdown handler
    atexit.register(lambda: scheduler.shutdown() if scheduler else None)
    
    logger.info("=" * 60)
    logger.info("24/7 Automation Pipeline Started")
    logger.info("=" * 60)
    logger.info("Scheduled Jobs:")
    logger.info("  1. Fetch New Art Websites - Weekly (Monday 3 AM)")
    logger.info("  2. Scrape Pending Websites - Every 6 hours")
    logger.info("  3. Extract and Store Contacts - Every 4 hours")
    logger.info("  4. Generate AI Emails - Every 2 hours")
    logger.info("  5. Send Emails If Not Sent - Every hour")
    logger.info("=" * 60)
    
    print("Background scheduler started - 24/7 automation pipeline active")

