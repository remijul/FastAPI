from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
from typing import Union, Dict, Any

logger = logging.getLogger(__name__)

class ModelNotFoundError(HTTPException):
    def __init__(self, model_name: str, version: str = None):
        detail = f"Model '{model_name}' not found"
        if version:
            detail += f" with version '{version}'"
        super().__init__(status_code=404, detail=detail)

class InvalidInputError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=f"Invalid input: {detail}")

class PredictionError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=f"Prediction failed: {detail}")

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handler for HTTPException"""
    logger.error(f"HTTP error: {exc.status_code} - {exc.detail}")
    
    # Ensure detail is JSON serializable
    detail = str(exc.detail) if isinstance(exc.detail, Exception) else exc.detail
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": detail, "status_code": exc.status_code}
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler for RequestValidationError"""
    # Extract the validation errors
    error_details = []
    formatted_errors = []  # Create a JSON-serializable version
    
    for error in exc.errors():
        location = ".".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        error_details.append(f"{location}: {message}")
        
        # Create a JSON-serializable representation
        formatted_error = {
            "loc": [str(loc) for loc in error["loc"]],
            "msg": error["msg"],
            "type": error.get("type", "")
        }
        formatted_errors.append(formatted_error)
    
    detailed_error = "\n".join(error_details)
    logger.error(f"Validation error: {detailed_error}")
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": {
                "errors": formatted_errors,  # Use the serializable version
                "message": "Input validation error. Check your request format."
            },
            "status_code": 422
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handler for general exceptions"""
    logger.exception("Unhandled exception", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"Internal server error: {str(exc)}",
            "status_code": 500
        }
    )