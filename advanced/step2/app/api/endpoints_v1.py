from fastapi import APIRouter, HTTPException, Query, Depends
import numpy as np
from typing import Dict, Any
import logging
from app.schemas.iris import (
    IrisFeatures, 
    IrisFeaturesArray, 
    PredictionResponse,
    ModelInfo,
    ErrorResponse
)

from app.services.model_service import ModelService
from app.utils.security import get_current_active_user

router = APIRouter()

# Set up logger
logger = logging.getLogger(__name__)

def get_model_service(
    model_name: str = Query(None, description="Model name"),
    version: str = Query(None, description="Model version")
) -> ModelService:
    """Get a model service instance with the specified model and version"""
    try:
        # Use the parameters if provided, otherwise use defaults
        model_name = model_name or None
        version = version or None
        
        # Create and return the model service
        return ModelService(model_name=model_name, version=version)
    except FileNotFoundError as e:
        raise ModelNotFoundError(
            model_name=model_name or "default", 
            version=version or "default"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading model: {str(e)}")

@router.get(
    "/", 
    summary="Root endpoint",
    description="Returns basic information about the API",
    tags=["General"],
    responses={
        200: {"description": "Successful response"}
    }
)
async def root():
    """
    Returns basic information about the API and links to documentation.
    """
    return {
        "message": "Welcome to the ML Model API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

@router.get("/info")
async def info():
    """Returns API information (v1)"""
    return {
        "version": "1.0",
        "model": "iris",
        "description": "Basic iris classification API"
    }

@router.post(
    "/predict",
    response_model=PredictionResponse,
    dependencies=[Depends(get_current_active_user)]
)
async def predict(
    features: IrisFeatures,
    model_service = Depends(get_model_service)
):
    """Make a prediction (v1)"""
    try:
        # Convert to numpy array
        input_features = np.array([
            [
                features.sepal_length,
                features.sepal_width,
                features.petal_length,
                features.petal_width
            ]
        ])
        
        # Make prediction
        result = model_service.predict(input_features)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))