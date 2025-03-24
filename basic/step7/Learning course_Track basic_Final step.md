# Step 7: Simple Deployment and Next Steps

## Objective
Learn how to deploy your ML API to make it accessible to others and implement basic monitoring to track its performance and usage.

## Context
Deploying your API allows others to access it from anywhere. Monitoring helps you understand how your API is being used and identify issues quickly. In this step, you'll learn basic deployment options and how to add simple monitoring to your API.

## Why it is required
Deployment and monitoring are essential for several reasons:
- Deployment makes your API accessible to users beyond your local machine
- Monitoring helps you track API usage, performance, and potential issues
- Both are necessary steps in taking your API from development to production
- They help ensure reliability and availability of your service
- Monitoring provides insights that can guide future improvements

## How to achieve this

### 1. Prepare your application for deployment:
Create a production configuration file `config_prod.py`:

```python
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")

# Model configuration
DEFAULT_MODEL = "iris"
DEFAULT_MODEL_VERSION = "v1"

# API configuration
API_TITLE = "Iris Classification API"
API_DESCRIPTION = "A simple API for ML model predictions"
API_VERSION = "0.1.0"

# Server configuration
HOST = "0.0.0.0"  # Listen on all available network interfaces
PORT = int(os.getenv("PORT", 8000))  # Use PORT environment variable or default to 8000
RELOAD = False  # Disable auto-reload in production
WORKERS = int(os.getenv("WORKERS", 1))  # Number of worker processes

# Security settings
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
```

### 2. Create a production server script:
Create a file `run_prod.py`:

```python
import uvicorn
import os
import logging
from app.main import app  # Import your FastAPI app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("api_prod.log")
    ]
)
logger = logging.getLogger("api_production")

def run_production_server():
    """Run the API server in production mode"""
    # Import the production config
    import config_prod as config
    
    logger.info(f"Starting production server on {config.HOST}:{config.PORT}")
    
    # Run the server
    uvicorn.run(
        "app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.RELOAD,
        workers=config.WORKERS,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    run_production_server()
```

### 3. Create a Docker deployment:
Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p models/iris/v1 logs

# Environment variables
ENV PORT=8000
ENV WORKERS=2

# Train the model
RUN python train_model.py

# Expose the port
EXPOSE 8000

# Run the application
CMD ["python", "run_prod.py"]
```

Create a `.dockerignore` file:

```
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.pytest_cache/
.coverage
htmlcov/
.git/
*.log
```

### 4. Add basic request monitoring:
Create a new file `app/utils/monitoring.py`:

```python
import time
import threading
import logging
from collections import deque, defaultdict
from typing import Dict, List, Deque, Any

logger = logging.getLogger(__name__)

