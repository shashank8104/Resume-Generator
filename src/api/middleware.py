"""Middleware for FastAPI application"""

import time
import uuid
from typing import Callable
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from ..utils.logging_utils import get_logger

logger = get_logger(__name__)

def setup_middleware(app: FastAPI):
    """Setup all middleware for the FastAPI application"""
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify exact origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Gzip compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Custom middleware
    app.middleware("http")(log_requests)
    app.middleware("http")(add_request_id)
    app.middleware("http")(add_security_headers)

async def log_requests(request: Request, call_next: Callable) -> Response:
    """Log all incoming requests and responses"""
    
    # Generate request ID
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Log incoming request
    logger.info(
        f"Request {request_id}: {request.method} {request.url} "
        f"from {request.client.host if request.client else 'unknown'}"
    )
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log response
    logger.info(
        f"Response {request_id}: {response.status_code} "
        f"in {process_time:.3f}s"
    )
    
    # Add processing time to response headers
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = request_id
    
    return response

async def add_request_id(request: Request, call_next: Callable) -> Response:
    """Add unique request ID to each request"""
    
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response

async def add_security_headers(request: Request, call_next: Callable) -> Response:
    """Add security headers to responses"""
    
    response = await call_next(request)
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    return response