"""
Scheduler for periodic tasks (follow-ups, reply checks)
"""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import os
from dotenv import load_dotenv
import redis
from rq import Queue
import time

load_dotenv()

logger = logging.getLogger(__name__)

# Redis connection for RQ
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_conn = redis.from_url(redis_url)
followup_queue = Queue("followup", connection=redis_conn)

scheduler = AsyncIOScheduler()


def schedule_followups():
    """Schedule follow-up email job"""
    try:
        from worker.tasks.followup import send_followups_task
        
        # Create a job ID (in production, create Job record first)
        # For now, use a simple identifier
        job_id = f"followup_{int(__import__('time').time())}"
        
        # Queue the task
        followup_queue.enqueue(send_followups_task, job_id)
        logger.info("Scheduled follow-up job")
    except ImportError:
        logger.warning("Worker tasks not available - follow-up job not queued. Ensure worker service is running.")


def schedule_reply_check():
    """Schedule reply check job"""
    try:
        from worker.tasks.reply_handler import check_replies_task
        
        # Queue the task
        followup_queue.enqueue(check_replies_task)
        logger.info("Scheduled reply check job")
    except ImportError:
        logger.warning("Worker tasks not available - reply check job not queued. Ensure worker service is running.")


def start_scheduler():
    """Start the scheduler with configured jobs"""
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
    logger.info("Scheduler started")


def stop_scheduler():
    """Stop the scheduler"""
    scheduler.shutdown()
    logger.info("Scheduler stopped")

