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
API_TITLE = "ML Model API"
API_DESCRIPTION = "A simple API for ML model predictions"
API_VERSION = "0.1.0"

# Server configuration
HOST = "0.0.0.0"
PORT = 8000
RELOAD = True