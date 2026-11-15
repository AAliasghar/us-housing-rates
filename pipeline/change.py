"""How much a value changes from each month to N months later.

ROAD MAP of this file
    change_ahead  For each month: the % change from this month to N months later.
"""

import pandas as pd


# change_ahead: look FORWARD from each month.
#
#   1. Refuse a number of months below 1.
#   2. Move the values up by N rows, so each row also sees its value N months later.
#   3. growth % = (later - now) / now * 100
#
# The rows must be one month apart, with no month missing. The joined table is like that:
# 428 rows, 1991-01 to 2026-08, no gaps.
def change_ahead(values: pd.Series, months: int) -> pd.Series:
    # 1. "0 months ahead" or "-3 months ahead" makes no sense.
    if months < 1:
        raise ValueError(f"months must be at least 1, got {months}")

    # 2. shift(-months) moves every value UP by that many rows.
    #    With months=1: row 0 now holds row 1's value, row 1 holds row 2's, and so on.
    #    The last row has nothing below it, so it gets a blank (NaN).
    #    shift makes a new Series; the input is not changed.
    later = values.shift(-months)

    # 3. The growth formula. A blank in "later" gives a blank result, never a made-up 0.
    return (later - values) / values * 100
