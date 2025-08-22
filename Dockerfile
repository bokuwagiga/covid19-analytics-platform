# Dockerfile
FROM python:3.10-slim

# Set workdir
WORKDIR /app

# Ensure Python can find `src` as a package
ENV PYTHONPATH=/app/src

# Install system deps
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Default command (will usually be overridden by docker-compose)
CMD ["python", "src/app.py"]
