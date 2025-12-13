#!/usr/bin/env python3
"""
Postgres pinger / heartbeat service (Task 2).

Key behaviors:
 - Reads DB host/port/database from config.yaml (bundled).
 - Reads DB_USER, DB_PASSWORD, POLL_INTERVAL_SECONDS, CONNECT_TIMEOUT, LOG_DUPLICATE_PATH from environment.
 - Executes `SELECT VERSION();` every POLL_INTERVAL_SECONDS.
 - Successful connects & non-typical version responses -> stdout (INFO).
 - Failures -> stderr (ERROR).
 - Uses connect_timeout to avoid hanging (so next check still happens).
 - Optional duplication of logs to a file path if LOG_DUPLICATE_PATH is set.
"""

import os
import sys
import time
import logging
import yaml
import getpass
import traceback
import psycopg2
from logging import StreamHandler
from logging.handlers import RotatingFileHandler

# ---------------------------
# Config from env (highlighted lines map to Task 2 requirements)
# ---------------------------
CONFIG_PATH = os.environ.get("CONFIG_PATH", "/app/config.yaml")
# REQ 1.5: Poll interval (seconds). Default = 300 (5 minutes)
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL_SECONDS", "300"))
# REQ 1.4: Connect timeout to avoid hanging
CONNECT_TIMEOUT = int(os.environ.get("CONNECT_TIMEOUT", "10"))
# REQ 1.7: Optional duplicate log path
LOG_DUPLICATE_PATH = os.environ.get("LOG_DUPLICATE_PATH")
# REQ 1.6: Credentials read from environment
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

# ---------------------------
# Load config.yaml (host, port, database)
# ---------------------------
def load_config(path=CONFIG_PATH):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        print(f"Config file '{path}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as ex:
        print("Failed to load config:", ex, file=sys.stderr)
        sys.exit(1)

# ---------------------------
# Logger: stdout for INFO, stderr for WARN/ERROR; optional file duplication
# ---------------------------
def setup_logger(logfile=None):
    logger = logging.getLogger("pinger")
    logger.setLevel(logging.DEBUG)

    # stdout handler for INFO (successful & non-typical)
    h_out = StreamHandler(stream=sys.stdout)
    h_out.setLevel(logging.INFO)
    h_out.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(h_out)

    # stderr handler for WARNING/ERROR (failures)
    h_err = StreamHandler(stream=sys.stderr)
    h_err.setLevel(logging.WARNING)
    h_err.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(h_err)

    # Optional rotating file handler for duplication
    if logfile:
        try:
            fh = RotatingFileHandler(logfile, maxBytes=5*1024*1024, backupCount=3, encoding="utf-8")
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
            logger.addHandler(fh)
            logger.info(f"File logging enabled to: {logfile}")
        except Exception as e:
            logger.error(f"Failed to create log file '{logfile}': {e}")

    logger.propagate = False
    return logger

# ---------------------------
# Credentials fallback (local dev only)
# ---------------------------
def get_credentials():
    user = DB_USER
    pwd = DB_PASSWORD
    if not user:
        user = input("DB_USER not set. Enter DB username: ").strip()
    if not pwd:
        pwd = getpass.getpass("DB_PASSWORD not set. Enter DB password: ")
    return user, pwd

# ---------------------------
# Helpers
# ---------------------------
def is_typical_version(vstr):
    if not vstr:
        return False
    return vstr.strip().lower().startswith("postgresql ")

def check_once(cfg, user, pwd, connect_timeout, logger):
    # Build safe connection parameters (only safe keys; user cannot inject arbitrary options)
    conn_kwargs = {
        "host": cfg.get("host", "localhost"),
        "port": int(cfg.get("port", 5432)),
        "dbname": cfg.get("database", "postgres"),
        "user": user,
        "password": pwd,
        # REQ 1.4: ensure connect doesn't hang indefinitely
        "connect_timeout": connect_timeout
    }
    try:
        conn = psycopg2.connect(**conn_kwargs)
        with conn.cursor() as cur:
            cur.execute("SELECT VERSION();")
            row = cur.fetchone()
            if row:
                version = row[0]
                if is_typical_version(version):
                    # REQ 1.2: successful connection logged to stdout as INFO
                    logger.info(f"Successful connect. PostgreSQL version: {version}")
                else:
                    # REQ 1.3: non-typical version response logged to stdout (INFO)
                    logger.info(f"Connected. Non-typical version response: {version}")
            else:
                logger.info("Connected but no version string returned.")
        conn.close()
        return True
    except Exception as e:
        tb = traceback.format_exc()
        # REQ 1.2: failures logged to stderr as ERROR (handler routes error to stderr)
        logger.error(f"Connection failed: {e}\n{tb}")
        return False

def main():
    cfg = load_config()
    logger = setup_logger(LOG_DUPLICATE_PATH)
    user, pwd = get_credentials()

    logger.info("Starting Postgres pinger service")
    logger.debug(f"Config: host={cfg.get('host')}, port={cfg.get('port')}, database={cfg.get('database')}")
    logger.debug(f"POLL_INTERVAL_SECONDS={POLL_INTERVAL}, CONNECT_TIMEOUT={CONNECT_TIMEOUT}")

    while True:
        start = time.time()
        try:
            check_once(cfg, user, pwd, CONNECT_TIMEOUT, logger)
        except Exception as e:
            logger.error(f"Unexpected error in check loop: {e}\n{traceback.format_exc()}")

        elapsed = time.time() - start
        # Ensure interval between checks = POLL_INTERVAL (REQ 1.5)
        remaining = max(0, POLL_INTERVAL - elapsed)
        try:
            time.sleep(remaining)
        except KeyboardInterrupt:
            logger.info("Interrupted, exiting.")
            break

if __name__ == "__main__":
    main()
