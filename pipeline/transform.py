"""Change the shape of a series, for example from weekly to monthly.

ROAD MAP of this file
    to_monthly   Turn weekly (or daily) rows into one row per month: the average of that month.
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
