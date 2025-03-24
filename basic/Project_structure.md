```
ml-api-project/
├── app/                           # Main application code
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints.py           # API route handlers
│   ├── models/
│   │   ├── __init__.py
│   │   └── iris_model.py          # ML model training logic
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── iris.py                # Pydantic data validation models
│   ├── services/
│   │   ├── __init__.py
│   │   └── model_service.py       # Model loading & prediction service
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── exceptions.py          # Custom exception handlers
│   │   ├── helpers.py             # Utility functions
│   │   ├── monitoring.py          # Monitoring utilities
│   │   └── rate_limit.py          # Rate limiting middleware
│   └── templates/
│       ├── dashboard.html         # Monitoring dashboard UI
│       └── documentation.html     # API documentation page
├── models/                        # Saved model files
│   └── iris/
│       ├── v1/                    # Version-specific model files
│       │   ├── model.pkl          # Serialized model
│       │   ├── scaler.pkl         # Serialized data scaler
│       │   └── metadata.json      # Model metadata
│       └── latest.txt             # Points to current version
├── data/                          # Data directory (if needed)
├── logs/                          # Log files
├── tests/                         # Test files
│   ├── __init__.py
│   └── test_api.py                # API tests
├── config.py                      # Development configuration
├── config_prod.py                 # Production configuration
├── requirements.txt               # Dependencies
├── Dockerfile                     # Container definition
├── train_model.py                 # Model training script
├── run_prod.py                    # Production server runner
├── load_test.py                   # Performance testing script
└── .dockerignore                  # Docker build exclusions
```