"""
Custom middleware for the application.
"""
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exceptions import MyChordHubException
from app.utils.logger import get_logger

logger = get_logger("middleware")


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware for handling application errors."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and handle errors."""
        try:
            response = await call_next(request)
            return response
        
        except MyChordHubException as e:
            logger.error(
                f"Application error: {e.message}",
                extra={
                    "status_code": e.status_code,
                    "details": e.details,
                    "path": request.url.path,
                    "method": request.method
                }
            )
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": e.message,
                    "details": e.details,
                    "status_code": e.status_code
                }
            )
        
        except Exception as e:
            logger.error(
                f"Unexpected error: {str(e)}",
                extra={
                    "path": request.url.path,
                    "method": request.method
                },
                exc_info=True
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": "An unexpected error occurred",
                    "status_code": 500
                }
            )


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response information."""
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request
        start_time = time.time()
        logger.info(
            f"Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query": str(request.query_params),
                "client_ip": request.client.host if request.client else None
            }
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Request completed",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "process_time": round(process_time, 4)
            }
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(round(process_time, 4))
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response."""
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Add HSTS header for HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response