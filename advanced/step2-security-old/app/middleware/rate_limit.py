from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
from collections import defaultdict
import threading

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiting implementation using sliding window"""
    
    def __init__(self, rate_limit, time_window):
        """
        Initialize rate limiter
        
        Args:
            rate_limit: Maximum number of requests allowed in the time window
            time_window: Time window in seconds
        """
        self.rate_limit = rate_limit
        self.time_window = time_window
        self.requests = defaultdict(list)  # client_identifier -> list of request timestamps
        self.lock = threading.Lock()
    
    def is_rate_limited(self, client_identifier):
        """
        Check if client is rate limited
        
        Args:
            client_identifier: Unique client identifier (e.g., IP address)
            
        Returns:
            tuple: (is_limited, current_count, limit)
        """
        with self.lock:
            # Get current time
            current_time = time.time()
            
            # Clean up old requests
            self.requests[client_identifier] = [
                timestamp for timestamp in self.requests[client_identifier] 
                if current_time - timestamp < self.time_window
            ]
            
            # Check rate limit
            current_count = len(self.requests[client_identifier])
            
            if current_count >= self.rate_limit:
                return True, current_count, self.rate_limit
            
            # Add current request
            self.requests[client_identifier].append(current_time)
            
            return False, current_count + 1, self.rate_limit

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to implement rate limiting"""
    
    def __init__(self, app, rate_limit=100, time_window=60):
        """
        Initialize middleware
        
        Args:
            app: FastAPI app
            rate_limit: Maximum number of requests allowed in the time window
            time_window: Time window in seconds
        """
        super().__init__(app)
        self.rate_limiter = RateLimiter(rate_limit, time_window)
    
    async def dispatch(self, request: Request, call_next):
        # Get client identifier (IP address)
        client_ip = request.client.host
        
        # Check rate limit
        is_limited, current, limit = self.rate_limiter.is_rate_limited(client_ip)
        
        if is_limited:
            logger.warning(f"Rate limit exceeded for client {client_ip}")
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later."
            )
        
        # Process the request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(limit - current)
        
        return response