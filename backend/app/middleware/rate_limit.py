"""
Rate Limiting Middleware for Morocco Judicial Digital System

Implements tiered rate limiting for different endpoints and user types:
- Login: 5 attempts/minute per IP (brute force protection)
- Registration: 3 attempts/hour per IP (spam protection) 
- Authenticated API: 100 requests/minute per user
- Anonymous API: 20 requests/minute per IP
- File uploads: 10 requests/hour per user
"""

from typing import Optional
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address


def get_user_identifier(request: Request) -> str:
    """
    Get rate limit identifier based on authentication status.
    
    For authenticated users: use user_id from token
    For anonymous users: use IP address
    
    This allows different rate limits for authenticated vs anonymous users.
    """
    # Try to get user from request state (set by auth dependency)
    user = getattr(request.state, "user", None)
    
    if user and hasattr(user, "id"):
        return f"user:{user.id}"
    
    # Fallback to IP for anonymous users
    return f"ip:{get_remote_address(request)}"


def get_ip_address(request: Request) -> str:
    """
    Get client IP address, handling proxy headers.
    
    Checks X-Forwarded-For and X-Real-IP headers for reverse proxy setups.
    """
    # Check proxy headers first
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take first IP from comma-separated list
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct client IP
    return get_remote_address(request)


# Rate limiter instances for different scenarios

# IP-based limiter for public endpoints (login, register, etc.)
ip_limiter = Limiter(
    key_func=get_ip_address,
    headers_enabled=True,  # Include X-RateLimit-* headers in response
)

# User/IP-based limiter for API endpoints
user_limiter = Limiter(
    key_func=get_user_identifier,
    headers_enabled=True,
)

# Strict limiter for sensitive operations
strict_limiter = Limiter(
    key_func=get_ip_address,
    headers_enabled=True,
)


def get_limiter_for_route(route_type: str) -> Limiter:
    """
    Get appropriate limiter based on route type.
    
    Args:
        route_type: One of 'ip', 'user', 'strict'
    
    Returns:
        Limiter instance
    """
    limiters = {
        "ip": ip_limiter,
        "user": user_limiter,
        "strict": strict_limiter,
    }
    return limiters.get(route_type, user_limiter)
