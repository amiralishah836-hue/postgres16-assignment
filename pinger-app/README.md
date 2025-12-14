# Pinger App (Task 2)

This service polls PostgreSQL `SELECT VERSION();` every POLL_INTERVAL_SECONDS and logs results.

## Files
- pinger.py — main service
- config.yaml — host/port/database (no password)
- requirements.txt — Python deps
- Dockerfile — container image
- .env.pinger.example — example environment variables

## Env variables
- POLL_INTERVAL_SECONDS (default 300)
- CONNECT_TIMEOUT (default 10)
- DB_USER, DB_PASSWORD (required)
- LOG_DUPLICATE_PATH (optional, path inside container, use volumes to persist)

## Run (local)
1. Copy `.env.pinger.example` -> `.env.pinger` and set DB credentials.
2. `docker-compose up --build -d`
3. `docker logs -f pinger`

## Demo tips
- For demo set `POLL_INTERVAL_SECONDS=30` to speed up checks.
- To simulate failure, stop postgres container or set wrong password.