class APIMonitor:
    """Simple in-memory API monitoring"""
    
    def __init__(self, max_requests: int = 1000):
        """
        Initialize the API monitor
        
        Args:
            max_requests: Maximum number of requests to keep in memory
        """
        self.max_requests = max_requests
        self.requests: Deque[Dict[str, Any]] = deque(maxlen=max_requests)
        self.endpoints: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"count": 0, "errors": 0, "total_time": 0})
        self.lock = threading.Lock()
        
        # Initialize counter variables
        self.total_requests = 0
        self.total_errors = 0
        self.start_time = time.time()
        
    def record_request(self, method: str, path: str, status_code: int, duration: float, error: str = None) -> None:
        """
        Record information about an API request
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            status_code: HTTP status code
            duration: Request duration in seconds
            error: Error message (if any)
        """
        # Create request record
        request = {
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration": duration,
            "timestamp": time.time(),
            "error": error
        }
        
        # Thread safety
        with self.lock:
            # Add to requests queue
            self.requests.append(request)
            
            # Update endpoint statistics
            self.endpoints[path]["count"] += 1
            self.endpoints[path]["total_time"] += duration
            
            if status_code >= 400:
                self.endpoints[path]["errors"] += 1
            
            # Update global counters
            self.total_requests += 1
            if status_code >= 400:
                self.total_errors += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get monitoring statistics
        
        Returns:
            Dictionary with monitoring statistics
        """
        with self.lock:
            uptime = time.time() - self.start_time
            
            # Calculate statistics
            stats = {
                "uptime_seconds": uptime,
                "uptime_human": self._format_uptime(uptime),
                "total_requests": self.total_requests,
                "total_errors": self.total_errors,
                "error_rate": (self.total_errors / self.total_requests * 100) if self.total_requests > 0 else 0,
                "requests_per_second": self.total_requests / uptime if uptime > 0 else 0,
                "endpoints": {}
            }
            
            # Calculate endpoint statistics
            for path, data in self.endpoints.items():
                avg_time = data["total_time"] / data["count"] if data["count"] > 0 else 0
                error_rate = (data["errors"] / data["count"] * 100) if data["count"] > 0 else 0
                
                stats["endpoints"][path] = {
                    "count": data["count"],
                    "errors": data["errors"],
                    "error_rate": error_rate,
                    "avg_response_time": avg_time
                }
            
            return stats
    
    def get_recent_requests(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent requests
        
        Args:
            limit: Maximum number of requests to return
            
        Returns:
            List of recent requests
        """
        with self.lock:
            return list(self.requests)[-limit:]
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent error requests
        
        Args:
            limit: Maximum number of error requests to return
            
        Returns:
            List of recent error requests
        """
        with self.lock:
            errors = [r for r in self.requests if r["status_code"] >= 400]
            return errors[-limit:]
    
    def _format_uptime(self, seconds: float) -> str:
        """
        Format uptime in human-readable format
        
        Args:
            seconds: Uptime in seconds
            
        Returns:
            Formatted uptime string
        """
        days, remainder = divmod(int(seconds), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days} days")
        if hours > 0:
            parts.append(f"{hours} hours")
        if minutes > 0:
            parts.append(f"{minutes} minutes")
        if seconds > 0 or not parts:
            parts.append(f"{seconds} seconds")
        
        return ", ".join(parts)

# Create a global monitor instance
monitor = APIMonitor()
```

Update `app/main.py` to use the monitor:

```python
import time
from app.utils.monitoring import monitor

# Add monitoring middleware (after rate limiting middleware)
@app.middleware("http")
async def monitoring_middleware(request: Request, call_next):
    """Record request for monitoring"""
    start_time = time.time()
    
    # Get request details
    method = request.method
    path = request.url.path
    
    # Process the request
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Record the request
        monitor.record_request(
            method=method,
            path=path,
            status_code=response.status_code,
            duration=duration
        )
        
        return response
    except Exception as e:
        # Record error request
        duration = time.time() - start_time
        monitor.record_request(
            method=method,
            path=path,
            status_code=500,
            duration=duration,
            error=str(e)
        )
        raise
```

### 5. Add monitoring endpoints:
Add to `app/api/endpoints.py`:

```python
from app.utils.monitoring import monitor

@router.get(
    "/metrics",
    summary="API metrics",
    description="Returns monitoring metrics for the API",
    tags=["Monitoring"],
    response_model=Dict[str, Any]
)
async def metrics():
    """
    Returns monitoring metrics for the API.
    
    Includes:
    - Uptime
    - Total requests
    - Error rate
    - Endpoint-specific metrics
    """
    return monitor.get_statistics()

@router.get(
    "/metrics/requests",
    summary="Recent requests",
    description="Returns information about recent API requests",
    tags=["Monitoring"],
    response_model=List[Dict[str, Any]]
)
async def recent_requests(limit: int = Query(10, ge=1, le=100)):
    """Returns information about the most recent API requests"""
    return monitor.get_recent_requests(limit=limit)

@router.get(
    "/metrics/errors",
    summary="Recent errors",
    description="Returns information about recent API errors",
    tags=["Monitoring"],
    response_model=List[Dict[str, Any]]
)
async def recent_errors(limit: int = Query(10, ge=1, le=100)):
    """Returns information about the most recent API errors"""
    return monitor.get_recent_errors(limit=limit)
```

### 6. Create a model monitoring dashboard:
Create `app/templates/dashboard.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>API Monitoring Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }
        .card {
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        .metric {
            font-size: 24px;
            font-weight: bold;
            margin: 10px 0;
        }
        .label {
            color: #666;
            font-size: 14px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .good {
            color: green;
        }
        .warning {
            color: orange;
        }
        .error {
            color: red;
        }
        .full-width {
            grid-column: 1 / -1;
        }
        .refresh-btn {
            padding: 8px 16px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-bottom: 20px;
        }
        .refresh-btn:hover {
            background-color: #45a049;
        }
        .last-update {
            font-style: italic;
            color: #666;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <h1>API Monitoring Dashboard</h1>
    
    <button id="refreshBtn" class="refresh-btn">Refresh Data</button>
    <div id="lastUpdate" class="last-update">Last updated: never</div>
    
    <div class="dashboard">
        <div class="card">
            <div class="label">Uptime</div>
            <div id="uptime" class="metric">-</div>
        </div>
        
        <div class="card">
            <div class="label">Total Requests</div>
            <div id="totalRequests" class="metric">-</div>
        </div>
        
        <div class="card">
            <div class="label">Requests Per Second</div>
            <div id="requestsPerSecond" class="metric">-</div>
        </div>
        
        <div class="card">
            <div class="label">Error Rate</div>
            <div id="errorRate" class="metric">-</div>
        </div>
        
        <div class="card full-width">
            <h2>Endpoint Statistics</h2>
            <table id="endpointTable">
                <thead>
                    <tr>
                        <th>Endpoint</th>
                        <th>Requests</th>
                        <th>Avg Response Time</th>
                        <th>Error Rate</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- Endpoint data will be inserted here -->
                </tbody>
            </table>
        </div>
        
        <div class="card full-width">
            <h2>Recent Requests</h2>
            <table id="requestsTable">
                <thead>
                    <tr>
                        <th>Method</th>
                        <th>Path</th>
                        <th>Status</th>
                        <th>Duration (ms)</th>
                        <th>Time</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- Request data will be inserted here -->
                </tbody>
            </table>
        </div>
        
        <div class="card full-width">
            <h2>Recent Errors</h2>
            <table id="errorsTable">
                <thead>
                    <tr>
                        <th>Method</th>
                        <th>Path</th>
                        <th>Status</th>
                        <th>Error</th>
                        <th>Time</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- Error data will be inserted here -->
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        // Function to fetch metrics
        async function fetchMetrics() {
            try {
                const response = await fetch('/metrics');
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('Error fetching metrics:', error);
                return null;
            }
        }
        
        // Function to fetch recent requests
        async function fetchRecentRequests() {
            try {
                const response = await fetch('/metrics/requests?limit=10');
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('Error fetching recent requests:', error);
                return [];
            }
        }
        
        // Function to fetch recent errors
        async function fetchRecentErrors() {
            try {
                const response = await fetch('/metrics/errors?limit=10');
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('Error fetching recent errors:', error);
                return [];
            }
        }
        
        // Update dashboard
        async function updateDashboard() {
            const metrics = await fetchMetrics();
            const recentRequests = await fetchRecentRequests();
            const recentErrors = await fetchRecentErrors();
            
            if (metrics) {
                // Update metrics
                document.getElementById('uptime').textContent = metrics.uptime_human;
                document.getElementById('totalRequests').textContent = metrics.total_requests;
                document.getElementById('requestsPerSecond').textContent = metrics.requests_per_second.toFixed(2);
                
                const errorRateElement = document.getElementById('errorRate');
                errorRateElement.textContent = metrics.error_rate.toFixed(2) + '%';
                
                // Set color based on error rate
                if (metrics.error_rate < 1) {
                    errorRateElement.className = 'metric good';
                } else if (metrics.error_rate < 5) {
                    errorRateElement.className = 'metric warning';
                } else {
                    errorRateElement.className = 'metric error';
                }
                
                // Update endpoint table
                const endpointTable = document.getElementById('endpointTable').getElementsByTagName('tbody')[0];
                endpointTable.innerHTML = '';
                
                for (const [path, data] of Object.entries(metrics.endpoints)) {
                    const row = endpointTable.insertRow();
                    
                    // Endpoint
                    const endpointCell = row.insertCell();
                    endpointCell.textContent = path;
                    
                    // Requests
                    const requestsCell = row.insertCell();
                    requestsCell.textContent = data.count;
                    
                    // Avg Response Time
                    const responseTimeCell = row.insertCell();
                    responseTimeCell.textContent = (data.avg_response_time * 1000).toFixed(2) + ' ms';
                    
                    // Error Rate
                    const errorRateCell = row.insertCell();
                    errorRateCell.textContent = data.error_rate.toFixed(2) + '%';
                    
                    // Set color based on error rate
                    if (data.error_rate < 1) {
                        errorRateCell.className = 'good';
                    } else if (data.error_rate < 5) {
                        errorRateCell.className = 'warning';
                    } else {
                        errorRateCell.className = 'error';
                    }
                }
            }
            
            // Update recent requests table
            const requestsTable = document.getElementById('requestsTable').getElementsByTagName('tbody')[0];
            requestsTable.innerHTML = '';
            
            for (const request of recentRequests) {
                const row = requestsTable.insertRow();
                
                // Method
                const methodCell = row.insertCell();
                methodCell.textContent = request.method;
                
                // Path
                const pathCell = row.insertCell();
                pathCell.textContent = request.path;
                
                // Status
                const statusCell = row.insertCell();
                statusCell.textContent = request.status_code;
                
                // Set color based on status code
                if (request.status_code < 300) {
                    statusCell.className = 'good';
                } else if (request.status_code < 400) {
                    statusCell.className = 'warning';
                } else {
                    statusCell.className = 'error';
                }
                
                // Duration
                const durationCell = row.insertCell();
                durationCell.textContent = (request.duration * 1000).toFixed(2) + ' ms';
                
                // Time
                const timeCell = row.insertCell();
                timeCell.textContent = new Date(request.timestamp * 1000).toLocaleTimeString();
            }
            
            // Update recent errors table
            const errorsTable = document.getElementById('errorsTable').getElementsByTagName('tbody')[0];
            errorsTable.innerHTML = '';
            
            for (const error of recentErrors) {
                const row = errorsTable.insertRow();
                
                // Method
                const methodCell = row.insertCell();
                methodCell.textContent = error.method;
                
                // Path
                const pathCell = row.insertCell();
                pathCell.textContent = error.path;
                
                // Status
                const statusCell = row.insertCell();
                statusCell.textContent = error.status_code;
                statusCell.className = 'error';
                
                // Error
                const errorCell = row.insertCell();
                errorCell.textContent = error.error || '(No error message)';
                
                // Time
                const timeCell = row.insertCell();
                timeCell.textContent = new Date(error.timestamp * 1000).toLocaleTimeString();
            }
            
            // Update last update time
            document.getElementById('lastUpdate').textContent = 'Last updated: ' + new Date().toLocaleTimeString();
        }
        
        // Initial update
        updateDashboard();
        
        // Set up auto-refresh
        setInterval(updateDashboard, 10000);  // Refresh every 10 seconds
        
        // Set up refresh button
        document.getElementById('refreshBtn').addEventListener('click', updateDashboard);
    </script>
</body>
</html>
```

Add a route for the dashboard:

```python
# app/main.py
@app.get("/dashboard", tags=["Monitoring"])
async def dashboard(request: Request):
    """
    Returns the monitoring dashboard.
    """
    return templates.TemplateResponse("dashboard.html", {"request": request})
```

### 7. Create a simple deployment guide:
Create a file `DEPLOYMENT.md`:

```markdown
# Deployment Guide

This guide explains how to deploy the Iris Classification API in different environments.

## Local Deployment

For local deployment during development:

```bash
# Run in development mode
uvicorn app.main:app --reload
```

For local production-like deployment:

```bash
# Run in production mode
python run_prod.py
```

## Docker Deployment

Build and run the Docker container:

```bash
# Build the Docker image
docker build -t iris-api .

# Run the container
docker run -p 8000:8000 iris-api
```

## Cloud Deployment

### Heroku

1. Install the Heroku CLI
2. Create a `Procfile`:
   ```
   web: python run_prod.py
   ```
3. Deploy to Heroku:
   ```bash
   heroku create iris-classification-api
   git push heroku main
   ```

### Google Cloud Run

1. Install the Google Cloud SDK
2. Build and push the Docker image:
   ```bash
   gcloud builds submit --tag gcr.io/[PROJECT-ID]/iris-api
   ```
3. Deploy to Cloud Run:
   ```bash
   gcloud run deploy iris-api --image gcr.io/[PROJECT-ID]/iris-api --platform managed
   ```

## Environment Variables

Configure these environment variables for deployment:

- `PORT`: Port to run the server on (default: 8000)
- `WORKERS`: Number of worker processes (default: 1)
- `ALLOWED_ORIGINS`: Comma-separated list of allowed origins for CORS (default: "*")

## Monitoring

Access the monitoring dashboard at `/dashboard`.

API metrics are available at:
- `/metrics`: Overall API metrics
- `/metrics/requests`: Recent requests
- `/metrics/errors`: Recent errors
```

## Examples of usage

### Running in production mode

```bash
# Run the production server
python run_prod.py
```

### Building and running with Docker

```bash
# Build the Docker image
docker build -t iris-api .

# Run the container
docker run -p 8000:8000 iris-api

# Access the API
curl http://localhost:8000/info
```

### Accessing the monitoring dashboard

1. Start the API server
2. Open a web browser and navigate to `http://localhost:8000/dashboard`
3. View real-time metrics, recent requests, and errors

### Using the monitoring API endpoints

```python
import requests

base_url = "http://localhost:8000"

# Get overall metrics
response = requests.get(f"{base_url}/metrics")
print("API Metrics:", response.json())

# Get recent requests
response = requests.get(f"{base_url}/metrics/requests?limit=5")
print("Recent Requests:", response.json())

# Get recent errors
response = requests.get(f"{base_url}/metrics/errors?limit=5")
print("Recent Errors:", response.json())
```

## Tasks for students

1. Implement the monitoring system in your API project
2. Create the monitoring dashboard and endpoints
3. Prepare your application for production using the provided configuration
4. Build and run your API using Docker
5. Test the monitoring dashboard by making various API requests
6. Create a simple load test to generate traffic to your API:
   - Use a script to make multiple requests in sequence or in parallel
   - Monitor the dashboard to see how the metrics change
7. Add another metric to the monitoring system, such as:
   - Average prediction time for the `/predict` endpoint
   - Most common predictions made by the model
   - Request counts by HTTP method (GET, POST, etc.)

## Solution (for instructors)

### Solution for Task 6: Simple load test script

```python
# load_test.py
import requests
import threading
import time
import random
import argparse
from typing import List, Dict

def make_request(url: str, data: Dict, timeout: int = 10) -> Dict:
    """Make a POST request to the prediction endpoint"""
    try:
        response = requests.post(url, json=data, timeout=timeout)
        return {
            "success": response.status_code < 400,
            "status_code": response.status_code,
            "response_time": response.elapsed.total_seconds(),
            "data": response.json() if response.status_code < 400 else None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def generate_sample() -> Dict:
    """Generate a random iris sample"""
    # Random but realistic iris measurements
    sepal_length = round(random.uniform(4.0, 8.0), 1)
    sepal_width = round(random.uniform(2.0, 4.5), 1)
    petal_length = round(random.uniform(1.0, 7.0), 1)
    petal_width = round(random.uniform(0.1, 2.5), 1)
    
    # Occasionally generate invalid data
    if random.random() < 0.05:  # 5% chance
        # Make one of the values negative
        if random.random() < 0.25:
            sepal_length = -sepal_length
        elif random.random() < 0.5:
            sepal_width = -sepal_width
        elif random.random() < 0.75:
            petal_length = -petal_length
        else:
            petal_width = -petal_width
    
    return {
        "sepal_length": sepal_length,
        "sepal_width": sepal_width,
        "petal_length": petal_length,
        "petal_width": petal_width
    }

def worker(base_url: str, requests_per_thread: int, delay: float, results: List):
    """Worker function to make requests"""
    for _ in range(requests_per_thread):
        # Choose endpoint
        if random.random() < 0.7:  # 70% for predict
            url = f"{base_url}/predict"
            data = generate_sample()
        elif random.random() < 0.9:  # 20% for batch
            url = f"{base_url}/predict/batch"
            data = [generate_sample() for _ in range(random.randint(1, 5))]
        else:  # 10% for array
            url = f"{base_url}/predict/array"
            sample = generate_sample()
            data = {
                "features": [
                    sample["sepal_length"],
                    sample["sepal_width"],
                    sample["petal_length"],
                    sample["petal_width"]
                ]
            }
        
        # Make request
        result = make_request(url, data)
        results.append(result)
        
        # Occasionally make non-prediction requests
        if random.random() < 0.2:  # 20% chance
            # Choose a GET endpoint
            endpoint = random.choice(["/info", "/health", "/metrics", "/versions"])
            try:
                requests.get(f"{base_url}{endpoint}")
            except:
                pass
        
        # Wait if delay is specified
        if delay > 0:
            time.sleep(delay)

def run_load_test(
    base_url: str = "http://localhost:8000",
    num_threads: int = 5,
    requests_per_thread: int = 20,
    delay: float = 0.1
):
    """
    Run a load test against the API
    
    Args:
        base_url: Base URL of the API
        num_threads: Number of concurrent threads
        requests_per_thread: Number of requests per thread
        delay: Delay between requests (in seconds)
    """
    print(f"Starting load test with {num_threads} threads, {requests_per_thread} requests per thread")
    print(f"Total requests: {num_threads * requests_per_thread}")
    print(f"Target: {base_url}")
    print(f"Delay between requests: {delay} seconds")
    print("-" * 50)
    
    # Create threads
    threads = []
    results = []
    
    start_time = time.time()
    
    for i in range(num_threads):
        t = threading.Thread(
            target=worker,
            args=(base_url, requests_per_thread, delay, results)
        )
        threads.append(t)
        t.start()
    
    # Wait for all threads to complete
    for t in threads:
        t.join()
    
    end_time = time.time()
    
    # Calculate statistics
    total_time = end_time - start_time
    total_requests = len(results)
    successful_requests = sum(1 for r in results if r.get("success", False))
    failed_requests = total_requests - successful_requests
    
    if total_requests > 0:
        success_rate = (successful_requests / total_requests) * 100
    else:
        success_rate = 0
    
    response_times = [r.get("response_time", 0) for r in results if "response_time" in r]
    
    if response_times:
        avg_response_time = sum(response_times) / len(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
    else:
        avg_response_time = min_response_time = max_response_time = 0
    
    # Print results
    print("\nLoad Test Results:")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Total requests: {total_requests}")
    print(f"Successful requests: {successful_requests} ({success_rate:.2f}%)")
    print(f"Failed requests: {failed_requests}")
    print(f"Requests per second: {total_requests / total_time:.2f}")
    
    if response_times:
        print(f"Average response time: {avg_response_time:.4f} seconds")
        print(f"Min response time: {min_response_time:.4f} seconds")
        print(f"Max response time: {max_response_time:.4f} seconds")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load test the Iris Classification API")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the API")
    parser.add_argument("--threads", type=int, default=5, help="Number of concurrent threads")
    parser.add_argument("--requests", type=int, default=20, help="Requests per thread")
    parser.add_argument("--delay", type=float, default=0.1, help="Delay between requests (seconds)")
    
    args = parser.parse_args()
    
    run_load_test(
        base_url=args.url,
        num_threads=args.threads,
        requests_per_thread=args.requests,
        delay=args.delay
    )
```

### Solution for Task 7: Additional monitoring metric

Add to `app/utils/monitoring.py`:

```python
class APIMonitor:
    def __init__(self, max_requests: int = 1000):
        # ... (existing code)
        
        # Add prediction tracking
        self.predictions: Dict[str, int] = defaultdict(int)
        self.prediction_times: List[float] = []
    
    def record_prediction(self, prediction: str, duration: float) -> None:
        """
        Record information about a prediction
        
        Args:
            prediction: Predicted class
            duration: Prediction duration in seconds
        """
        with self.lock:
            # Update prediction counter
            self.predictions[prediction] += 1
            
            # Record prediction time
            self.prediction_times.append(duration)
            
            # Keep only the last 1000 prediction times
            if len(self.prediction_times) > 1000:
                self.prediction_times.pop(0)
    
    def get_prediction_stats(self) -> Dict[str, Any]:
        """
        Get prediction statistics
        
        Returns:
            Dictionary with prediction statistics
        """
        with self.lock:
            # Calculate statistics
            total_predictions = sum(self.predictions.values())
            
            if self.prediction_times:
                avg_prediction_time = sum(self.prediction_times) / len(self.prediction_times)
                min_prediction_time = min(self.prediction_times)
                max_prediction_time = max(self.prediction_times)
            else:
                avg_prediction_time = min_prediction_time = max_prediction_time = 0
            
            # Get top predictions
            top_predictions = sorted(
                [(k, v) for k, v in self.predictions.items()],
                key=lambda x: x[1],
                reverse=True
            )
            
            return {
                "total_predictions": total_predictions,
                "avg_prediction_time": avg_prediction_time,
                "min_prediction_time": min_prediction_time,
                "max_prediction_time": max_prediction_time,
                "top_predictions": top_predictions[:5]  # Top 5 predictions
            }
```

Update the `predict` endpoint in `app/api/endpoints.py`:

```python
@router.post(
    "/predict", 
    response_model=PredictionResponse, 
    summary="Make a prediction", 
    tags=["Prediction"]
)
async def predict(
    features: IrisFeatures,
    model_service: ModelService = Depends(get_model_service)
):
    """Make a prediction based on the provided iris features"""
    try:
        start_time = time.time()
        
        # Convert to numpy array in the expected format
        input_features = np.array([
            [
                features.sepal_length, 
                features.sepal_width, 
                features.petal_length, 
                features.petal_width
            ]
        ])
        
        # Make prediction
        result = model_service.predict(input_features)
        
        # Record prediction for monitoring
        prediction_time = time.time() - start_time
        monitor.record_prediction(
            prediction=result["prediction"][0],
            duration=prediction_time
        )
        
        return result
    except Exception as e:
        # Exception handling code...
```

Add a new endpoint for prediction metrics:

```python
@router.get(
    "/metrics/predictions",
    summary="Prediction metrics",
    description="Returns metrics about model predictions",
    tags=["Monitoring"],
    response_model=Dict[str, Any]
)
async def prediction_metrics():
    """Returns metrics about model predictions"""
    return monitor.get_prediction_stats()
```

## Next steps

Congratulations on completing the learning track! You've built a complete ML model API with FastAPI and scikit-learn. Here are some advanced topics you might want to explore next:

1. **Advanced ML Models**: Try using more complex models like Random Forests, Gradient Boosting, or Neural Networks.

2. **CI/CD Pipeline**: Set up continuous integration and deployment for your API using tools like GitHub Actions or Jenkins.

3. **Advanced Authentication**: Implement more sophisticated authentication methods like OAuth2.

4. **Containerization and Orchestration**: Learn about orchestrating multiple containers with Kubernetes.

5. **Cloud Deployment**: Deploy your API to cloud platforms like AWS, Google Cloud, or Azure.

6. **Model Monitoring**: Implement advanced model monitoring to detect concept drift and model degradation.

7. **API Gateway**: Use an API gateway to manage multiple microservices.

8. **Database Integration**: Add a database to store predictions and user data.

9. **Asynchronous Processing**: Implement background tasks and message queues for long-running operations.

10. **A/B Testing**: Set up an infrastructure for comparing different model versions.

Remember, the skills you've learned in this track are transferable to many other data science and ML engineering projects. Good luck with your future endeavors!