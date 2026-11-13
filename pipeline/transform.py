"""Change the shape of a series, for example from weekly to monthly.

ROAD MAP of this file
    to_monthly   Turn weekly (or daily) rows into one row per month: the average of that month.
    join_series  Put several monthly series side by side in one table, matched by month.
"""

import pandas as pd


# to_monthly: turn weekly (or daily) rows into one row per month.
#
#   1. Work out the month of each row, as the first day of that month.
#   2. Group the values by that month.
#   3. For each month, take the average, and count how many values it was built from.
#   4. Put it together as a table with the columns date, value and observations.
#
# Blank values are skipped: mean() and count() both ignore NaN. A month with only blanks
# gets an empty value and 0 observations, but it keeps its row.
#
# Input:  a table like the one read_series returns, with the columns date and value.
# Output: one row per month, in date order, dated the 1st, like the monthly house prices.
def to_monthly(table: pd.DataFrame) -> pd.DataFrame:
    # 1. Work out the month of each row. Example: 2026-10-08 becomes 2026-10-01.
    # to_period("M") turns a date into its month, and to_timestamp() gives that month's first day.
    month = table["date"].dt.to_period("M").dt.to_timestamp()

    # 2. Group the values by month. Rows from the same month land in the same group.
    # groupby also sorts the months, so the result is in date order.
    groups = table["value"].groupby(month)

    # 3. mean() is the average. count() counts only the values that are not blank.
    averages = groups.mean()
    observations = groups.count()

    # 4. Put it together as a new table.
    monthly = pd.DataFrame(
        {
            "date": averages.index,
            "value": averages.values,
            "observations": observations.values,
        }
    )
    return monthly


# join_series: put several monthly series side by side in one table, matched by month.
#
#   1. For each table, check that it is monthly and has each month only once. If not, stop.
#   2. Keep only its date and value columns, and rename value to the series name.
#   3. Join it to the tables before it, by date. Only months found in every table stay.
#   4. Sort by date, and give the result back.
#
# Input:  a dictionary of name -> table, for example {"house_prices": ..., "mortgage_rate": ...}.
#         Each table has a date and a value column, like the ones read_series and to_monthly return.
# Output: one row per month, with a date column and one column per series.
def join_series(tables: dict) -> pd.DataFrame:
    joined = None

    for name, table in tables.items():
        # 1. Check the table. If a check fails, stop with a clear error instead of giving a wrong table.
        # .dt.day gives the day of the month. On a monthly table, it is 1 on every row.
        if not (table["date"].dt.day == 1).all():
            raise ValueError("'" + name + "' is not monthly: every date must be the 1st of a month")
        # duplicated() is True for a date that already appeared in an earlier row.
        if table["date"].duplicated().any():
            raise ValueError("'" + name + "' has the same month twice")

        # 2. Keep date and value, and rename value to the series name, for example "house_prices".
        part = table[["date", "value"]].rename(columns={"value": name})

        # 3. The first table starts the result. Each later table is joined to it by date.
        # how="inner" keeps only the months that are in both, like JOIN in SQL.
        if joined is None:
            joined = part
        else:
            joined = joined.merge(part, on="date", how="inner")

    # 4. Sort by date. reset_index numbers the rows 0, 1, 2, ... again after sorting.
    joined = joined.sort_values("date").reset_index(drop=True)
    return joined
