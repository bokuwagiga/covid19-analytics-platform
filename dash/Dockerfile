FROM python:3.10-slim

WORKDIR /app
ENV PYTHONPATH=/app

RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY dash/src ./src
COPY shared ./shared

# run Dash via gunicorn, pointing to "server" inside src/app.py
CMD ["gunicorn", "-b", "0.0.0.0:8050", "src.app:server"]
