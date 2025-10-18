"""Rate limiting middleware to prevent brute force attacks."""
from typing import Dict, Tuple
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
import asyncio


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using sliding window algorithm.
    
    Limits requests per IP address to prevent brute force attacks.
    """
    
    def __init__(self, app, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        
        # Store: {ip: [(timestamp, count)]}
        self.request_history: Dict[str, list] = defaultdict(list)
        
        # Sensitive endpoints that need stricter limits
        self.sensitive_endpoints = {
            "/api/v1/auth/login": (5, 20),  # 5/min, 20/hour
            "/api/v1/auth/refresh": (10, 50),  # 10/min, 50/hour
            "/api/v1/users/register": (3, 10),  # 3/min, 10/hour
        }
        
        # Start cleanup task
        asyncio.create_task(self._cleanup_old_entries())
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Get rate limits for this endpoint
        path = request.url.path
        if path in self.sensitive_endpoints:
            per_minute, per_hour = self.sensitive_endpoints[path]
        else:
            per_minute, per_hour = self.requests_per_minute, self.requests_per_hour
        
        # Check rate limits
        now = datetime.utcnow()
        
        # Clean old entries for this IP
        self._clean_ip_history(client_ip, now)
        
        # Count requests in time windows
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        
        history = self.request_history[client_ip]
        requests_last_minute = sum(1 for ts, _ in history if ts > minute_ago)
        requests_last_hour = sum(1 for ts, _ in history if ts > hour_ago)
        
        # Check limits
        if requests_last_minute >= per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {per_minute} requests per minute",
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int((now + timedelta(minutes=1)).timestamp()))
                }
            )
        
        if requests_last_hour >= per_hour:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {per_hour} requests per hour",
                headers={
                    "Retry-After": "3600",
                    "X-RateLimit-Limit": str(per_hour),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int((now + timedelta(hours=1)).timestamp()))
                }
            )
        
        # Record this request
        history.append((now, 1))
        
        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(per_minute)
        response.headers["X-RateLimit-Remaining"] = str(per_minute - requests_last_minute - 1)
        response.headers["X-RateLimit-Reset"] = str(int((now + timedelta(minutes=1)).timestamp()))
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request, considering proxies."""
        # Check X-Forwarded-For header (from proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Take the first IP (client IP)
            return forwarded.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct connection IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _clean_ip_history(self, ip: str, now: datetime):
        """Remove entries older than 1 hour for specific IP."""
        hour_ago = now - timedelta(hours=1)
        if ip in self.request_history:
            self.request_history[ip] = [
                (ts, count) for ts, count in self.request_history[ip]
                if ts > hour_ago
            ]
    
    async def _cleanup_old_entries(self):
        """Periodically clean up old entries to prevent memory leaks."""
        while True:
            await asyncio.sleep(300)  # Run every 5 minutes
            now = datetime.utcnow()
            hour_ago = now - timedelta(hours=1)
            
            # Clean all IPs
            for ip in list(self.request_history.keys()):
                self.request_history[ip] = [
                    (ts, count) for ts, count in self.request_history[ip]
                    if ts > hour_ago
                ]
                
                # Remove empty entries
                if not self.request_history[ip]:
                    del self.request_history[ip]
