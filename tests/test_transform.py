"""Tests for to_monthly. Read this file first: it shows what the code must do.

ROAD MAP of this file
    Mortgage rates come weekly, but house prices come monthly. To compare them,
    to_monthly turns weekly rows into one row per month: the average of that month's values.

    Test 1  The weeks of one month become one row, dated the 1st, with their average.
    Test 2  Each month gets its own row, in date order, even if the input is not sorted.
    Test 3  A blank week is skipped, not counted as 0.
    Test 4  A month with only blank weeks stays empty, and its row is kept.
    Test 5  Each month says how many values it was built from, so a half-finished month is visible.

    The numbers are made up, and chosen so the averages are easy to work out by hand.
    Averages are compared with pytest.approx ("equal, give or take tiny rounding"), because a computer
    stores most decimals only almost exactly: in Python, 0.1 + 0.2 gives 0.30000000000000004.
"""

import pandas as pd
import pytest

from pipeline.transform import to_monthly


def weekly(rows):
    """Build a small table like the one read_series returns: a date column and a value column."""
    table = pd.DataFrame(rows, columns=["date", "value"])
    table["date"] = pd.to_datetime(table["date"])
    return table


def test_the_weeks_of_one_month_become_one_row_with_their_average():
    # 1. Input: three weeks in October. (7.0 + 7.2 + 7.4) / 3 = 7.2
    table = weekly([("2026-10-01", 7.0), ("2026-10-08", 7.2), ("2026-10-15", 7.4)])

    # 2. Run
    monthly = to_monthly(table)

    # 3. Check: one row, dated the first day of the month, like the monthly house prices
    assert monthly["date"].tolist() == [pd.Timestamp("2026-10-01")]
    assert monthly["value"].tolist() == pytest.approx([7.2])


def test_each_month_gets_its_own_row_in_date_order():
    # The November week comes first on purpose: the result must still be in date order.
    table = weekly([("2026-11-05", 6.0), ("2026-10-08", 7.0), ("2026-10-15", 8.0)])

    monthly = to_monthly(table)

    assert monthly["date"].tolist() == [pd.Timestamp("2026-10-01"), pd.Timestamp("2026-11-01")]
    assert monthly["value"].tolist() == pytest.approx([7.5, 6.0])


def test_a_blank_week_is_skipped_not_counted_as_zero():
    # With the blank skipped: (7.0 + 7.4) / 2 = 7.2.
    # If the blank counted as 0, the average would wrongly be (7.0 + 0 + 7.4) / 3 = 4.8.
    table = weekly([("2026-10-01", 7.0), ("2026-10-08", None), ("2026-10-15", 7.4)])

    monthly = to_monthly(table)

    assert monthly["value"].tolist() == pytest.approx([7.2])
    # The blank week is not a value either, so the month was built from 2 values, not 3.
    assert monthly["observations"].tolist() == [2]


def test_a_month_with_only_blank_weeks_stays_empty_and_its_row_is_kept():
    # Like the blank October 2025 in UNRATE: the month must not disappear, and must not become 0.
    table = weekly([("2025-09-04", 4.0), ("2025-10-02", None), ("2025-10-09", None), ("2025-11-06", 5.0)])

    monthly = to_monthly(table)

    assert len(monthly) == 3
    assert pd.isna(monthly["value"][1])


def test_each_month_says_how_many_values_it_was_built_from():
    # October has 3 weeks with a number. November has only 1 so far: a half-finished month,
    # whose average may still change. The observations column makes that visible.
    table = weekly([("2026-10-01", 7.0), ("2026-10-08", 7.2), ("2026-10-15", 7.4), ("2026-11-05", 7.18)])

    monthly = to_monthly(table)

    assert monthly["observations"].tolist() == [3, 1]
