"""Incremental load of FRED series into raw.fred_observations.

Run it from the project folder, with Postgres running:  python -m pipeline.load
"""

from datetime import date

import pandas as pd
import psycopg

from pipeline.db import connect, create_tables
from pipeline.fred import fetch_series

# The series this project loads. Adding one is a one-line change.
SERIES = ["HPIPONM226S", "MORTGAGE30US"]

# FRED revises published values, so every load also rereads the months before the watermark.
LOOKBACK_MONTHS = 12

# IS DISTINCT FROM also compares NULLs, so loaded_at changes only when the value really does.
UPSERT = """
    INSERT INTO raw.fred_observations AS stored (series_id, date, value)
    VALUES (%s, %s, %s)
    ON CONFLICT (series_id, date) DO UPDATE
        SET value = excluded.value, loaded_at = now()
        WHERE stored.value IS DISTINCT FROM excluded.value
"""


def download_start(watermark: date | None, lookback_months: int = LOOKBACK_MONTHS) -> date | None:
    """Return the first date to download, or None to download everything."""
    if watermark is None:
        return None
    return (pd.Timestamp(watermark) - pd.DateOffset(months=lookback_months)).date()


def read_watermark(conn: psycopg.Connection, series_id: str) -> date | None:
    """Return the newest stored date of a series, or None when it has no rows."""
    query = "SELECT max(date) FROM raw.fred_observations WHERE series_id = %s"
    return conn.execute(query, (series_id,)).fetchone()[0]


def upsert(conn: psycopg.Connection, series_id: str, table: pd.DataFrame) -> int:
    """Insert new rows, update revised ones, and return how many rows changed."""
    # NUMERIC would store NaN as a number, so blanks become None (NULL).
    rows = [
        (series_id, day.date(), None if pd.isna(value) else value)
        for day, value in zip(table["date"], table["value"])
    ]
    with conn.cursor() as cursor:
        cursor.executemany(UPSERT, rows)
        return cursor.rowcount


def load_series(conn: psycopg.Connection, series_id: str, fetch=fetch_series) -> int:
    """Download what is new for one series, upsert it, and return how many rows changed."""
    start_date = download_start(read_watermark(conn, series_id), LOOKBACK_MONTHS)
    table = fetch(series_id, start=start_date)
    return upsert(conn, series_id, table)


def load_all(conn: psycopg.Connection, series_ids=SERIES, fetch=fetch_series) -> dict[str, int]:
    """Load every series and return the changed rows per series. The caller commits."""
    create_tables(conn)
    return {series_id: load_series(conn, series_id, fetch=fetch) for series_id in series_ids}


def main() -> None:
    # One transaction for the whole run: the with-block commits at the end, or rolls back
    # everything if any series fails, so the table never holds half a run.
    with connect() as conn:
        for series_id, changed in load_all(conn).items():
            print(f"{series_id}: {changed} rows changed")


if __name__ == "__main__":
    main()
