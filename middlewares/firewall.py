from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

BLACKLIST_IPS = {"192.168.1.10", "10.0.0.5"}
WHITELIST_IPS = set()
BLOCKED_USER_AGENTS = {"curl", "scrapy", "bot"}
BLOCKED_PATHS = {"/admin/delete", "/danger"}

class FirewallMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print("Inside Firewall Middleware")
        client_ip = request.client.host
        user_agent = request.headers.get("User-Agent", "").lower()
        path = request.url.path.lower()

        # Blocked IPs
        if client_ip in BLACKLIST_IPS:
            raise HTTPException(status_code=403, detail="Access Denied: IP blocked")

        # Only allow whitelisted IPs (optional strict mode)
        if WHITELIST_IPS and client_ip not in WHITELIST_IPS:
            raise HTTPException(status_code=403, detail="IP not in whitelist")

        # Block bad user agents
        if any(bot in user_agent for bot in BLOCKED_USER_AGENTS):
            raise HTTPException(status_code=403, detail="Bot access blocked")

        # Block restricted paths
        if path in BLOCKED_PATHS:
            raise HTTPException(status_code=403, detail="Path blocked by firewall")

        return await call_next(request)
