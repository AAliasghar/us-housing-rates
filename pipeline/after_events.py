"""For each big move, how much prices changed some months later.

ROAD MAP of this file
    changes_after  One row per event, one column per wait (like "12m"): the % change after it.
"""

import pandas as pd

from pipeline.change import change_ahead


# changes_after: put big_moves and change_ahead together.
#
#   For each wait in months_list (for example 3, 6, 12, 24):
#     1. change_ahead gives the % change from EVERY month to that many months later.
#     2. Keep only the event months.
#     3. Store it as a column named after the wait, like "12m".
#
# An event too close to the end of the data gets a blank for the long waits:
# change_ahead already leaves those blank, and we keep them blank.
def changes_after(values: pd.Series, events: pd.Series, months_list: list) -> pd.DataFrame:
    # The row labels of the events: the rows where events is True.
    event_rows = values.index[events]

    columns = {}
    for months in months_list:
        # 1. % change from every month to `months` months later.
        change = change_ahead(values, months)

        # 2. Keep only the event rows. .loc[rows] picks rows by their labels.
        # 3. Name the column after the wait.
        columns[f"{months}m"] = change.loc[event_rows]

    # One row per event, one column per wait. index=event_rows keeps the table right
    # even when there are no events: then it is empty but still has its columns.
    return pd.DataFrame(columns, index=event_rows)
