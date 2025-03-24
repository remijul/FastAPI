import numpy as np

def sanitize_input_features(features: np.ndarray) -> np.ndarray:
    """
    Sanitize and validate input features
    
    Args:
        features: Input feature array
        
    Returns:
        Sanitized features
        
    Raises:
        ValueError: If input is invalid
    """
    # Check if input is a numpy array
    if not isinstance(features, np.ndarray):
        raise ValueError("Input must be a numpy array")
    
    # Check dimensions
    if features.ndim != 2:
        raise ValueError(f"Expected 2D array, got {features.ndim}D")
    
    if features.shape[1] != 4:
        raise ValueError(f"Expected 4 features, got {features.shape[1]}")
    
    # Check for NaN or infinity
    if np.any(np.isnan(features)) or np.any(np.isinf(features)):
        raise ValueError("Input contains NaN or infinity values")
    
    # Check for negatives
    if np.any(features < 0):
        raise ValueError("Input contains negative values")
    
    # Check for unreasonably large values
    if np.any(features > 30):
        raise ValueError("Input contains unreasonably large values (>30cm)")
    
    # Ensure correct data type (float)
    return features.astype(np.float32)