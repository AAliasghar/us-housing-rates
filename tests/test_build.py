"""Tests for build. Read this file first: it shows what the code must do.

ROAD MAP of this file
    Test 1  build downloads, makes monthly, joins, and saves the result to a file.
    Test 2  build asks for exactly the two series it needs.

    Like in test_fetch.py, the tests give build a fake fetch function instead of the
    real download, so they need no internet. The numbers are made up.
"""

import pandas as pd
import pytest

from pipeline.build import build
from pipeline.fred import read_series
from pipeline.store import load_table

# What the fake download hands back for each series, as FRED-style text.
FAKE_FRED = {
    "HPIPONM226S": "observation_date,HPIPONM226S\n2026-01-01,400.0\n2026-02-01,401.0\n",
    "MORTGAGE30US": "observation_date,MORTGAGE30US\n2026-01-08,7.0\n2026-01-22,7.2\n2026-02-05,7.1\n",
}


def test_build_makes_the_joined_table_and_saves_it(tmp_path):
    path = tmp_path / "joined.csv"

    def fake_fetch(series_id):
        return read_series(FAKE_FRED[series_id])

    joined = build(path=path, fetch=fake_fetch)

    # January's mortgage rate is the average of its two weeks: (7.0 + 7.2) / 2 = 7.1
    assert list(joined.columns) == ["date", "house_prices", "mortgage_rate"]
    assert joined["date"].tolist() == [pd.Timestamp("2026-01-01"), pd.Timestamp("2026-02-01")]
    assert joined["house_prices"].tolist() == [400.0, 401.0]
    assert joined["mortgage_rate"].tolist() == pytest.approx([7.1, 7.1])

    # The same table was saved to the file.
    pd.testing.assert_frame_equal(load_table(path), joined)


def test_build_asks_for_exactly_the_two_series(tmp_path):
    asked_for = []

    def fake_fetch(series_id):
        asked_for.append(series_id)
        return read_series(FAKE_FRED[series_id])

    build(path=tmp_path / "joined.csv", fetch=fake_fetch)

    assert sorted(asked_for) == ["HPIPONM226S", "MORTGAGE30US"]
