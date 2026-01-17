"""
Scheduler for periodic tasks (follow-ups, reply checks, automatic scraper)
"""
import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import os
from dotenv import load_dotenv
import time
from datetime import datetime, timezone

load_dotenv()

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def schedule_followups():
    """Schedule follow-up email job"""
    # TODO: Implement followup task in backend/app/tasks/followup.py
    logger.warning("Followup task not yet implemented in backend - scheduler job skipped")
    # When implemented, use asyncio.create_task() like other tasks:
    # try:
    #     from app.tasks.followup import process_followup_job
    #     import asyncio
    #     job_id = f"followup_{int(time.time())}"
    #     asyncio.create_task(process_followup_job(job_id))
    #     logger.info("Scheduled follow-up job")
    # except ImportError:
    #     logger.warning("Followup task not yet implemented")


def schedule_reply_check():
    """Schedule reply check job"""
    # TODO: Implement reply handler in backend/app/tasks/reply_handler.py
    logger.warning("Reply handler not yet implemented in backend - scheduler job skipped")
    # When implemented, use asyncio.create_task() like other tasks:
    # try:
    #     from app.tasks.reply_handler import process_reply_check_job
    #     import asyncio
    #     asyncio.create_task(process_reply_check_job())
    #     logger.info("Scheduled reply check job")
    # except ImportError:
    #     logger.warning("Reply handler not yet implemented")


async def check_and_run_scraper():
    """Check scraper automation conditions and run if needed"""
    try:
        from app.db.database import AsyncSessionLocal
        from app.api.scraper import (
            get_scraper_setting, check_master_switch,
            calculate_and_set_next_run
        )
        from app.models.scraper_history import ScraperHistory
        from app.models.job import Job
        from sqlalchemy import select
        
        async with AsyncSessionLocal() as db:
            # Check master switch
            master_enabled = await check_master_switch(db)
            if not master_enabled:
                return
            
            # Check auto switch
            auto_enabled = await get_scraper_setting(db, "auto_enabled", False)
            if not auto_enabled:
                return
            
            # Check next run time
            next_run_at_str = await get_scraper_setting(db, "next_run_at", None)
            if not next_run_at_str:
                return
            
            try:
                next_run_at = datetime.fromisoformat(next_run_at_str.replace('Z', '+00:00'))
            except Exception as e:
                logger.error(f"Error parsing next_run_at: {e}")
                return
            
            now = datetime.now(timezone.utc)
            if now < next_run_at:
                return  # Not time yet
            
            # Check if there's already a running job
            result = await db.execute(
                select(Job).where(
                    Job.job_type.in_(["discover", "enrich"]),
                    Job.status == "running"
                )
            )
            running_job = result.scalar_one_or_none()
            if running_job:
                logger.info("Skipping scraper run - job already running")
                return
            
            # Create history entry
            history = ScraperHistory(
                triggered_at=now,
                status="running"
            )
            db.add(history)
            await db.commit()
            await db.refresh(history)
            
            logger.info(f"🚀 Starting automatic scraper run (history_id: {history.id})")
            
            # Get config
            locations = await get_scraper_setting(db, "locations", [])
            categories = await get_scraper_setting(db, "categories", [])
            interval = await get_scraper_setting(db, "interval", "1h")
            
            # Create discovery job directly (bypass auth for system user)
            from app.tasks.discovery import process_discovery_job
            import asyncio
            
            # Create job record
            job = Job(
                job_type="discover",
                params={
                    "keywords": "",
                    "locations": locations,
                    "categories": categories,
                    "max_results": 100
                },
                status="pending"
            )
            db.add(job)
            await db.commit()
            await db.refresh(job)
            
            # Start discovery task in background
            try:
                # Create task and don't await - let it run in background
                task = asyncio.create_task(process_discovery_job(str(job.id)))
                logger.info(f"✅ Automatic discovery job {job.id} started (task_id: {id(task)})")
                
                # Mark history as completed immediately (job runs async)
                # The actual job completion will be tracked separately
                history.completed_at = datetime.now(timezone.utc)
                history.status = "completed"
                history.success_count = 1
                # Don't set duration yet - job is still running
                await db.commit()
                
                # Calculate next run immediately
                await calculate_and_set_next_run(db, interval)
                
                logger.info(f"✅ Automatic scraper run initiated (job_id: {job.id})")
                
            except Exception as e:
                logger.error(f"❌ Automatic scraper run failed: {e}", exc_info=True)
                history.completed_at = datetime.now(timezone.utc)
                history.status = "failed"
                history.failed_count = 1
                history.error_message = str(e)
                duration = (history.completed_at - history.triggered_at).total_seconds()
                history.duration_seconds = duration
                await db.commit()
                
    except Exception as e:
        logger.error(f"Error in check_and_run_scraper: {e}", exc_info=True)


def start_scheduler():
    """Start the scheduler with configured jobs"""
    # Schedule scraper check every minute (async function)
    scheduler.add_job(
        check_and_run_scraper,
        trigger=IntervalTrigger(minutes=1),
        id="scraper_check",
        name="Check and Run Automatic Scraper",
        max_instances=1  # Prevent overlapping runs
    )
    
    # Schedule follow-ups daily at 9 AM
    scheduler.add_job(
        schedule_followups,
        trigger=CronTrigger(hour=9, minute=0),
        id="daily_followups",
        name="Daily Follow-up Emails"
    )
    
    # Schedule reply checks every 6 hours
    scheduler.add_job(
        schedule_reply_check,
        trigger=IntervalTrigger(hours=6),
        id="reply_checks",
        name="Check for Email Replies"
    )
    
    scheduler.start()
    logger.info("Scheduler started (includes automatic scraper check every minute)")


def stop_scheduler():
    """Stop the scheduler"""
    scheduler.shutdown()
    logger.info("Scheduler stopped")

