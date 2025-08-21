# Dockerfile
FROM python:3.10-slim

# Set workdir
WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Default command (overwritten in docker-compose)
CMD ["python", "app.py"]
