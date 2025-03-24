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