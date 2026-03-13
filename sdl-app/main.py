#!/usr/bin/env python3

import yaml
import psycopg2
import getpass
import os
import sys
import logging

# -----------------------
# Logging Setup
# -----------------------

LOG_DUPLICATE_PATH = os.environ.get("LOG_DUPLICATE_PATH")

def setup_logger():
    logger = logging.getLogger("sdl_app")
    logger.setLevel(logging.INFO)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    stdout_handler.setFormatter(formatter)
    stderr_handler.setFormatter(formatter)

    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)

    if LOG_DUPLICATE_PATH:
        file_handler = logging.FileHandler(LOG_DUPLICATE_PATH)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

logger = setup_logger()

# -----------------------
# Safe Whitelist
# -----------------------

ALLOWED_TABLES = {
    "projects": ["id", "name", "description", "owner", "created_at"],
    "threats": ["id", "project_id", "title", "threat_type", "severity", "status"],
    "vulnerabilities": ["id", "project_id", "name", "cvss_score", "status", "reported_at"],
    "mitigations": ["id", "threat_id", "control", "implemented", "verified"],
    "assessments": ["id", "project_id", "phase", "reviewer", "result", "review_date"]
}

# -----------------------
# Config Loader
# -----------------------

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

# -----------------------
# DB Connection
# -----------------------

def connect_db(cfg, user, password):
    try:
        conn = psycopg2.connect(
            host=cfg["host"],
            port=cfg["port"],
            database=cfg["database"],
            user=user,
            password=password,
            connect_timeout=10
        )
        logger.info("Connected to database successfully.")
        return conn
    except Exception:
        logger.error("Unable to connect to database.")
        sys.exit(1)

# -----------------------
# Column Validation
# -----------------------

def validate_column(table, column):
    return column in ALLOWED_TABLES.get(table, [])

# -----------------------
# View Table Data
# -----------------------

def view_table(conn):

    table = input("Enter table name: ").strip()

    if table not in ALLOWED_TABLES:
        logger.error("Invalid table name.")
        return

    filter_choice = input("Filter results? (yes/no): ").strip().lower()

    try:
        with conn.cursor() as cur:

            if filter_choice == "no":

                query = f"SELECT * FROM {table}"
                cur.execute(query)

            elif filter_choice == "yes":

                column = input("Column name: ").strip()

                if not validate_column(table, column):
                    logger.error("Invalid column name.")
                    return

                value = input("Value: ").strip()

                query = f"SELECT * FROM {table} WHERE {column} = %s"
                cur.execute(query, (value,))

            rows = cur.fetchall()

            for r in rows:
                print(r)

            logger.info("Query executed successfully.")

    except Exception:
        logger.error("Query failed.")

# -----------------------
# Single Insert
# -----------------------

def insert_row(conn):

    table = input("Table name: ").strip()

    if table not in ALLOWED_TABLES:
        logger.error("Invalid table.")
        return

    columns = []
    values = []

    for col in ALLOWED_TABLES[table]:

        if col == "id":
            continue

        value = input(f"{col}: ").strip()

        if value:
            columns.append(col)
            values.append(value)

    placeholders = ", ".join(["%s"] * len(values))
    column_str = ", ".join(columns)

    try:

        with conn.cursor() as cur:

            query = f"INSERT INTO {table} ({column_str}) VALUES ({placeholders})"
            cur.execute(query, values)

        conn.commit()

        logger.info("Insert successful.")

    except Exception:

        conn.rollback()
        logger.error("Insert failed.")

# -----------------------
# Multi Row Insert (6.4)
# -----------------------

def insert_multiple_rows(conn):

    table = input("Table name: ").strip()

    if table not in ALLOWED_TABLES:
        logger.error("Invalid table.")
        return

    column_input = input("Columns (comma separated): ")

    columns = [c.strip() for c in column_input.split(",")]

    for col in columns:
        if not validate_column(table, col):
            logger.error(f"Invalid column: {col}")
            return

    print("Enter rows. Type 'done' to stop.")

    rows = []

    while True:

        row_input = input("Row values: ")

        if row_input.lower() == "done":
            break

        values = tuple(v.strip() for v in row_input.split(","))

        if len(values) != len(columns):
            logger.error("Column count mismatch.")
            return

        rows.append(values)

    placeholders = ", ".join(["%s"] * len(columns))
    column_str = ", ".join(columns)

    query = f"INSERT INTO {table} ({column_str}) VALUES ({placeholders})"

    try:

        with conn.cursor() as cur:

            cur.executemany(query, rows)

        conn.commit()

        logger.info("Multi-row insert successful.")

    except Exception as e:

        conn.rollback()
        logger.error("Multi-row insert failed.")

# -----------------------
# Transactional Multi Table Insert (6.3.2)
# -----------------------

def transactional_insert(conn):

    try:

        conn.autocommit = False

        with conn.cursor() as cur:

            cur.execute(
                "INSERT INTO projects (name, description) VALUES (%s,%s) RETURNING id",
                ("Secure SDL Project", "Transactional insert demo")
            )

            project_id = cur.fetchone()[0]

            cur.execute(
                "INSERT INTO vulnerabilities (project_id,name,cvss_score,status) VALUES (%s,%s,%s,%s) RETURNING id",
                (project_id,"Insecure Logging",7.5,"Open")
            )

            vuln_id = cur.fetchone()[0]

            cur.execute(
                "INSERT INTO mitigations (threat_id,control,implemented,verified) VALUES (%s,%s,%s,%s)",
                (vuln_id,"Implement centralized logging",False,False)
            )

        conn.commit()

        logger.info("Transactional insert successful.")

    except Exception as e:

        conn.rollback()
        logger.error("Transaction failed.")

    finally:

        conn.autocommit = True

# -----------------------
# Update Row
# -----------------------

def update_row(conn):

    table = input("Table name: ").strip()

    if table not in ALLOWED_TABLES:
        logger.error("Invalid table.")
        return

    row_id = input("Row ID: ")

    updates = []
    values = []

    for col in ALLOWED_TABLES[table]:

        if col == "id":
            continue

        val = input(f"New value for {col} (skip empty): ").strip()

        if val:
            updates.append(f"{col}=%s")
            values.append(val)

    if not updates:
        print("Nothing to update.")
        return

    values.append(row_id)

    set_clause = ", ".join(updates)

    query = f"UPDATE {table} SET {set_clause} WHERE id=%s"

    try:

        with conn.cursor() as cur:
            cur.execute(query, values)

        conn.commit()

        logger.info("Update successful.")

    except Exception:

        conn.rollback()
        logger.error("Update failed.")

# -----------------------
# Menu
# -----------------------

def menu():

    print("\nSDL Secure Management System")

    print("1 View table")
    print("2 Insert row")
    print("3 Update row")
    print("4 Multi-row insert")
    print("5 Transactional multi-table insert")
    print("6 Exit")

# -----------------------
# Main
# -----------------------

def main():

    cfg = load_config()

    print("Secure SDL App")

    user = input("DB Username: ")
    password = getpass.getpass("DB Password: ")

    conn = connect_db(cfg, user, password)

    while True:

        menu()

        choice = input("Choice: ")

        if choice == "1":
            view_table(conn)

        elif choice == "2":
            insert_row(conn)

        elif choice == "3":
            update_row(conn)

        elif choice == "4":
            insert_multiple_rows(conn)

        elif choice == "5":
            transactional_insert(conn)

        elif choice == "6":
            print("Exiting...")
            break

        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()
