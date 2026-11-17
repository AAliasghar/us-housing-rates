"""Tests for big_moves. Read this file first: it shows what the code must do.

ROAD MAP of this file
    Test 1  A big rise is marked in the FIRST month it crosses the line, not in the months after.
    Test 2  Crossing again too soon is the same event; crossing again later is a new event.
    Test 3  Big falls work the same way, with a minus line.
    Test 4  The first months cannot be events: there is nothing "months before" to compare with.
    Test 5  points=0 is refused: 0 is not a move.

    The rule (agreed in step 12c):
        A big rise is the first month where the value is at least `points` higher than
        `months` months before, and at least `months` months after the previous big rise.
        A big fall is the same with a minus `points`.

    The real analysis uses months=12. The tests use months=2 or 3, so the tables stay short.
    big_moves gives back True/False for each row: True means "an event starts here".
"""

import pandas as pd
import pytest

from pipeline.events import big_moves


def event_rows(result):
    """The row numbers that are True, as a plain list. Easier to read than a list of True/False."""
    return [row for row, is_event in enumerate(result) if is_event]


def test_a_big_rise_is_marked_in_the_first_month_only():
    rates = pd.Series([5.0, 5.0, 5.0, 6.0, 6.5, 6.5, 6.5])
    # Change from 2 months before:  -   -   0   1.0  1.5  0.5  0
    # Row 3 is the first at +1 or more. Row 4 is still above, but it is the same event.

    result = big_moves(rates, points=1.0, months=2)

    assert event_rows(result) == [3]


def test_crossing_again_too_soon_is_the_same_event():
    rates = pd.Series([5.0, 5.0, 5.0, 6.0, 5.5, 6.2, 6.2, 6.2, 6.2, 6.2, 7.5])
    # Change from 3 months before:  -  -  -  1.0  0.5  1.2  0.2  0.7  0  0  1.3
    # Row 3:  first crossing                                        -> event
    # Row 5:  crosses again, but only 2 rows after row 3 (less than 3) -> same event, ignored
    # Row 10: crosses again, 7 rows after row 3                       -> new event

    result = big_moves(rates, points=1.0, months=3)

    assert event_rows(result) == [3, 10]


def test_big_falls_use_a_minus_line():
    rates = pd.Series([7.0, 7.0, 7.0, 6.0, 6.0, 6.0])
    # Change from 2 months before:  -   -   0  -1.0 -1.0  0

    result = big_moves(rates, points=-1.0, months=2)

    assert event_rows(result) == [3]


def test_the_first_months_are_never_events():
    # Rows 0 and 1 have nothing 2 months before them, so their change is blank (NaN).
    # A blank must never count as a big move.
    rates = pd.Series([9.0, 1.0, 9.0, 9.0])

    result = big_moves(rates, points=1.0, months=2)

    assert result[0] == False  # noqa: E712  (== False reads more clearly here than "not")
    assert result[1] == False  # noqa: E712
    # One answer per row, so it can sit next to the table as a new column.
    assert len(result) == len(rates)


def test_points_zero_is_refused():
    with pytest.raises(ValueError, match="not 0"):
        big_moves(pd.Series([5.0, 6.0, 7.0]), points=0, months=1)
