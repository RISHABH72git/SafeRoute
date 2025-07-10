from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session

from models.global_model import ApiKey
from utils.common import fixed_window
from utils.db import get_db


class RateLimiterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print("Inside RateLimiterMiddleware")
        all_path = request.url.path
        if not all_path.startswith('/users'):
            db: Session = next(get_db())
            api_key = request.headers.get("X-API-Key")
            if not api_key:
                raise HTTPException(status_code=400, detail="Missing API Key")

            api_key_obj = db.query(ApiKey).filter(ApiKey.apikey == api_key).first()
            if not api_key_obj:
                raise HTTPException(status_code=403, detail="Invalid API Key")

            key = f"ratelimit:{api_key}"
            allowed = await fixed_window(key, api_key_obj.limit_per_minute, 60)
            if not allowed:
                raise HTTPException(status_code=429, detail="Too many requests, Rate limit exceeded")

        return await call_next(request)
