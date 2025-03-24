from typing import List, Optional
from pydantic import BaseModel, Field

class IrisFeatures(BaseModel):
    sepal_length: float = Field(..., gt=0, description="Sepal length in cm")
    sepal_width: float = Field(..., gt=0, description="Sepal width in cm")
    petal_length: float = Field(..., gt=0, description="Petal length in cm")
    petal_width: float = Field(..., gt=0, description="Petal width in cm")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sepal_length": 5.1,
                "sepal_width": 3.5,
                "petal_length": 1.4,
                "petal_width": 0.2
            }
        }

class IrisFeaturesArray(BaseModel):
    features: List[float] = Field(..., min_items=4, max_items=4, 
                               description="Array of 4 features: [sepal_length, sepal_width, petal_length, petal_width]")
    
    class Config:
        json_schema_extra = {
            "example": {
                "features": [5.1, 3.5, 1.4, 0.2]
            }
        }

class PredictionResponse(BaseModel):
    prediction: List[str]
    prediction_index: List[int]
    probabilities: Optional[List[List[float]]] = None

class ModelInfo(BaseModel):
    model_name: str
    version: str
    model_type: Optional[str] = None
    feature_names: List[str]
    target_names: List[str]
    created_at: Optional[str] = None
    accuracy: Optional[float] = None