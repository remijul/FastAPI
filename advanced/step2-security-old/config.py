import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")

# Model configuration
DEFAULT_MODEL = "iris"
DEFAULT_MODEL_VERSION = "v1"

# API configuration
API_TITLE = "Secure ML Model API"
API_DESCRIPTION = """
    This API provides iris flower classification using machine learning with authentication and authorization.
    
    ## Features
    
    * Predict iris species from sepal and petal measurements
    * Get information about the underlying ML model
    * Check available model versions
    
    ## Usage
    
    1. Use the `/predict` endpoint to classify a single iris sample
    2. Use the `/predict/batch` endpoint for multiple samples
    3. Check the API health with the `/health` endpoint
    
    The API is built with FastAPI and uses scikit-learn for machine learning.
    """
API_VERSION = "0.1.0"
API_TAGS = [
        {
            "name": "General",
            "description": "General operations for API information and health",
        },
        {
            "name": "Model",
            "description": "Operations related to the ML model information",
        },
        {
            "name": "Prediction",
            "description": "Endpoints for making predictions using the ML model",
        },
    ]



# Server configuration
HOST = "0.0.0.0"
PORT = 8000
RELOAD = True