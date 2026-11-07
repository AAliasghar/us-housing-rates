"""Work with data files from FRED, the US Federal Reserve's data website.

ROAD MAP of this file
    read_series   Turn the text of a FRED file into a clean table.  (done)
    fetch_series  Download that text from FRED.                     (not written yet)

What a FRED file looks like (this is plain text, with commas between the columns):

    observation_date,UNRATE
    2025-09-01,4.4
    2025-10-01,
    2025-11-01,4.5

The first line holds the column names. The blank after 2025-10-01 means FRED has no number for that month.
"""

import io

import pandas as pd

# Every FRED file uses this name for its first column.
FRED_DATE_COLUMN = "observation_date"


# read_series: turn the text of a FRED file into a clean table.
#
#   1. Read the first line of the text, which holds the column names.
#   2. Check that it is a FRED file. If not, stop with a clear error.
#   3. Read all the text into a table.
#   4. Rename the columns to "date" and "value", the same for every series.
#   5. Turn the "date" column into real dates, and the "value" column into real numbers.
#   6. Give the finished table back.
#
# It does not download anything. It only works on text that it is given, so the tests need no internet.
#
# "csv_text: str" means: this function receives one input, called csv_text, and it should be text.
# "-> pd.DataFrame" means: it gives back a pandas table.
def read_series(csv_text: str) -> pd.DataFrame:
    # 1. Read the first line of the text, which holds the column names.
    # Example: first_line becomes "observation_date,UNRATE"
    # strip() removes invisible characters, such as the line ending, from both ends.
    all_lines = csv_text.split("\n")
    first_line = all_lines[0].strip()

    # Split at the comma. Example: column_names becomes ["observation_date", "UNRATE"]
    column_names = first_line.split(",")

    # 2. Check that it is a FRED file. If not, stop with a clear error.
    # Real case: asking FRED for a series that no longer exists returned a web page, not data.
    has_two_columns = len(column_names) == 2
    first_column_is_correct = column_names[0] == FRED_DATE_COLUMN

    if not has_two_columns or not first_column_is_correct:
        raise ValueError("Not a FRED file. The first line was: " + first_line)

    # 3. Read all the text into a table.
    # read_csv expects a file, and io.StringIO makes our text behave like an open file.
    # A blank value becomes empty (NaN) here, which is what we want.
    text_as_a_file = io.StringIO(csv_text)
    table = pd.read_csv(text_as_a_file)

    # 4. Rename the columns to "date" and "value", the same for every series.
    # Example: "observation_date" becomes "date", and "UNRATE" becomes "value".
    series_name = column_names[1]
    new_names = {FRED_DATE_COLUMN: "date", series_name: "value"}
    table = table.rename(columns=new_names)

    # 5. Turn the "date" column into real dates, and the "value" column into real numbers.
    # Text like "abc" in the value column raises an error here. That is what we want:
    # bad data should stop the run, not quietly turn into an empty value.
    table["date"] = pd.to_datetime(table["date"])
    table["value"] = pd.to_numeric(table["value"])

    # 6. Give the finished table back.
    return table
