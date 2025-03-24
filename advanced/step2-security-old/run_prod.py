import uvicorn
import os
import logging
from app.main import app  # Import your FastAPI app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("api_prod.log")
    ]
)
logger = logging.getLogger("api_production")

def run_production_server():
    """Run the API server in production mode"""
    # Import the production config
    import config_prod as config
    
    logger.info(f"Starting production server on {config.HOST}:{config.PORT}")
    
    # Run the server
    uvicorn.run(
        "app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.RELOAD,
        workers=config.WORKERS,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    run_production_server()