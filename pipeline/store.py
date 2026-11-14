"""Save tables to files and read them back, so later steps do not download from FRED every time.

ROAD MAP of this file
    save_table  Write a table to a CSV file, creating its folder if needed.
    load_table  Read the file back, with real dates.
"""

from pathlib import Path

import pandas as pd


# save_table: write a table to a CSV file.
#
#   1. Make sure the folder for the file exists.
#   2. Write the table, without pandas' row numbers.
def save_table(table: pd.DataFrame, path) -> None:
    # Path turns text like "data/joined.csv" into a path object, which knows its folder (.parent).
    path = Path(path)

    # 1. parents=True also creates missing folders above it. exist_ok=True: no error if it exists.
    path.parent.mkdir(parents=True, exist_ok=True)

    # 2. index=False leaves out the row numbers 0, 1, 2, ... that pandas would otherwise write.
    table.to_csv(path, index=False)


# load_table: read a table saved by save_table.
#
#   1. Read the CSV file. A blank cell becomes empty (NaN), as in read_series.
#   2. A CSV file only stores text, so turn the date column back into real dates.
def load_table(path) -> pd.DataFrame:
    # 1. Read the file.
    table = pd.read_csv(path)

    # 2. Real dates again.
    table["date"] = pd.to_datetime(table["date"])
    return table
