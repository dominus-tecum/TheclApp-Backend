from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.sanitizer import sanitize_dict
import json

class SanitizationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Only sanitize POST, PUT, PATCH requests with JSON body
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.json()
                sanitized_body = sanitize_dict(body)
                # Replace request body with sanitized version
                request._body = json.dumps(sanitized_body).encode()
            except:
                pass
        
        response = await call_next(request)
        return response