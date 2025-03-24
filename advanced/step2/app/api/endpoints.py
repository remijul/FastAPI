from fastapi import APIRouter, HTTPException, Query, Depends, Path
import numpy as np
from typing import List, Dict, Any, Optional
import logging
from app.schemas.iris import (
    IrisFeatures, 
    IrisFeaturesArray, 
    PredictionResponse,
    ModelInfo,
    ErrorResponse
)
from app.services.model_service import ModelService
from app.utils.exceptions import ModelNotFoundError, InvalidInputError, PredictionError
from app.utils.monitoring import monitor
from app.utils.security import get_current_active_user, check_data_scientist_role

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

@router.get(
    "/info", 
    response_model=ModelInfo, 
    summary="Get model information", 
    tags=["Model"],
    responses={
        200: {"description": "Model information retrieved successfully"},
        404: {"description": "Model not found", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse}
    }
)
async def get_model_info(model_service: ModelService = Depends(get_model_service)):
    """Get information about the currently loaded model"""
    return model_service.get_model_info()

@router.get(
    "/versions", 
    summary="Get available model versions", 
    tags=["Model"],
    responses={
        200: {"description": "Versions retrieved successfully"},
        404: {"description": "Model not found", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse}
    }
)
async def get_versions(model_service: ModelService = Depends(get_model_service)):
    """Get a list of available model versions"""
    versions = model_service.get_available_versions()
    return {"versions": versions}

@router.post(
    "/predict", 
    response_model=PredictionResponse, 
    summary="Make a prediction",
    description="""
    Makes a prediction for the iris species based on the provided measurements.
    
    The model will return the predicted species and confidence scores.
    """,
    response_description="Prediction result with species name and confidence",
    tags=["Prediction"],
    responses={
        200: {"description": "Prediction successful"},
        400: {"description": "Invalid input", "model": ErrorResponse},
        404: {"description": "Model not found", "model": ErrorResponse},
        422: {"description": "Validation error", "model": ErrorResponse},
        500: {"description": "Prediction error", "model": ErrorResponse}
    }
)
async def predict(
    features: IrisFeatures,
    model_service: ModelService = Depends(get_model_service),
    current_user = Depends(get_current_active_user)  # Require authentication
):
    """
    Make a prediction based on the provided iris features
    
    - **sepal_length**: Length of the sepal in cm (must be > 0)
    - **sepal_width**: Width of the sepal in cm (must be > 0)
    - **petal_length**: Length of the petal in cm (must be > 0)
    - **petal_width**: Width of the petal in cm (must be > 0)
    
    Returns the predicted species and confidence scores.
    """
    # Log which user is making the prediction
    logger.info(f"User {current_user.username} ({current_user.email}) made a prediction")

    try:
        # Convert to numpy array in the expected format
        input_features = np.array([
            [
                features.sepal_length, 
                features.sepal_width, 
                features.petal_length, 
                features.petal_width
            ]
        ])
        
        # Perform additional validation
        if np.any(input_features < 0):
            raise InvalidInputError("All measurements must be positive")
        
        # Make prediction
        result = model_service.predict(input_features)
        
        return result
    except InvalidInputError:
        # Re-raise the caught exception
        raise
    except ValueError as e:
        # Convert ValueError to a more friendly error
        raise InvalidInputError(str(e))
    except Exception as e:
        # General prediction error
        raise PredictionError(str(e))

@router.post(
    "/predict/array", 
    response_model=PredictionResponse, 
    summary="Make a prediction from array", 
    tags=["Prediction"],
    responses={
        200: {"description": "Prediction successful"},
        400: {"description": "Invalid input", "model": ErrorResponse},
        404: {"description": "Model not found", "model": ErrorResponse},
        422: {"description": "Validation error", "model": ErrorResponse},
        500: {"description": "Prediction error", "model": ErrorResponse}
    }
)
async def predict_array(
    features: IrisFeaturesArray,
    model_service: ModelService = Depends(get_model_service)
):
    """Make a prediction based on a feature array [sepal_length, sepal_width, petal_length, petal_width]"""
    try:
        # Convert to numpy array in the expected format
        input_features = np.array([features.features])
        
        # Perform additional validation
        if np.any(input_features < 0):
            raise InvalidInputError("All measurements must be positive")
        
        # Make prediction
        result = model_service.predict(input_features)
        
        return result
    except InvalidInputError:
        # Re-raise the caught exception
        raise
    except ValueError as e:
        # Convert ValueError to a more friendly error
        raise InvalidInputError(str(e))
    except Exception as e:
        # General prediction error
        raise PredictionError(str(e))

