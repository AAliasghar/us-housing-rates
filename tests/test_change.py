"""Tests for change_ahead. Read this file first: it shows what the code must do.

ROAD MAP of this file
    Test 1  One month ahead: each value compared with the next month's.
    Test 2  Two months ahead.
    Test 3  The last months have no future yet, so they stay blank.
    Test 4  The input is not changed.
    Test 5  A number of months below 1 is refused.

    The question for Stage 2 is: "N months AFTER this month, how much had prices changed?"
    So change_ahead looks FORWARD: from this month to N months later.

    growth % = (later - now) / now * 100

    The numbers are made up so the answers are easy: 100 -> 110 is +10 %, 110 -> 121 is +10 %.
"""

import pandas as pd
import pytest

from pipeline.change import change_ahead


def prices():
    """Four months of made-up prices."""
    return pd.Series([100.0, 110.0, 121.0, 108.9])


def test_one_month_ahead():
    result = change_ahead(prices(), months=1)

    # 100 -> 110 is +10 %, 110 -> 121 is +10 %, 121 -> 108.9 is -10 %
    assert result[0] == pytest.approx(10.0)
    assert result[1] == pytest.approx(10.0)
    assert result[2] == pytest.approx(-10.0)


def test_two_months_ahead():
    result = change_ahead(prices(), months=2)

    # 100 -> 121 is +21 % (not +20 %: the second 10 % grows on 110, not on 100)
    assert result[0] == pytest.approx(21.0)
    # 110 -> 108.9 is -1 %
    assert result[1] == pytest.approx(-1.0)


def test_the_last_months_stay_blank():
    # Month 3 has no "1 month later" in the data, so we cannot know its change yet.
    # It must stay blank (NaN), never 0: 0 would be a made-up "no change".
    result = change_ahead(prices(), months=1)
    assert pd.isna(result[3])

    # With 2 months ahead, the last 2 months stay blank.
    result = change_ahead(prices(), months=2)
    assert pd.isna(result[2])
    assert pd.isna(result[3])


def test_the_input_is_not_changed():
    values = prices()

    change_ahead(values, months=1)

    # assert_series_equal compares every value and explains any difference.
    pd.testing.assert_series_equal(values, prices())


@pytest.mark.parametrize("months", [0, -3])
def test_months_below_one_is_refused(months):
    with pytest.raises(ValueError, match="at least 1"):
        change_ahead(prices(), months=months)
