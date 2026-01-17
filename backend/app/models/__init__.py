"""
Import all models here for Alembic to detect them
"""
from app.models.prospect import Prospect
from app.models.job import Job
from app.models.email_log import EmailLog
from app.models.settings import Settings
from app.models.discovery_query import DiscoveryQuery
from app.models.scraper_history import ScraperHistory
# Import social outreach models (separate system, but need to be in metadata)
from app.models.social import SocialProfile, SocialDiscoveryJob, SocialDraft, SocialMessage

__all__ = [
    "Prospect", "Job", "EmailLog", "Settings", "DiscoveryQuery", "ScraperHistory",
    "SocialProfile", "SocialDiscoveryJob", "SocialDraft", "SocialMessage"
]
