from fastapi import Request, HTTPException
import time
from typing import Dict, List, Tuple

class RateLimiter:
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        """
        Initialize a rate limiter
        
        Args:
            max_requests: Maximum number of requests allowed per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = {}  # client_id -> list of timestamps
    
    def is_rate_limited(self, request: Request) -> bool:
        """
        Check if a request is rate limited
        
        Args:
            request: The incoming request
            
        Returns:
            True if the request should be rate limited, False otherwise
        """
        # Get client identifier (IP address in this simple implementation)
        client_id = request.client.host if request.client else "unknown"
        
        # Get current time
        current_time = time.time()
        
        # Initialize client if not seen before
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Remove requests older than the window
        self.requests[client_id] = [
            timestamp for timestamp in self.requests[client_id]
            if current_time - timestamp < self.window_seconds
        ]
        
        # Check if client has exceeded rate limit
        if len(self.requests[client_id]) >= self.max_requests:
            return True
        
        # Record this request
        self.requests[client_id].append(current_time)
        
        return False

# Create a global rate limiter instance
rate_limiter = RateLimiter(max_requests=60, window_seconds=10)  # 60 requests per minute