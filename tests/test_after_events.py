"""Tests for changes_after. Read this file first: it shows what the code must do.

ROAD MAP of this file
    Test 1  For each event: the % change 1 and 2 months later, one row per event.
    Test 2  The columns are named after the months: "1m", "2m".
    Test 3  An event too close to the end has no answer yet for the long wait: blank, not 0.
    Test 4  No events gives an empty table that still has the columns.

    changes_after puts the two earlier steps together:
        big_moves     says WHERE the events are (True/False per month),
        change_ahead  says how much prices changed N months after each month.
    changes_after keeps only the event months, for each N.

    The real analysis uses 3, 6, 12 and 24 months. The tests use 1 and 2, so the tables stay short.
"""

import pandas as pd
import pytest

from pipeline.after_events import changes_after


def prices():
    """Five months of made-up prices: +10 % each month, then -10 %."""
    return pd.Series([100.0, 110.0, 121.0, 133.1, 119.79])


def test_one_row_per_event_with_the_change_after_it():
    events = pd.Series([True, False, True, False, False])  # events in rows 0 and 2

    result = changes_after(prices(), events, months_list=[1, 2])

    # One row per event, labelled with the event's row number.
    assert result.index.tolist() == [0, 2]
    # Row 0: 100 -> 110 is +10 %, 100 -> 121 is +21 %
    assert result.loc[0, "1m"] == pytest.approx(10.0)
    assert result.loc[0, "2m"] == pytest.approx(21.0)
    # Row 2: 121 -> 133.1 is +10 %, 121 -> 119.79 is -1 %
    assert result.loc[2, "1m"] == pytest.approx(10.0)
    assert result.loc[2, "2m"] == pytest.approx(-1.0)


def test_columns_are_named_after_the_months():
    events = pd.Series([True, False, False, False, False])

    result = changes_after(prices(), events, months_list=[1, 2])

    assert list(result.columns) == ["1m", "2m"]


def test_an_event_too_close_to_the_end_stays_blank():
    # Row 3 has a month after it (row 4), but not 2 months after it.
    events = pd.Series([False, False, False, True, False])

    result = changes_after(prices(), events, months_list=[1, 2])

    assert result.loc[3, "1m"] == pytest.approx(-10.0)
    assert pd.isna(result.loc[3, "2m"])


def test_no_events_gives_an_empty_table():
    events = pd.Series([False, False, False, False, False])

    result = changes_after(prices(), events, months_list=[1, 2])

    assert len(result) == 0
    assert list(result.columns) == ["1m", "2m"]
