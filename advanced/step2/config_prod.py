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
API_TITLE = "Iris Classification API"
API_DESCRIPTION = "A simple API for ML model predictions"
API_VERSION = "0.1.0"

# Server configuration
HOST = "0.0.0.0"  # Listen on all available network interfaces
PORT = int(os.getenv("PORT", 8000))  # Use PORT environment variable or default to 8000
RELOAD = False  # Disable auto-reload in production
WORKERS = int(os.getenv("WORKERS", 1))  # Number of worker processes

# Security settings
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")