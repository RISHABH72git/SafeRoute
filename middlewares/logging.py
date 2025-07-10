from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from sqlalchemy.orm import Session
from models.global_model import APILog, ApiKey
import json
from utils.db import get_db


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        db: Session = next(get_db())
        print("Inside Logging Middleware")
        client_ip = request.client.host
        path = str(request.url.path)
        method = request.method
        headers = dict(request.headers)
        api_key = request.headers.get("X-API-Key")
        try:
            body_bytes = await request.body()
            request_body = body_bytes.decode("utf-8")
        except Exception:
            request_body = ""

        # Proceed with request
        response = await call_next(request)
        # try:
        #     resp_body = b""
        #     async for chunk in response.body_iterator:
        #         resp_body += chunk
        # except Exception:
        #     resp_body = b""
        api_key_obj = db.query(ApiKey).filter(ApiKey.apikey == api_key).first()
        log = APILog(
            method=method,
            path=path,
            status_code=response.status_code,
            client_ip=client_ip,
            request_headers=json.dumps(headers),
            request_body=request_body,  # trim long bodies
            response_body="",
            apikey_id=api_key_obj.id,
        )
        try:
            db.add(log)
            db.commit()
        except Exception as e:
            print("Error logging API request:", str(e))

        return response
