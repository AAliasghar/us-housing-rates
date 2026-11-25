"""Integration tests for the watermark and the upsert. They need Postgres: docker compose up -d."""

from datetime import date
from decimal import Decimal

import pandas as pd
import pytest

from pipeline.db import create_tables
from pipeline.load import read_watermark, upsert

pytestmark = pytest.mark.integration

LONG_AGO = "2000-01-01 00:00+00"


@pytest.fixture
def raw(db):
    create_tables(db)
    return db


def table(rows):
    frame = pd.DataFrame(rows, columns=["date", "value"])
    frame["date"] = pd.to_datetime(frame["date"])
    frame["value"] = pd.to_numeric(frame["value"])
    return frame


def stored(conn, series_id):
    return conn.execute(
        "SELECT date, value FROM raw.fred_observations WHERE series_id = %s ORDER BY date", (series_id,)
    ).fetchall()


def make_old(conn, series_id):
    """Backdate loaded_at: now() stays the same inside one transaction, so a change would not show."""
    conn.execute("UPDATE raw.fred_observations SET loaded_at = %s WHERE series_id = %s", (LONG_AGO, series_id))


def count_old(conn, series_id):
    query = "SELECT count(*) FROM raw.fred_observations WHERE series_id = %s AND loaded_at = %s"
    return conn.execute(query, (series_id, LONG_AGO)).fetchone()[0]


def test_a_series_without_rows_has_no_watermark(raw):
    assert read_watermark(raw, "TEST") is None


def test_the_watermark_is_the_newest_date_of_that_series_only(raw):
    upsert(raw, "TEST", table([("2026-11-05", 7.18), ("2026-11-12", 7.20)]))
    upsert(raw, "OTHER", table([("2026-11-19", 1.0)]))

    assert read_watermark(raw, "TEST") == date(2026, 11, 12)


def test_new_rows_are_inserted(raw):
    changed = upsert(raw, "TEST", table([("2026-11-05", 7.18), ("2026-11-12", 7.20)]))

    assert changed == 2
    assert stored(raw, "TEST") == [(date(2026, 11, 5), Decimal("7.18")), (date(2026, 11, 12), Decimal("7.2"))]


def test_a_blank_value_is_stored_as_null_not_as_nan(raw):
    upsert(raw, "TEST", table([("2025-10-01", None)]))

    assert stored(raw, "TEST") == [(date(2025, 10, 1), None)]


def test_a_rerun_with_the_same_data_changes_nothing(raw):
    rows = table([("2026-11-05", 7.18), ("2026-11-12", None)])
    upsert(raw, "TEST", rows)
    make_old(raw, "TEST")

    assert upsert(raw, "TEST", rows) == 0
    assert count_old(raw, "TEST") == 2


def test_only_a_revised_value_is_updated(raw):
    upsert(raw, "TEST", table([("2026-07-01", 443.21), ("2026-08-01", 444.00)]))
    make_old(raw, "TEST")

    changed = upsert(raw, "TEST", table([("2026-07-01", 443.21), ("2026-08-01", 444.61)]))

    assert changed == 1
    assert stored(raw, "TEST")[1] == (date(2026, 8, 1), Decimal("444.61"))
    assert count_old(raw, "TEST") == 1


def test_a_blank_that_gets_a_value_later_is_updated(raw):
    upsert(raw, "TEST", table([("2025-10-01", None)]))

    assert upsert(raw, "TEST", table([("2025-10-01", 4.4)])) == 1
    assert stored(raw, "TEST") == [(date(2025, 10, 1), Decimal("4.4"))]


def test_an_empty_download_changes_nothing(raw):
    assert upsert(raw, "TEST", table([])) == 0
