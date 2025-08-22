FROM python:3.10-slim

WORKDIR /app
ENV PYTHONPATH=/app

RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy API requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/src ./src
COPY shared ./shared

CMD ["python", "src/api.py"]
