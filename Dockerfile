FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend Python scripts
COPY backend/ ./

# Copy the static frontend directory
COPY static/ ./static/

# Expose FastAPI port
EXPOSE 8000

# Start server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
