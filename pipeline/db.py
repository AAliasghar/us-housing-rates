"""Connection to the project's Postgres and creation of its tables."""

import os
from pathlib import Path

import psycopg

SCHEMA_FILE = Path(__file__).resolve().parent.parent / "sql" / "raw_fred_observations.sql"

# Local defaults match docker-compose.yml. Any standard PG* variable that is set overrides them,
# so CI and Airflow can point the same code at another database without code changes.
DEFAULTS = {"PGHOST": "localhost", "PGPORT": "5433", "PGUSER": "housing", "PGPASSWORD": "housing", "PGDATABASE": "housing"}


def connect(**options) -> psycopg.Connection:
    """Open a connection using the PG* variables, falling back to the local defaults."""
    settings = {name: os.environ.get(name, default) for name, default in DEFAULTS.items()}
    return psycopg.connect(
        host=settings["PGHOST"],
        port=settings["PGPORT"],
        user=settings["PGUSER"],
        password=settings["PGPASSWORD"],
        dbname=settings["PGDATABASE"],
        **options,
    )


def create_tables(conn: psycopg.Connection) -> None:
    """Create the raw schema and table if they do not exist yet. Safe to run every time."""
    conn.execute(SCHEMA_FILE.read_text(encoding="utf-8"))
