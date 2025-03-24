import os
import numpy as np
import pandas as pd
import json
from datetime import datetime
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

from app.services.model_service import ModelService
import config

def train_iris_model(save: bool = True) -> tuple:
    """
    Train an Iris classification model and optionally save it
    
    Args:
        save: Whether to save the model
        
    Returns:
        Tuple of (model, scaler, metadata, accuracy)
    """
    print("Loading Iris dataset...")
    iris = load_iris()
    X = iris.data
    y = iris.target
    feature_names = iris.feature_names
    target_names = iris.target_names
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    
    # Standardize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train the model
    print("Training KNN classifier...")
    model = KNeighborsClassifier(n_neighbors=5)
    model.fit(X_train_scaled, y_train)
    
    # Evaluate the model
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model accuracy: {accuracy:.4f}")
    
    # Create metadata
    metadata = {
        "model_type": "KNeighborsClassifier",
        "feature_names": list(feature_names),
        "target_names": list(target_names),
        "params": model.get_params(),
        "accuracy": float(accuracy),
        "created_at": datetime.now().isoformat(),
        "dataset": "iris",
        "test_size": 0.3,
        "random_state": 42
    }
    
    # Save the model if requested
    if save:
        # Ensure the models directory exists
        model_dir = os.path.join(config.MODELS_DIR, "iris")
        os.makedirs(model_dir, exist_ok=True)
        
        # Use the model service to save everything
        model_service = ModelService(model_name="iris", load_existing=False)
        version = model_service.save_model(model, scaler, metadata, version="v1")
        print(f"Model saved as version: {version}")
    
    return model, scaler, metadata, accuracy

if __name__ == "__main__":
    train_iris_model(save=True)