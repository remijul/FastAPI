from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import traceback
import json
from pydantic import ValidationError

logger = logging.getLogger(__name__)

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors
    """
    # Log the error details
    logger.warning(f"Validation error: {exc}")
    
    # Extract error details in a clean format
    error_details = []
    for error in exc.errors():
        location = " -> ".join([str(loc) for loc in error["loc"]])
        error_details.append({
            "location": location,
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": error_details,
            "request_id": getattr(request.state, "request_id", None)
        }
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle HTTP exceptions
    """
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "Request error",
            "detail": exc.detail,
            "request_id": getattr(request.state, "request_id", None)
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle all other exceptions
    """
    # Get request details for logging
    method = request.method
    url = str(request.url)
    client_ip = request.client.host
    
    # Detailed error logging for monitoring
    logger.error(
        f"Unhandled exception: {exc}\n"
        f"Request: {method} {url}\n"
        f"Client: {client_ip}\n"
        f"Request ID: {getattr(request.state, 'request_id', None)}\n"
        f"{traceback.format_exc()}"
    )
    
    # Don't include internal error details in the response
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred",
            "request_id": getattr(request.state, "request_id", None)
        }
    )