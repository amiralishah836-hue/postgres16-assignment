# pinger-app Dockerfile (Task 2)
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY pinger.py /app/pinger.py
COPY config.yaml /app/config.yaml

RUN chmod +x /app/pinger.py

# Defaults (can be overridden via env_file)
ENV POLL_INTERVAL_SECONDS=300
ENV CONNECT_TIMEOUT=10
ENV CONFIG_PATH=/app/config.yaml

ENTRYPOINT ["python", "/app/pinger.py"]
