import os
import json
import pickle
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Tuple, List, Optional

import config
from app.utils.helpers import sanitize_input_features

# Ensure the models directory exists
os.makedirs(os.path.join(config.MODELS_DIR, "iris", "v1"), exist_ok=True)

class ModelService:
    def __init__(self, model_name: str = None, version: str = None, load_existing: bool = True):
        self.model_name = model_name or config.DEFAULT_MODEL
        self.version = version or config.DEFAULT_MODEL_VERSION
        self.model = None
        self.scaler = None
        self.metadata = {}
        self.model_dir = os.path.join(config.MODELS_DIR, self.model_name, self.version)
        
        # Load the model only if requested
        if load_existing:
            self.load_model()
        
    def load_model(self) -> None:
        """Load model, scaler, and metadata from disk"""
        # If version is "latest", try to load the latest version from the text file
        if self.version == "latest":
            latest_file = os.path.join(config.MODELS_DIR, self.model_name, "latest.txt")
            if os.path.exists(latest_file):
                with open(latest_file, "r") as f:
                    self.version = f.read().strip()
                    self.model_dir = os.path.join(config.MODELS_DIR, self.model_name, self.version)
        
        # Check if model directory exists
        if not os.path.exists(self.model_dir):
            raise FileNotFoundError(f"Model directory not found: {self.model_dir}")
        
        # Load the model
        model_path = os.path.join(self.model_dir, "model.pkl")
        if os.path.exists(model_path):
            with open(model_path, "rb") as f:
                self.model = pickle.load(f)
        else:
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        # Load the scaler
        scaler_path = os.path.join(self.model_dir, "scaler.pkl")
        if os.path.exists(scaler_path):
            with open(scaler_path, "rb") as f:
                self.scaler = pickle.load(f)
        
        # Load the metadata
        metadata_path = os.path.join(self.model_dir, "metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                self.metadata = json.load(f)
    
    def save_model(self, model: Any, scaler: Any = None, metadata: Dict = None, 
                version: str = None) -> str:
        """Save model, scaler, and metadata to disk"""
        # If version is not provided, create a new version
        if version is None:
            # Generate a version name based on current timestamp
            version = f"v{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create the model directory
        model_dir = os.path.join(config.MODELS_DIR, self.model_name, version)
        os.makedirs(model_dir, exist_ok=True)
        
        # Save the model
        model_path = os.path.join(model_dir, "model.pkl")
        with open(model_path, "wb") as f:
            pickle.dump(model, f)
        
        # Save the scaler if provided
        if scaler is not None:
            scaler_path = os.path.join(model_dir, "scaler.pkl")
            with open(scaler_path, "wb") as f:
                pickle.dump(scaler, f)
        
        # Save the metadata if provided
        if metadata is not None:
            metadata_path = os.path.join(model_dir, "metadata.json")
            with open(metadata_path, "w") as f:
                json.dump(metadata, f)
        
        # Instead of using symlinks, create a text file that points to the latest version
        latest_file = os.path.join(config.MODELS_DIR, self.model_name, "latest.txt")
        with open(latest_file, "w") as f:
            f.write(version)
        
        return version
    
    def predict(self, features: np.ndarray) -> Dict[str, Any]:
        """Make a prediction using the loaded model"""
        if self.model is None:
            raise ValueError("Model not loaded")
        
        # Sanitize and validate input
        features = sanitize_input_features(features)
    
        # Scale the features if a scaler is available
        if self.scaler is not None:
            features = self.scaler.transform(features)
        
        # Make prediction
        prediction = self.model.predict(features)
        
        # Get prediction probabilities if available
        probabilities = None
        if hasattr(self.model, "predict_proba"):
            probabilities = self.model.predict_proba(features).tolist()
        
        # Get the class names if available
        target_names = self.metadata.get("target_names", ["Class " + str(i) for i in range(len(np.unique(prediction)))])
        
        # Format the response
        result = {
            "prediction": [target_names[i] for i in prediction.tolist()],
            "prediction_index": prediction.tolist(),
            "probabilities": probabilities,
            "model_version": self.version
        }
        
        if probabilities:
            result["probabilities"] = probabilities
        
        return result
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        return {
            "model_name": self.model_name,
            "version": self.version,
            "model_type": type(self.model).__name__ if self.model else None,
            "metadata": self.metadata,
            "feature_names": self.metadata.get("feature_names", []),
            "target_names": self.metadata.get("target_names", []),
            "created_at": self.metadata.get("created_at", None),
            "accuracy": self.metadata.get("accuracy", None)
        }
    
    def get_available_versions(self) -> List[str]:
        """Get a list of available model versions"""
        model_path = os.path.join(config.MODELS_DIR, self.model_name)
        
        if not os.path.exists(model_path):
            return []
        
        # Get directories that don't start with . and aren't 'latest'
        versions = [d for d in os.listdir(model_path) 
                   if os.path.isdir(os.path.join(model_path, d)) 
                   and not d.startswith(".") 
                   and d != "latest"]
        
        return sorted(versions)