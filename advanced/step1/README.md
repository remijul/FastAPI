# Iris Classification API

A simple ML model API built with FastAPI and scikit-learn for classifying iris flowers.

## Description

This project demonstrates how to create a production-ready API for machine learning models. It uses the classic Iris dataset to train a classifier that can predict the species of iris flowers based on their measurements.

## Features

- Predict iris species from measurements
- Get model information and available versions
- Batch prediction for multiple samples
- Input validation and error handling
- API documentation and testing

## Installation

### Prerequisites

- Python 3.7+
- pip

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/iris-classification-api.git
   cd iris-classification-api
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Train the model:
   ```
   python train_model.py
   ```

## Usage

### Running the API

```
python -m app.main
```

The API will be available at `http://localhost:8000`.

### API Documentation

- Interactive documentation: http://localhost:8000/docs
- Alternative documentation: http://localhost:8000/redoc
- Custom documentation: http://localhost:8000/documentation

### Making Predictions

#### Using curl:

```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}'
```

#### Using Python:

```python
import requests

# Make a prediction
data = {
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
}
response = requests.post("http://localhost:8000/predict", json=data)
print(response.json())
```

## Testing

Run the tests:

```
python run_tests.py
```

Or using pytest directly:

```
pytest -v tests/
```

## Project Structure

```
ml-api-project/
├── app/
│   ├── api/              # API endpoints
│   ├── models/           # ML model code
│   ├── schemas/          # Pydantic models
│   ├── services/         # Services for model management
│   ├── templates/        # HTML templates
│   ├── utils/            # Utility functions
│   └── main.py           # FastAPI application
├── models/               # Saved model files
├── tests/                # Test files
├── config.py             # Configuration
├── requirements.txt      # Dependencies
├── run_tests.py          # Test runner
└── train_model.py        # Model training script
```

## License

MIT