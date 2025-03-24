from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import logging
from contextlib import asynccontextmanager
import time
import config

from app.api.endpoints import router as api_router
#from app.api import endpoints  # Your existing endpoints
from app.api import auth       # New auth module
from app.db.database import create_tables
from app.utils.exceptions import (
    http_exception_handler, 
    validation_exception_handler,
    general_exception_handler
)
from app.middleware.security import SecurityHeadersMiddleware, RequestIdMiddleware, TimingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.utils.error_handlers import (
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler
)
from app.utils.rate_limit import rate_limiter
from app.utils.monitoring import monitor
from app.utils.security import get_current_active_user, check_admin_role, check_data_scientist_role

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("api.log")
    ]
)
logger = logging.getLogger(__name__)

# Define lifespan context manager (replaces on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    logger.info("Starting up the API server...")
    yield
    # Shutdown code
    logger.info("Shutting down the API server...")
    # Create database tables on startup
    create_tables()

# Create FastAPI app
app = FastAPI(
    title=config.API_TITLE,
    description=config.API_DESCRIPTION,
    version=config.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=config.API_TAGS
)

'''
# Add exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)
'''

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com", "https://www.yourdomain.com"],  # Specify exact origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Limit to necessary methods
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining"],
    max_age=86400,  # Cache preflight requests for 24 hours
)

# Add security middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(TimingMiddleware)
app.add_middleware(RateLimitMiddleware, rate_limit=100, time_window=60)

# Configure custom error handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Add rate limiting middleware (add this before other middleware)
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting to all requests"""
    # Skip rate limiting for certain paths
    if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)
    
    return await call_next(request)

# Add monitoring middleware
@app.middleware("http")
async def monitoring_middleware(request: Request, call_next):
    """Record request for monitoring"""
    start_time = time.time()
    
    # Get request details
    method = request.method
    path = request.url.path
    
    # Process the request
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Record the request
        monitor.record_request(
            method=method,
            path=path,
            status_code=response.status_code,
            duration=duration
        )
        
        return response
    except Exception as e:
        # Record error request
        duration = time.time() - start_time
        monitor.record_request(
            method=method,
            path=path,
            status_code=500,
            duration=duration,
            error=str(e)
        )
        raise

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and their processing time"""
    import time
    
    start_time = time.time()
    
    # Get request details
    method = request.method
    url = request.url.path
    query_params = str(request.query_params)
    client_host = request.client.host if request.client else "unknown"
    
    logger.info(f"Request: {method} {url} - Client: {client_host} - Params: {query_params}")
    
    # Process the request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    formatted_process_time = "{:.2f}".format(process_time * 1000)
    
    logger.info(f"Response: {method} {url} - Status: {response.status_code} - Time: {formatted_process_time}ms")
    
    return response

@app.get("/documentation", tags=["General"])
async def documentation(request: Request):
    """
    Returns a detailed HTML documentation page for the API.
    """
    return templates.TemplateResponse("documentation.html", {"request": request})

@app.get("/dashboard", tags=["Monitoring"])
async def dashboard(request: Request):
    """
    Returns the monitoring dashboard.
    """
    return templates.TemplateResponse("dashboard.html", {"request": request})

# Add protected admin endpoints
@app.get("/admin", tags=["Admin"])
def admin_endpoint(current_user = Depends(check_admin_role)):
    """Endpoint only accessible to administrators"""
    return {"message": f"Hello admin {current_user.username}!"}

# Add protected data scientist endpoints
@app.get("/models/evaluate", tags=["Model Management"])
def evaluate_model(current_user = Depends(check_data_scientist_role)):
    """Endpoint accessible to data scientists and admins"""
    return {"message": f"Hello {current_user.role} {current_user.username}!"}

# Include routers
app.include_router(auth.router)
app.include_router(api_router,
    dependencies=[Depends(get_current_active_user)]  # All endpoints require authentication
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host=config.HOST, 
        port=config.PORT, 
        reload=config.RELOAD
    )