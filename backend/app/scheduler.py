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

# Redis connection for RQ - lazy initialization to avoid import-time failures
_redis_conn = None
_followup_queue = None

def get_redis_connection():
    """Get or create Redis connection (lazy initialization)"""
    global _redis_conn
    if _redis_conn is None:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        try:
            _redis_conn = redis.from_url(redis_url, socket_connect_timeout=2, socket_timeout=2)
            _redis_conn.ping()
            logger.debug("Redis connection established for scheduler")
        except Exception as e:
            logger.warning(f"Redis connection failed for scheduler: {e}. Scheduler operations will be disabled.")
            _redis_conn = None
    return _redis_conn

def get_followup_queue():
    """Get or create followup queue (lazy initialization)"""
    global _followup_queue
    if _followup_queue is None:
        conn = get_redis_connection()
        if conn is None:
            return None
        try:
            _followup_queue = Queue("followup", connection=conn)
        except Exception as e:
            logger.warning(f"Failed to create followup queue: {e}")
            return None
    return _followup_queue

scheduler = AsyncIOScheduler()


def schedule_followups():
    """Schedule follow-up email job"""
    # TODO: Implement followup task in backend/app/tasks/followup.py
    logger.warning("Followup task not yet implemented in backend - scheduler job skipped")
    # When implemented, uncomment:
    # try:
    #     from app.tasks.followup import send_followups_task
    #     job_id = f"followup_{int(time.time())}"
    #     queue = get_followup_queue()
    #     if queue:
    #         queue.enqueue(send_followups_task, job_id)
    #         logger.info("Scheduled follow-up job")
    # except ImportError:
    #     logger.warning("Followup task not yet implemented")


def schedule_reply_check():
    """Schedule reply check job"""
    # TODO: Implement reply handler in backend/app/tasks/reply_handler.py
    logger.warning("Reply handler not yet implemented in backend - scheduler job skipped")
    # When implemented, uncomment:
    # try:
    #     from app.tasks.reply_handler import check_replies_task
    #     queue = get_followup_queue()
    #     if queue:
    #         queue.enqueue(check_replies_task)
    #         logger.info("Scheduled reply check job")
    # except ImportError:
    #     logger.warning("Reply handler not yet implemented")


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

