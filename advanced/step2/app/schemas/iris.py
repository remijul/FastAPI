from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field, field_validator, model_validator
import numpy as np

class IrisFeatures(BaseModel):
    sepal_length: float = Field(..., gt=0, le=30, description="Sepal length in cm (0-30cm)")
    sepal_width: float = Field(..., gt=0, le=30, description="Sepal width in cm (0-30cm)")
    petal_length: float = Field(..., gt=0, le=30, description="Petal length in cm (0-30cm)")
    petal_width: float = Field(..., gt=0, le=30, description="Petal width in cm (0-30cm)")
    
    class ConfigDict:
        extra = "forbid"  # This will reject extra fields
        json_schema_extra = {
            "example": {
                "sepal_length": 5.1,
                "sepal_width": 3.5,
                "petal_length": 1.4,
                "petal_width": 0.2
            }
        }
    
    @field_validator('*')
    @classmethod
    def check_nan_inf(cls, v, info):
        if isinstance(v, float):
            if np.isnan(v) or np.isinf(v):
                raise ValueError(f"{info.field_name} must be a valid number (not NaN or infinity)")
        return v

    @model_validator(mode='after')
    def check_realistic_values(self):
        """Validate that values are within realistic ranges for iris flowers"""
        sepal_length = self.sepal_length
        sepal_width = self.sepal_width
        petal_length = self.petal_length
        petal_width = self.petal_width
        
        # Check if sepal length is always greater than petal length (common for iris)
        if sepal_length < petal_length:
            raise ValueError("Sepal length is typically greater than petal length for iris flowers")
        
        # Check if the combination of values makes biological sense
        if petal_length < 0.5 and petal_width > 0.5:
            raise ValueError("Unusual combination: very short petals are not typically wide")
            
        if sepal_length > 10:
            raise ValueError("Unusually large sepal length (>10cm). Verify your measurement.")
            
        return self

class IrisFeaturesArray(BaseModel):
    features: List[float] = Field(..., min_items=4, max_items=4, 
                               description="Array of 4 features: [sepal_length, sepal_width, petal_length, petal_width]")
    
    class ConfigDict:
        json_schema_extra = {
            "example": {
                "features": [5.1, 3.5, 1.4, 0.2]
            }
        }
    
    @field_validator('features')
    @classmethod
    def validate_features(cls, v):
        if len(v) != 4:
            raise ValueError("Features array must contain exactly 4 values")
        
        # Check individual feature values
        for i, feature in enumerate(v):
            if np.isnan(feature) or np.isinf(feature):
                raise ValueError(f"Feature {i+1} must be a valid number (not NaN or infinity)")
            
            if feature <= 0 or feature > 30:
                raise ValueError(f"Feature {i+1} must be between 0 and 30 cm")
        
        # Perform same biological checks as in IrisFeatures
        sepal_length, sepal_width, petal_length, petal_width = v
        
        if sepal_length < petal_length:
            raise ValueError("Sepal length is typically greater than petal length for iris flowers")
            
        if petal_length < 0.5 and petal_width > 0.5:
            raise ValueError("Unusual combination: very short petals are not typically wide")
            
        if sepal_length > 10:
            raise ValueError("Unusually large sepal length (>10cm). Verify your measurement.")
            
        return v

class PredictionResponse(BaseModel):
    prediction: List[str]
    prediction_index: List[int]
    probabilities: Optional[List[List[float]]] = None
    
    class ConfigDict:
        json_schema_extra = {
            "example": {
                "prediction": ["setosa"],
                "prediction_index": [0],
                "probabilities": [[0.95, 0.04, 0.01]]
            }
        }

class ModelInfo(BaseModel):
    model_name: str
    version: str
    model_type: Optional[str] = None
    feature_names: List[str]
    target_names: List[str]
    created_at: Optional[str] = None
    accuracy: Optional[float] = None
    
    class ConfigDict:
        protected_namespaces = ()  # Disable protected namespace warnings
        json_schema_extra = {
            "example": {
                "model_name": "iris",
                "version": "v1",
                "model_type": "KNeighborsClassifier",
                "feature_names": ["sepal length (cm)", "sepal width (cm)", "petal length (cm)", "petal width (cm)"],
                "target_names": ["setosa", "versicolor", "virginica"],
                "created_at": "2023-01-01T12:00:00",
                "accuracy": 0.97
            }
        }

# New schemas for error handling
class ErrorResponse(BaseModel):
    detail: Union[str, Dict[str, Any]]
    status_code: int
    
    class ConfigDict:
        json_schema_extra = {
            "example": {
                "detail": "Invalid input: sepal_length must be greater than 0",
                "status_code": 400
            }
        }

# V2 models with enhancements
class IrisFeaturesV2(IrisFeatures):
    """Enhanced input features (v2)"""
    include_importance: bool = Field(False, description="Include feature importance in response")

class PredictionResponseV2(PredictionResponse):
    """Enhanced prediction response (v2)"""
    feature_importance: Optional[Dict[str, float]] = None

# Error response model
class ErrorResponse(BaseModel):
    """Error response"""
    detail: str