@router.post(
    "/predict/batch", 
    response_model=List[PredictionResponse], 
    summary="Make batch predictions", 
    tags=["Prediction"],
    responses={
        200: {"description": "Batch prediction successful"},
        400: {"description": "Invalid input", "model": ErrorResponse},
        404: {"description": "Model not found", "model": ErrorResponse},
        422: {"description": "Validation error", "model": ErrorResponse},
        500: {"description": "Prediction error", "model": ErrorResponse}
    }
)
async def predict_batch(
    features_batch: List[IrisFeatures],
    model_service: ModelService = Depends(get_model_service)
):
    """Make predictions for a batch of samples"""
    try:
        # Check for empty batch
        if not features_batch:
            raise InvalidInputError("Batch cannot be empty")
            
        # Convert each item in the batch to a numpy array
        input_features = np.array([
            [
                features.sepal_length, 
                features.sepal_width, 
                features.petal_length, 
                features.petal_width
            ]
            for features in features_batch
        ])
        
        # Limit batch size for performance reasons
        if len(input_features) > 100:
            raise InvalidInputError("Batch size cannot exceed 100 samples")
        
        # Perform additional validation
        if np.any(input_features < 0):
            raise InvalidInputError("All measurements must be positive")
        
        # Make prediction
        result = model_service.predict(input_features)
        
        # Format for response
        results = []
        for i in range(len(input_features)):
            # Create individual results from the batch prediction
            item_result = {
                "prediction": [result["prediction"][i]],
                "prediction_index": [result["prediction_index"][i]],
            }
            
            if "probabilities" in result:
                item_result["probabilities"] = [result["probabilities"][i]]
                
            results.append(item_result)
        
        return results
    except InvalidInputError:
        # Re-raise the caught exception
        raise
    except ValueError as e:
        # Convert ValueError to a more friendly error
        raise InvalidInputError(str(e))
    except Exception as e:
        # General prediction error
        raise PredictionError(str(e))

@router.get(
    "/health", 
    summary="Check API health", 
    tags=["General"],
    responses={
        200: {"description": "API is healthy"},
        500: {"description": "API is unhealthy", "model": ErrorResponse}
    }
)
async def health_check():
    """Check the health status of the API"""
    try:
        # Try to load the default model to check if it's available
        model_service = ModelService()
        model_info = model_service.get_model_info()
        
        return {
            "status": "healthy",
            "model": model_info["model_name"],
            "version": model_info["version"],
            "model_type": model_info["model_type"]
        }
    except Exception as e:
        # If there's an error loading the model, the API is not healthy
        raise HTTPException(
            status_code=500, 
            detail={
                "status": "unhealthy",
                "error": str(e)
            }
        )

@router.get(
    "/metrics",
    summary="API metrics",
    description="Returns monitoring metrics for the API",
    tags=["Monitoring"],
    response_model=Dict[str, Any]
)
async def metrics():
    """
    Returns monitoring metrics for the API.
    
    Includes:
    - Uptime
    - Total requests
    - Error rate
    - Endpoint-specific metrics
    """
    return monitor.get_statistics()

@router.get(
    "/metrics/requests",
    summary="Recent requests",
    description="Returns information about recent API requests",
    tags=["Monitoring"],
    response_model=List[Dict[str, Any]]
)
async def recent_requests(limit: int = Query(10, ge=1, le=100)):
    """Returns information about the most recent API requests"""
    return monitor.get_recent_requests(limit=limit)

@router.get(
    "/metrics/errors",
    summary="Recent errors",
    description="Returns information about recent API errors",
    tags=["Monitoring"],
    response_model=List[Dict[str, Any]]
)
async def recent_errors(limit: int = Query(10, ge=1, le=100)):
    """Returns information about the most recent API errors"""
    return monitor.get_recent_errors(limit=limit)

# Admin-only endpoint for model management
@router.post(
    "/models/retrain",
    summary="Retrain the model",
    tags=["Model Management"]
)
async def retrain_model(
    model_name: str,
    model_service: ModelService = Depends(get_model_service),
    current_user = Depends(check_data_scientist_role)  # Require data scientist or admin role
):
    """Retrain the specified model (data scientist/admin only)"""
    # Your model retraining code here
    return {"message": f"Model {model_name} retraining initiated by {current_user.username}"}