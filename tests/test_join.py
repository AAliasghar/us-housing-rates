"""Tests for join_series. Read this file first: it shows what the code must do.

ROAD MAP of this file
    join_series puts monthly series side by side in one table, so they can be compared month
    by month. It receives a dictionary: the name each series should get, and its table.
    Example: {"house_prices": ..., "mortgage_rate": ...}

    Test 1  Two series become one table, one column per series, matched by month.
    Test 2  Only months that are in every table are kept.
    Test 3  A blank value stays blank, and its month is kept.
    Test 4  The result is in date order, even if the input is not.
    Test 5  A table that is not monthly is refused.
    Test 6  A table with the same month twice is refused.

    The numbers are made up.
"""

import pandas as pd
import pytest

from pipeline.transform import join_series


def monthly(rows):
    """Build a small monthly table: a date column (always the 1st of a month) and a value column."""
    table = pd.DataFrame(rows, columns=["date", "value"])
    table["date"] = pd.to_datetime(table["date"])
    return table


def test_two_series_become_one_table_matched_by_month():
    # 1. Input. The mortgage table also has an observations column, like the one to_monthly returns.
    house_prices = monthly([("2026-01-01", 400.0), ("2026-02-01", 401.0)])
    mortgage_rate = monthly([("2026-01-01", 7.0), ("2026-02-01", 7.1)])
    mortgage_rate["observations"] = [4, 4]

    # 2. Run
    joined = join_series({"house_prices": house_prices, "mortgage_rate": mortgage_rate})

    # 3. Check: one row per month, and each value column is named after its series.
    # Extra columns like observations are left out.
    assert list(joined.columns) == ["date", "house_prices", "mortgage_rate"]
    assert joined["date"].tolist() == [pd.Timestamp("2026-01-01"), pd.Timestamp("2026-02-01")]
    assert joined["house_prices"].tolist() == [400.0, 401.0]
    assert joined["mortgage_rate"].tolist() == [7.0, 7.1]


def test_only_months_that_are_in_every_table_are_kept():
    # House prices: January to March. Mortgage rates: February to April.
    # Only February and March can be compared, because only they have both values.
    house_prices = monthly([("2026-01-01", 400.0), ("2026-02-01", 401.0), ("2026-03-01", 402.0)])
    mortgage_rate = monthly([("2026-02-01", 7.1), ("2026-03-01", 7.2), ("2026-04-01", 7.3)])

    joined = join_series({"house_prices": house_prices, "mortgage_rate": mortgage_rate})

    assert joined["date"].tolist() == [pd.Timestamp("2026-02-01"), pd.Timestamp("2026-03-01")]


def test_a_blank_value_stays_blank_and_its_month_is_kept():
    # February exists in both tables, but its mortgage rate is unknown. Keep the month, keep the blank.
    house_prices = monthly([("2026-01-01", 400.0), ("2026-02-01", 401.0)])
    mortgage_rate = monthly([("2026-01-01", 7.0), ("2026-02-01", None)])

    joined = join_series({"house_prices": house_prices, "mortgage_rate": mortgage_rate})

    assert len(joined) == 2
    assert pd.isna(joined["mortgage_rate"][1])


def test_the_result_is_in_date_order():
    house_prices = monthly([("2026-02-01", 401.0), ("2026-01-01", 400.0)])
    mortgage_rate = monthly([("2026-01-01", 7.0), ("2026-02-01", 7.1)])

    joined = join_series({"house_prices": house_prices, "mortgage_rate": mortgage_rate})

    assert joined["date"].tolist() == [pd.Timestamp("2026-01-01"), pd.Timestamp("2026-02-01")]
    assert joined["house_prices"].tolist() == [400.0, 401.0]


def test_a_table_that_is_not_monthly_is_refused():
    # Real danger: the weekly mortgage table has 88 dates that happen to fall on the 1st of a month.
    # Joined by mistake, it would quietly match only those 88 weeks, and look like real results.
    house_prices = monthly([("2026-01-01", 400.0), ("2026-02-01", 401.0)])
    weekly_rate = monthly([("2026-01-01", 7.0), ("2026-01-08", 7.1), ("2026-02-05", 7.2)])

    with pytest.raises(ValueError, match="not monthly"):
        join_series({"house_prices": house_prices, "mortgage_rate": weekly_rate})


def test_a_table_with_the_same_month_twice_is_refused():
    # A repeated month would match twice and create extra rows, which would count that month twice.
    house_prices = monthly([("2026-01-01", 400.0), ("2026-01-01", 400.5), ("2026-02-01", 401.0)])
    mortgage_rate = monthly([("2026-01-01", 7.0), ("2026-02-01", 7.1)])

    with pytest.raises(ValueError, match="same month twice"):
        join_series({"house_prices": house_prices, "mortgage_rate": mortgage_rate})
