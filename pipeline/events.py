"""Find the months where a big move starts, like a big rise in mortgage rates.

ROAD MAP of this file
    big_moves  True in each month where a big rise (or fall) starts, False everywhere else.
"""

import pandas as pd


# big_moves: mark the first month of each big move.
#
#   1. Refuse points=0: that is not a move.
#   2. Change from `months` months before: now - before.
#   3. Which months are over the line: >= points for a rise, <= points for a fall.
#   4. Walk through the months one by one. A month starts an event only if:
#        a. it is over the line,
#        b. the month before was NOT over the line (the FIRST month it crossed), and
#        c. at least `months` months have passed since the last event.
#
# Why the first month: in that month you already know the move happened. The month with the
# biggest change is only known later. Using it would be look-ahead bias.
#
# Like change_ahead, this counts rows, so the rows must be one month apart with no gaps.
def big_moves(values: pd.Series, points: float, months: int = 12) -> pd.Series:
    # 1. A move of 0 is not a move.
    if points == 0:
        raise ValueError("points must be above or below 0, not 0")

    # 2. shift(+months) moves values DOWN, so each row sees its value `months` rows before.
    #    The first rows have nothing before them, so their change is blank (NaN).
    change = values - values.shift(months)

    # 3. True where the change is over the line. A blank compared with a number gives False,
    #    so the first months are never over the line.
    if points > 0:
        over_line = change >= points
    else:
        over_line = change <= points

    # 4. Walk through the rows. .iloc[row] means "the value in row number `row`".
    is_event = []
    last_event_row = None  # no event yet

    for row in range(len(values)):
        crossed_now = bool(over_line.iloc[row])
        crossed_before = row > 0 and bool(over_line.iloc[row - 1])
        far_enough = last_event_row is None or row - last_event_row >= months

        if crossed_now and not crossed_before and far_enough:
            is_event.append(True)
            last_event_row = row
        else:
            is_event.append(False)

    # One True/False per row, with the same row labels as the input, so it fits next to the table.
    return pd.Series(is_event, index=values.index)
