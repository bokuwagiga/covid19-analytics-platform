FROM python:3.10-slim

WORKDIR /app
ENV PYTHONPATH=/app/src:/app

RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/src ./src
COPY shared ./shared

# run Flask API via gunicorn, pointing to "app" inside src/api.py
CMD ["gunicorn", "-b", "0.0.0.0:5000", "src.api:app"]
