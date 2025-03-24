# Iris Classification API: Process Flow

Here's a comprehensive overview of the project architecture and process flow, focusing on the complete implementation through step 7.

## Project Structure & Components

```txt
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

## Process Flows

### 1. Model Training Flow

```txt
[train_model.py] --> Load Iris Dataset --> Train Model --> Scale Features --> Evaluate Model 
  --> Create Metadata --> Save Model, Scaler, and Metadata to /models/iris/vX/ --> Update latest.txt
```

### 2. API Initialization Flow

```txt
[run_prod.py] --> Import app from app.main --> Load config_prod.py --> Start Uvicorn Server -->
  FastAPI App Startup --> Load Latest Model via ModelService --> Register Endpoints --> Ready
```

### 3. Prediction Request Flow

```
Client Request --> FastAPI Router --> Rate Limiting Middleware --> Input Validation (Pydantic) 
  --> ModelService.predict() --> Scale Features --> Model Prediction --> Format Response
  --> Record in Monitoring --> Return Prediction
```

### 4. Monitoring System Flow

```txt
API Request --> Process Request --> Record in APIMonitor 
  --> Update Metrics (endpoints, response times, error rates)
  --> Available via /metrics endpoint and Dashboard
```

### 5. Deployment Flow

```
Development --> Build Docker Image --> Push to Container Registry 
  --> Deploy to Target Environment (Cloud/On-Premise)
  --> Configure Environment Variables --> Start Container
```

## Key Services & Components

### ModelService (app/services/model_service.py)

- Core service that manages model loading, versioning, and prediction
- Handles model persistence and version management
- Provides prediction capabilities to API endpoints

### API Endpoints (app/api/endpoints.py)

- `/`: Root endpoint with basic info
- `/info`: Model information
- `/versions`: Available model versions
- `/predict`: Make single prediction
- `/predict/array`: Alternative input format
- `/predict/batch`: Process multiple samples
- `/health`: API health check
- `/metrics`: Monitoring metrics
- `/dashboard`: Visual monitoring interface
- `/documentation`: API documentation

### Monitoring System (app/utils/monitoring.py)

- Tracks request metrics:
  - Total requests and errors
  - Response times
  - Endpoint-specific statistics
  - Prediction distribution

- Provides real-time dashboard visualization
- Records errors for troubleshooting

### Exception Handling (app/utils/exceptions.py)

- Custom exception types for different error scenarios
- Consistent error responses
- Proper logging of issues

### Rate Limiting (app/utils/rate_limit.py)

- Protects API from abuse
- Client-specific request tracking
- Configurable thresholds

### Documentation

- Interactive Swagger UI (`/docs`)
- Alternative ReDoc UI (`/redoc`)
- Custom documentation page (`/documentation`)
- Comprehensive endpoint descriptions and examples

This structure provides a complete end-to-end solution from model training to deployment with monitoring and documentation, making it a production-ready ML API service.