"""Tests for save_table and load_table. Read this file first: it shows what the code must do.

ROAD MAP of this file
    Test 1  A saved table loads back exactly the same, blanks included.
    Test 2  Missing folders are created.
    Test 3  Dates come back as real dates, not text.
    Test 4  The file has no row numbers: it starts with the column names.

    tmp_path is a gift from pytest: a new, empty folder for each test, deleted later.
    So the tests never touch the real data/ folder.
"""

import pandas as pd

from pipeline.store import load_table, save_table


def joined_table():
    """A small table like the one join_series returns. The numbers are made up."""
    table = pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-07-01", "2026-08-01"]),
            "house_prices": [443.21, 444.61],
            "mortgage_rate": [6.542, None],
        }
    )
    return table


def test_a_saved_table_loads_back_exactly_the_same(tmp_path):
    path = tmp_path / "joined.csv"

    save_table(joined_table(), path)
    loaded = load_table(path)

    # assert_frame_equal compares every column, value, blank and type, and explains any difference.
    pd.testing.assert_frame_equal(loaded, joined_table())


def test_missing_folders_are_created(tmp_path):
    path = tmp_path / "data" / "processed" / "joined.csv"

    save_table(joined_table(), path)

    assert path.exists()


def test_dates_come_back_as_real_dates(tmp_path):
    # A CSV file only stores text, so without care "2026-07-01" would come back as text.
    path = tmp_path / "joined.csv"

    save_table(joined_table(), path)
    loaded = load_table(path)

    assert loaded["date"][0] == pd.Timestamp("2026-07-01")


def test_the_file_has_no_row_numbers(tmp_path):
    path = tmp_path / "joined.csv"

    save_table(joined_table(), path)

    first_line = path.read_text().splitlines()[0]
    assert first_line == "date,house_prices,mortgage_rate"
