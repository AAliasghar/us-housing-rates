"""Shared test fixtures."""

import psycopg
import pytest


@pytest.fixture
def db():
    """A connection to the local Postgres, inside a transaction that is always rolled back.

    Tests that use it are skipped when Postgres is not reachable, so the unit tests still
    run anywhere. Nothing a test writes is ever kept.
    """
    from pipeline.db import connect

    try:
        conn = connect(connect_timeout=3)
    except psycopg.OperationalError as error:
        pytest.skip(f"Postgres not reachable: {error}")
    try:
        yield conn
    finally:
        conn.rollback()
        conn.close()
