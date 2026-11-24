"""Integration tests for the raw table. They need Postgres: docker compose up -d."""

import psycopg
import pytest

from pipeline.db import create_tables

pytestmark = pytest.mark.integration


def columns(db, schema, table):
    return db.execute(
        "SELECT column_name, data_type, is_nullable FROM information_schema.columns "
        "WHERE table_schema = %s AND table_name = %s ORDER BY ordinal_position",
        (schema, table),
    ).fetchall()


def test_create_tables_makes_the_raw_table(db):
    create_tables(db)

    assert columns(db, "raw", "fred_observations") == [
        ("series_id", "text", "NO"),
        ("date", "date", "NO"),
        ("value", "numeric", "YES"),
        ("loaded_at", "timestamp with time zone", "NO"),
    ]


def test_create_tables_can_run_twice(db):
    create_tables(db)
    create_tables(db)


def test_one_row_per_series_and_date(db):
    create_tables(db)
    db.execute("INSERT INTO raw.fred_observations (series_id, date, value) VALUES ('TEST', '2026-01-01', 1)")

    with pytest.raises(psycopg.errors.UniqueViolation):
        db.execute("INSERT INTO raw.fred_observations (series_id, date, value) VALUES ('TEST', '2026-01-01', 2)")


def test_a_missing_value_is_null_and_loaded_at_is_filled_in(db):
    create_tables(db)
    db.execute("INSERT INTO raw.fred_observations (series_id, date, value) VALUES ('TEST', '2026-01-01', NULL)")

    value, loaded_at = db.execute(
        "SELECT value, loaded_at FROM raw.fred_observations WHERE series_id = 'TEST'"
    ).fetchone()
    assert value is None
    assert loaded_at is not None
