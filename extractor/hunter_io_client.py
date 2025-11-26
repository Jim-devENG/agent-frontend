"""
Hunter.io API client for email finding and verification
"""
import requests
from typing import List, Dict, Optional
from utils.config import settings
import logging

logger = logging.getLogger(__name__)


class HunterIOClient:
    """Client for Hunter.io API"""
    
    BASE_URL = "https://api.hunter.io/v2"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Hunter.io client
        
        Args:
            api_key: Hunter.io API key (if None, uses HUNTER_IO_API_KEY from settings)
        """
        self.api_key = api_key or getattr(settings, 'HUNTER_IO_API_KEY', None)
        if not self.api_key:
            logger.warning("Hunter.io API key not configured. Set HUNTER_IO_API_KEY in .env")
    
    def is_configured(self) -> bool:
        """Check if API key is configured"""
        return self.api_key is not None
    
    def domain_search(self, domain: str, limit: int = 10) -> Dict:
        """
        Search for emails associated with a domain
        
        Args:
            domain: Domain to search (e.g., "liquidcanvas.art")
            limit: Maximum number of results
            
        Returns:
            Dictionary with emails and metadata
        """
        if not self.is_configured():
            return {"error": "Hunter.io API key not configured"}
        
        try:
            url = f"{self.BASE_URL}/domain-search"
            params = {
                "domain": domain,
                "api_key": self.api_key,
                "limit": limit
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("data"):
                emails = []
                for email_data in data["data"].get("emails", []):
                    emails.append({
                        "email": email_data.get("value"),
                        "type": email_data.get("type"),  # generic, personal
                        "confidence": email_data.get("confidence_score", 0),
                        "sources": email_data.get("sources", []),
                        "first_name": email_data.get("first_name"),
                        "last_name": email_data.get("last_name"),
                        "position": email_data.get("position"),
                        "linkedin": email_data.get("linkedin"),
                        "twitter": email_data.get("twitter"),
                    })
                
                return {
                    "success": True,
                    "domain": domain,
                    "emails": emails,
                    "total": data["data"].get("total", len(emails)),
                    "pattern": data["data"].get("pattern"),  # Email pattern like "{first}.{last}@domain.com"
                }
            else:
                return {
                    "success": False,
                    "error": data.get("errors", [{}])[0].get("details", "No emails found")
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Hunter.io API error: {str(e)}")
            return {"error": f"API request failed: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error in Hunter.io domain_search: {str(e)}")
            return {"error": str(e)}
    
    def email_finder(self, domain: str, first_name: Optional[str] = None, 
                    last_name: Optional[str] = None) -> Dict:
        """
        Find email for a specific person
        
        Args:
            domain: Domain name
            first_name: First name
            last_name: Last name
            
        Returns:
            Dictionary with found email and metadata
        """
        if not self.is_configured():
            return {"error": "Hunter.io API key not configured"}
        
        try:
            url = f"{self.BASE_URL}/email-finder"
            params = {
                "domain": domain,
                "api_key": self.api_key,
            }
            
            if first_name:
                params["first_name"] = first_name
            if last_name:
                params["last_name"] = last_name
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("data"):
                email_data = data["data"]
                return {
                    "success": True,
                    "email": email_data.get("email"),
                    "score": email_data.get("score", 0),
                    "sources": email_data.get("sources", []),
                    "first_name": email_data.get("first_name"),
                    "last_name": email_data.get("last_name"),
                    "position": email_data.get("position"),
                    "linkedin": email_data.get("linkedin"),
                    "twitter": email_data.get("twitter"),
                }
            else:
                return {
                    "success": False,
                    "error": data.get("errors", [{}])[0].get("details", "Email not found")
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Hunter.io API error: {str(e)}")
            return {"error": f"API request failed: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error in Hunter.io email_finder: {str(e)}")
            return {"error": str(e)}
    
    def verify_email(self, email: str) -> Dict:
        """
        Verify if an email address is valid and deliverable
        
        Args:
            email: Email address to verify
            
        Returns:
            Dictionary with verification results
        """
        if not self.is_configured():
            return {"error": "Hunter.io API key not configured"}
        
        try:
            url = f"{self.BASE_URL}/email-verifier"
            params = {
                "email": email,
                "api_key": self.api_key,
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("data"):
                verify_data = data["data"]
                return {
                    "success": True,
                    "email": verify_data.get("email"),
                    "result": verify_data.get("result"),  # deliverable, undeliverable, risky, unknown
                    "score": verify_data.get("score", 0),
                    "sources": verify_data.get("sources", []),
                }
            else:
                return {
                    "success": False,
                    "error": data.get("errors", [{}])[0].get("details", "Verification failed")
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Hunter.io API error: {str(e)}")
            return {"error": f"API request failed: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error in Hunter.io verify_email: {str(e)}")
            return {"error": str(e)}

