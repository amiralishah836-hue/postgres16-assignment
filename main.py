#!/usr/bin/env python3
import yaml
import psycopg2
import getpass
import sys

def load_config(path="config.yaml"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Config file '{path}' not found.")
        sys.exit(1)
    except Exception as ex:
        print("Failed to load config:", ex)
        sys.exit(1)

def main():
    cfg = load_config()

    print("=== PostgreSQL Connection App ===")
    # Prompt: username & password (do not store password)
    db_user = input(f"Username [{cfg.get('user','')}] : ").strip()
    if not db_user:
        db_user = cfg.get("user")

    db_password = getpass.getpass("Password: ")

    try:
        conn = psycopg2.connect(
            host=cfg["host"],
            port=cfg["port"],
            database=cfg["database"],
            user=db_user,
            password=db_password
        )

        with conn.cursor() as cur:
            cur.execute("SELECT VERSION();")
            version = cur.fetchone()
            print("\nConnected. PostgreSQL version:")
            print(version[0])

        conn.close()

    except Exception as e:
        print("\nConnection error:")
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    main()
