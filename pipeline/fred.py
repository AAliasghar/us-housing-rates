"""Work with data files from FRED, the US Federal Reserve's data website.

ROAD MAP of this file
    read_series    Turn the text of a FRED file into a clean table.
    fred_url       Build the web address of one FRED series.
    download_text  Download the text at a web address.
    fetch_series   Put them together: name of a series in, clean table out.

What a FRED file looks like (this is plain text, with commas between the columns):

    observation_date,UNRATE
    2025-09-01,4.4
    2025-10-01,
    2025-11-01,4.5

The first line holds the column names. The blank after 2025-10-01 means FRED has no number for that month.
"""

import io
import urllib.request

import pandas as pd

# Every FRED file uses this name for its first column.
FRED_DATE_COLUMN = "observation_date"

# FRED's address for downloading one series as a CSV file. The series name goes at the end.
FRED_CSV_ADDRESS = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="


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
    # Example: a web page arrives instead of data, such as an error page.
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


# fred_url: build the web address of one FRED series.
#
#   1. Check that the name has only plain letters and digits. If not, stop with a clear error.
#   2. Put the name at the end of FRED's address, and give it back.
#
# Example: "MORTGAGE30US" becomes "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
def fred_url(series_id: str) -> str:
    # 1. Check the name. Every FRED series name is plain letters and digits, like UNRATE or T10Y2Y.
    # isascii() means "only plain English characters", and isalnum() means "only letters and digits".
    # An empty name fails too. This stops typos, and stops extra text that would change the address.
    if not (series_id.isascii() and series_id.isalnum()):
        raise ValueError("Not a valid FRED series name: '" + series_id + "'")

    # 2. Put the name at the end of FRED's address.
    return FRED_CSV_ADDRESS + series_id


# download_text: download the text at a web address.
#
# This is the only function in the file that uses the internet, so the tests never call it.
# urllib comes with Python, so the project needs no new library for this.
def download_text(url: str) -> str:
    # 1. Ask the website, and wait at most 30 seconds. If the website answers with an error
    # (for example 404, "not found"), urlopen raises it, so a failed download stops the run.
    # We keep Python's standard User-Agent (the name a program gives when it asks a website).
    # In the first real run, FRED did not answer at all when the request used this project's
    # own name, and the download timed out after 30 seconds.
    with urllib.request.urlopen(url, timeout=30) as response:
        # 2. The answer arrives as bytes. decode turns the bytes into text.
        return response.read().decode("utf-8")


# fetch_series: name of a series in, clean table out.
#
#   1. Build the address. A bad name stops here, before anything is downloaded.
#   2. Download the text.
#   3. Turn the text into a clean table with read_series.
#
# "download=download_text" means: if nobody says which download function to use, use the real one.
# The tests pass in a fake one instead, so they need no internet.
def fetch_series(series_id: str, download=download_text) -> pd.DataFrame:
    # 1. Build the address.
    url = fred_url(series_id)

    # 2. Download the text.
    text = download(url)

    # 3. Turn the text into a clean table, and give it back.
    return read_series(text)
