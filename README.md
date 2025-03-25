![FastAPI logo](https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png) 

# ML API Development Learning Tracks

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-green.svg)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.0+-red.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

A comprehensive educational repository for learning how to build production-ready Machine Learning APIs using FastAPI and scikit-learn. This repository contains two learning tracks: a Basic Track for beginners and an Advanced Track for those looking to build more robust, secure APIs.

## 📚 Learning Tracks Overview

### Basic Track (7 Steps)
A progressive journey from basic API concepts to a complete ML model API:

1. **Introduction to FastAPI Basics** - First steps with the FastAPI framework
2. **Working with Data and Basic ML Concepts** - Loading data and building simple ML models
3. **Integrating ML Models with FastAPI** - Connecting ML models to API endpoints
4. **Model Persistence and Project Structure** - Saving/loading models and organizing code
5. **Input Validation and Error Handling** - Creating robust APIs with proper validation
6. **Basic Documentation and Testing** - Adding documentation and simple tests
7. **Simple Deployment and Next Steps** - Preparing the API for deployment

### Advanced Track (2 Steps)
Building on the Basic Track to add production-ready features:

1. **Authentication and Authorization** - Implementing JWT-based authentication and role-based access control
2. **API Testing and Version Control** - Creating comprehensive tests and managing API versions

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- Git (for version control)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ml-api-learning-tracks.git
cd ml-api-learning-tracks
```

2. Create and activate a virtual environment:
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database (for steps using authentication):
```bash
python init_db.py
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

### Docker Alternative

If you prefer using Docker:

```bash
docker build -t ml-api .
docker run -p 8000:8000 ml-api
```

## 📖 Learning Path Structure

### Basic Track

#### Step 1: Introduction to FastAPI Basics
- Setting up a FastAPI application
- Creating simple endpoints
- Path and query parameters
- Request and response models

#### Step 2: Working with Data and Basic ML Concepts
- Loading and exploring datasets
- Data preprocessing basics
- Training a simple classifier
- Model evaluation

#### Step 3: Integrating ML Models with FastAPI
- Creating prediction endpoints
- Handling model input/output
- Integrating scikit-learn models
- Basic error handling

#### Step 4: Model Persistence and Project Structure
- Saving and loading models
- Project organization best practices
- Managing model versions
- Creating a modular API structure

#### Step 5: Input Validation and Error Handling
- Pydantic models for validation
- Custom validators
- Error handling strategies
- Providing meaningful error messages

#### Step 6: Basic Documentation and Testing
- Automatic API documentation with OpenAPI
- Adding detailed endpoint descriptions
- Creating basic tests
- Manual vs automated testing

#### Step 7: Simple Deployment and Next Steps
- Preparing for deployment
- Docker containerization
- Basic monitoring
- Performance considerations

### Advanced Track

#### Step 1: Authentication and Authorization
- User management with database integration
- JWT token-based authentication
- Password hashing with bcrypt
- Role-based access control
- Protected endpoints

#### Step 2: API Testing and Version Control
- Path-based API versioning
- Maintaining backward compatibility
- Unit and integration testing
- Mock objects and dependencies
- Continuous Integration setup

## 🛠️ Project Structure

```
project-root/
│
├── app/                           # Main application package
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── api/                       # API endpoints
│   │   ├── __init__.py
│   │   ├── endpoints_v1.py        # Version 1 endpoints
│   │   └── endpoints_v2.py        # Version 2 endpoints
│   ├── db/                        # Database models and utilities
│   │   ├── __init__.py
│   │   └── database.py
│   ├── models/                    # Pydantic models
│   │   ├── __init__.py
│   │   ├── models.py              # Data models
│   │   └── user.py                # User models
│   ├── services/                  # Business logic services
│   │   ├── __init__.py
│   │   └── model_service.py       # ML model service
│   └── utils/                     # Utility functions
│       ├── __init__.py
│       ├── security.py            # Auth utilities
│       └── versioning.py          # API versioning utilities
│
├── tests/                         # Test files
│   ├── __init__.py
│   ├── test_api_v1.py             # V1 API tests
│   └── test_api_v1_v2.py          # Versioning tests
│
├── models/                        # Saved ML models
│   └── iris/
│       └── v1/
│
├── data/                          # Data files
│
├── .github/                       # GitHub configuration
│   └── workflows/
│       └── test.yml               # CI workflow
│
├── Dockerfile                     # Docker configuration
├── .gitignore
├── init_db.py                     # Database initialization script
├── requirements.txt               # Project dependencies
└── README.md                      # Project documentation
```

## 📝 Usage Examples

### Basic Prediction (v1)

```python
import requests

# Get an authentication token
response = requests.post(
    "http://localhost:8000/auth/token",
    data={
        "username": "user@example.com",
        "password": "SecureP@ss123"
    }
)
token = response.json()["access_token"]

# Make a prediction
headers = {"Authorization": f"Bearer {token}"}
data = {
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
}

response = requests.post(
    "http://localhost:8000/v1/predict",
    headers=headers,
    json=data
)

print(response.json())
```

### Enhanced Prediction (v2)

```python
import requests

# Get token (same as above)
# ...

# Make an enhanced prediction
response = requests.post(
    "http://localhost:8000/v2/predict",
    headers=headers,
    json={
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2,
        "include_importance": True
    }
)

print(response.json())
```

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api_v1.py

# Run with coverage report
pytest --cov=app
```

## 🤝 Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [scikit-learn Documentation](https://scikit-learn.org/stable/)
- [JWT Authentication](https://jwt.io/)
- [Docker Documentation](https://docs.docker.com/)
- [pytest Documentation](https://docs.pytest.org/)

## 👥 Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/) for the amazing web framework
- [scikit-learn](https://scikit-learn.org/) for machine learning tools
- All contributors and students who have helped improve this learning resource