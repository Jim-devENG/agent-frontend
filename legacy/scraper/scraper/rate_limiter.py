"""
Rate limiting utilities for scrapers
"""
import time
from threading import Lock
from typing import Dict
from collections import defaultdict


class RateLimiter:
    """Simple rate limiter using token bucket algorithm"""
    
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum number of requests allowed
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = Lock()
    
    def wait_if_needed(self, key: str = "default"):
        """
        Wait if rate limit would be exceeded
        
        Args:
            key: Key to track rate limits (e.g., domain name)
        """
        with self.lock:
            now = time.time()
            # Remove old requests outside time window
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if now - req_time < self.time_window
            ]
            
            # If at limit, wait until oldest request expires
            if len(self.requests[key]) >= self.max_requests:
                oldest_request = min(self.requests[key])
                wait_time = self.time_window - (now - oldest_request) + 0.1
                if wait_time > 0:
                    time.sleep(wait_time)
                    # Clean up again after waiting
                    now = time.time()
                    self.requests[key] = [
                        req_time for req_time in self.requests[key]
                        if now - req_time < self.time_window
                    ]
            
            # Record this request
            self.requests[key].append(time.time())
    
    def reset(self, key: str = "default"):
        """Reset rate limit for a key"""
        with self.lock:
            if key in self.requests:
                del self.requests[key]

