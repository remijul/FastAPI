from fastapi import APIRouter, HTTPException, Query, Depends
import numpy as np
from typing import List, Dict, Any
import config

from app.schemas.iris import (
    IrisFeatures, 
    IrisFeaturesArray, 
    PredictionResponse,
    ModelInfo
)
from app.services.model_service import ModelService

router = APIRouter()

def get_model_service(
    model_name: str = Query(None, description="Model name"),
    version: str = Query(None, description="Model version")
) -> ModelService:
    """Get a model service instance with the specified model and version"""
    try:
        # Use the parameters if provided, otherwise use defaults from config
        model_name = model_name or config.DEFAULT_MODEL
        version = version or config.DEFAULT_MODEL_VERSION
        
        # Create and return the model service
        return ModelService(model_name=model_name, version=version)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading model: {str(e)}")

@router.get("/", summary="Root endpoint", tags=["General"])
async def root():
    """Root endpoint, provides basic API information"""
    return {
        "message": "Welcome to the ML Model API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

@router.get("/info", response_model=ModelInfo, summary="Get model information", tags=["Model"])
async def get_model_info(model_service: ModelService = Depends(get_model_service)):
    """Get information about the currently loaded model"""
    return model_service.get_model_info()

@router.get("/versions", summary="Get available model versions", tags=["Model"])
async def get_versions(model_service: ModelService = Depends(get_model_service)):
    """Get a list of available model versions"""
    versions = model_service.get_available_versions()
    return {"versions": versions}

@router.post("/predict", response_model=PredictionResponse, summary="Make a prediction", tags=["Prediction"])
async def predict(
    features: IrisFeatures,
    model_service: ModelService = Depends(get_model_service)
):
    """Make a prediction based on the provided iris features"""
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
        
        # Make prediction
        result = model_service.predict(input_features)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@router.post("/predict/array", response_model=PredictionResponse, summary="Make a prediction from array", tags=["Prediction"])
async def predict_array(
    features: IrisFeaturesArray,
    model_service: ModelService = Depends(get_model_service)
):
    """Make a prediction based on a feature array [sepal_length, sepal_width, petal_length, petal_width]"""
    try:
        # Convert to numpy array in the expected format
        input_features = np.array([features.features])
        
        # Make prediction
        result = model_service.predict(input_features)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@router.post("/predict/batch", response_model=List[PredictionResponse], summary="Make batch predictions", tags=["Prediction"])
async def predict_batch(
    features_batch: List[IrisFeatures],
    model_service: ModelService = Depends(get_model_service)
):
    """Make predictions for a batch of samples"""
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction error: {str(e)}")