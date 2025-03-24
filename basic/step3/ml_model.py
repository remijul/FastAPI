import numpy as np
import pandas as pd
import pickle
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

def train_and_save_model():
    """Train a model and save it to disk"""
    # Load and split the dataset
    iris = load_iris()
    X = iris.data
    y = iris.target
    feature_names = iris.feature_names
    target_names = iris.target_names
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    
    # Standardize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train the model
    model = KNeighborsClassifier(n_neighbors=5)
    model.fit(X_train_scaled, y_train)
    
    # Evaluate the model
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model accuracy: {accuracy:.2f}")
    
    # Save the model and scaler
    with open('iris_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    with open('iris_scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    
    # Save feature and target information
    model_info = {
        'feature_names': feature_names,
        'target_names': target_names,
        'test_accuracy': accuracy # Save the accuracy along with model info
    }
    
    with open('model_info.pkl', 'wb') as f:
        pickle.dump(model_info, f)
    
    print("Model, scaler, and model info saved to disk.")
    
    return model, scaler, model_info

def load_model():
    """Load the model and related objects from disk"""
    with open('iris_model.pkl', 'rb') as f:
        model = pickle.load(f)
    
    with open('iris_scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    
    with open('model_info.pkl', 'rb') as f:
        model_info = pickle.load(f)
    
    return model, scaler, model_info

def make_prediction(features, model, scaler, target_names):
    """Make a prediction using the trained model"""
    # Ensure features is a 2D array
    if isinstance(features, list):
        features = np.array([features])
    
    # Scale the features
    scaled_features = scaler.transform(features)
    
    # Make prediction
    prediction = model.predict(scaled_features)
    predicted_class = target_names[prediction[0]]
    
    # Get probability scores if the model supports it
    probabilities = None
    if hasattr(model, 'predict_proba'):
        probabilities = model.predict_proba(scaled_features)[0].tolist()
    
    return {
        'prediction': predicted_class,
        'prediction_index': int(prediction[0]),
        'probabilities': probabilities
    }

if __name__ == "__main__":
    train_and_save_model()