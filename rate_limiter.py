from functools import wraps
from fastapi import HTTPException, Request
from typing import Dict
import time

# Simple in-memory rate limiter (for production, use Redis)
class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, list] = {}
    
    def is_allowed(self, key: str, max_requests: int = 5, window_seconds: int = 300) -> bool:
        """
        Check if request is allowed based on rate limit
        Args:
            key: Unique identifier (IP, user_id, etc.)
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
        """
        now = time.time()
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove old requests outside the window
        self.requests[key] = [req_time for req_time in self.requests[key] 
                             if now - req_time < window_seconds]
        
        # Check if limit exceeded
        if len(self.requests[key]) >= max_requests:
            return False
        
        # Add current request
        self.requests[key].append(now)
        return True

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(max_requests: int = 5, window_seconds: int = 300):
    """
    Rate limiting decorator
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            client_ip = request.client.host
            if not rate_limiter.is_allowed(client_ip, max_requests, window_seconds):
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Max {max_requests} requests per {window_seconds} seconds."
                )
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
