"""
Application settings management with database persistence
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from db.models import AppSettings
import json
import logging

logger = logging.getLogger(__name__)


class AppSettingsManager:
    """Manages application settings stored in database"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        setting = self.db.query(AppSettings).filter(AppSettings.key == key).first()
        if setting:
            try:
                # Try to parse as JSON, fallback to string
                return json.loads(setting.value)
            except (json.JSONDecodeError, TypeError):
                return setting.value
        return default
    
    def set(self, key: str, value: Any, description: Optional[str] = None):
        """Set a setting value"""
        try:
            # Convert value to JSON string if it's not a string
            if not isinstance(value, str):
                value_str = json.dumps(value)
            else:
                value_str = value
            
            setting = self.db.query(AppSettings).filter(AppSettings.key == key).first()
            if setting:
                setting.value = value_str
                if description:
                    setting.description = description
            else:
                setting = AppSettings(
                    key=key,
                    value=value_str,
                    description=description
                )
                self.db.add(setting)
            
            self.db.commit()
            logger.info(f"Setting updated: {key} = {value}")
        except Exception as e:
            logger.error(f"Failed to update setting {key}: {e}")
            self.db.rollback()
            raise
    
    def get_automation_enabled(self) -> bool:
        """Check if automation is enabled"""
        return self.get("automation_enabled", True)
    
    def set_automation_enabled(self, enabled: bool):
        """Enable or disable automation"""
        self.set("automation_enabled", enabled, "Master switch for all automation activities")
    
    def get_email_trigger_mode(self) -> str:
        """Get email trigger mode: 'automatic' or 'manual'"""
        return self.get("email_trigger_mode", "automatic")
    
    def set_email_trigger_mode(self, mode: str):
        """Set email trigger mode: 'automatic' or 'manual'"""
        if mode not in ["automatic", "manual"]:
            raise ValueError("Mode must be 'automatic' or 'manual'")
        self.set("email_trigger_mode", mode, "Email sending mode: automatic or manual")
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings as a dictionary"""
        settings = self.db.query(AppSettings).all()
        result = {}
        for setting in settings:
            try:
                result[setting.key] = json.loads(setting.value)
            except (json.JSONDecodeError, TypeError):
                result[setting.key] = setting.value
        return result
    
    def get_search_interval_seconds(self) -> int:
        """Get search interval in seconds (default: 900 = 15 minutes)"""
        return self.get("search_interval_seconds", 900)
    
    def set_search_interval_seconds(self, seconds: int):
        """Set search interval in seconds"""
        if seconds < 900:
            raise ValueError("Minimum interval is 900 seconds (15 minutes) to avoid rate limits")
        self.set("search_interval_seconds", seconds, "Interval between website discovery searches (seconds)")
    
    def get_automatic_scraper_enabled(self) -> bool:
        """Check if automatic scraper is enabled"""
        return self.get("automatic_scraper_enabled", False)
    
    def set_automatic_scraper_enabled(self, enabled: bool):
        """Enable or disable automatic scraper"""
        self.set("automatic_scraper_enabled", enabled, "Automatic scraper switch - runs searches at set intervals")

