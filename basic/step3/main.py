from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import numpy as np
from ml_model import load_model, make_prediction

# Initialize FastAPI app
app = FastAPI(
    title="Iris Classifier API",
    description="A simple API for Iris flower classification",
    version="0.1.0"
)

# Load the model, scaler, and model info
model, scaler, model_info = load_model()
feature_names = model_info['feature_names']
target_names = model_info['target_names']

# Define the request model
class IrisFeatures(BaseModel):
    sepal_length: float = Field(..., gt=0, description="Sepal length in cm")
    sepal_width: float = Field(..., gt=0, description="Sepal width in cm")
    petal_length: float = Field(..., gt=0, description="Petal length in cm")
    petal_width: float = Field(..., gt=0, description="Petal width in cm")
    
    def to_array(self):
        return np.array([
            self.sepal_length,
            self.sepal_width,
            self.petal_length,
            self.petal_width
        ]).reshape(1, -1)

# Define the response model
class PredictionResponse(BaseModel):
    prediction: str
    prediction_index: int
    probabilities: Optional[List[float]] = None

# Root endpoint
@app.get("/", status_code=200)
async def root():
    return {
        #"status_code": status,
        "message": "Welcome to the Iris Classifier API",
        "model_type": type(model).__name__,
        "target_classes": target_names.tolist()
    }

# Model info endpoint
@app.get("/info")
async def model_information():
    return {
        "model_type": type(model).__name__,
        "features": feature_names.tolist(),
        "target_classes": target_names.tolist(),
        "target_class_mapping": {i: name for i, name in enumerate(target_names)}
    }

# Prediction endpoint
@app.post("/predict", response_model=PredictionResponse)
async def predict(features: IrisFeatures):
    try:
        # Convert the input data to the format expected by the model
        input_features = features.to_array()
        
        # Make prediction
        result = make_prediction(input_features, model, scaler, target_names)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

# Batch prediction endpoint
@app.post("/predict/batch", response_model=List[PredictionResponse])
async def predict_batch(features_batch: List[IrisFeatures]):
    try:
        # Convert each item in the batch to a numpy array
        input_features = np.array([features.to_array()[0] for features in features_batch])
        
        # Make predictions for each sample
        results = []
        for i in range(len(input_features)):
            result = make_prediction(
                input_features[i].reshape(1, -1), 
                model, 
                scaler, 
                target_names
            )
            results.append(result)
            
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction error: {str(e)}")

# Example endpoint
@app.get("/example")
async def example():
    """Return an example input that can be used for testing"""
    return {
        "example_input": {
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2
        },
        "expected_output": {
            "prediction": "setosa",
            "prediction_index": 0
        }
    }