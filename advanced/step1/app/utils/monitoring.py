import time
import threading
import logging
from collections import deque, defaultdict
from typing import Dict, List, Deque, Any

logger = logging.getLogger(__name__)

class APIMonitor:
    """Simple in-memory API monitoring"""
    
    def __init__(self, max_requests: int = 1000):
        """
        Initialize the API monitor
        
        Args:
            max_requests: Maximum number of requests to keep in memory
        """
        self.max_requests = max_requests
        self.requests: Deque[Dict[str, Any]] = deque(maxlen=max_requests)
        self.endpoints: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"count": 0, "errors": 0, "total_time": 0})
        self.lock = threading.Lock()
        
        # Initialize counter variables
        self.total_requests = 0
        self.total_errors = 0
        self.start_time = time.time()
        
    def record_request(self, method: str, path: str, status_code: int, duration: float, error: str = None) -> None:
        """
        Record information about an API request
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            status_code: HTTP status code
            duration: Request duration in seconds
            error: Error message (if any)
        """
        # Create request record
        request = {
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration": duration,
            "timestamp": time.time(),
            "error": error
        }
        
        # Thread safety
        with self.lock:
            # Add to requests queue
            self.requests.append(request)
            
            # Update endpoint statistics
            self.endpoints[path]["count"] += 1
            self.endpoints[path]["total_time"] += duration
            
            if status_code >= 400:
                self.endpoints[path]["errors"] += 1
            
            # Update global counters
            self.total_requests += 1
            if status_code >= 400:
                self.total_errors += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get monitoring statistics
        
        Returns:
            Dictionary with monitoring statistics
        """
        with self.lock:
            uptime = time.time() - self.start_time
            
            # Calculate statistics
            stats = {
                "uptime_seconds": uptime,
                "uptime_human": self._format_uptime(uptime),
                "total_requests": self.total_requests,
                "total_errors": self.total_errors,
                "error_rate": (self.total_errors / self.total_requests * 100) if self.total_requests > 0 else 0,
                "requests_per_second": self.total_requests / uptime if uptime > 0 else 0,
                "endpoints": {}
            }
            
            # Calculate endpoint statistics
            for path, data in self.endpoints.items():
                avg_time = data["total_time"] / data["count"] if data["count"] > 0 else 0
                error_rate = (data["errors"] / data["count"] * 100) if data["count"] > 0 else 0
                
                stats["endpoints"][path] = {
                    "count": data["count"],
                    "errors": data["errors"],
                    "error_rate": error_rate,
                    "avg_response_time": avg_time
                }
            
            return stats
    
    def get_recent_requests(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent requests
        
        Args:
            limit: Maximum number of requests to return
            
        Returns:
            List of recent requests
        """
        with self.lock:
            return list(self.requests)[-limit:]
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent error requests
        
        Args:
            limit: Maximum number of error requests to return
            
        Returns:
            List of recent error requests
        """
        with self.lock:
            errors = [r for r in self.requests if r["status_code"] >= 400]
            return errors[-limit:]
    
    def _format_uptime(self, seconds: float) -> str:
        """
        Format uptime in human-readable format
        
        Args:
            seconds: Uptime in seconds
            
        Returns:
            Formatted uptime string
        """
        days, remainder = divmod(int(seconds), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days} days")
        if hours > 0:
            parts.append(f"{hours} hours")
        if minutes > 0:
            parts.append(f"{minutes} minutes")
        if seconds > 0 or not parts:
            parts.append(f"{seconds} seconds")
        
        return ", ".join(parts)

# Create a global monitor instance
monitor = APIMonitor()