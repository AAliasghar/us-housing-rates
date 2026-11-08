"""Tests for read_series. Read this file first: it shows what the code must do.

ROAD MAP of this file
    Each test is a small experiment with 3 parts:
      1. Input:  a tiny FRED-style file, written by hand. The numbers are made up.
      2. Run:    call read_series.
      3. Check:  assert that the result is what we worked out in our heads.

    Test 1  Normal rows give the right dates and numbers.
    Test 2  A blank value stays empty, and its row is kept.
    Test 3  Text that is not a FRED file stops with a clear error.
    Test 4  A value that is not a number stops with an error.

    No test uses the internet, so they run in milliseconds and never break because a website is down.
    Each test name is a full sentence, so a failure explains itself.
"""

import pandas as pd
import pytest

from pipeline.fred import read_series


def test_normal_rows_give_the_right_dates_and_numbers():
    # 1. Input
    csv_text = "observation_date,MORTGAGE30US\n2026-10-29,7.20\n2026-11-05,7.18\n"

    # 2. Run
    table = read_series(csv_text)

    # 3. Check: the same two column names for every series, real dates, and real numbers
    assert list(table.columns) == ["date", "value"]
    assert table["date"].tolist() == [pd.Timestamp("2026-10-29"), pd.Timestamp("2026-11-05")]
    assert table["value"].tolist() == [7.20, 7.18]


def test_a_blank_value_stays_empty_and_its_row_is_kept():
    # Real case: UNRATE and CPIAUCSL are blank for 2025-10-01 on FRED.
    csv_text = "observation_date,UNRATE\n2025-09-01,4.0\n2025-10-01,\n2025-11-01,5.0\n"

    table = read_series(csv_text)

    # A missing month must not disappear, and must not turn into 0%, which would look like real data.
    assert len(table) == 3
    assert pd.isna(table["value"][1])


# parametrize runs the same test once for each input in the list.
@pytest.mark.parametrize(
    "csv_text",
    [
        '<html lang="en">\n<body>Sorry, not found, try again</body>\n</html>\n',  # a web page instead of data, such as an error page
        "date,UNRATE\n2025-09-01,4.0\n",  # the wrong first column
        "observation_date,UNRATE,EXTRA\n2025-09-01,4.0,1.0\n",  # too many columns
        "",  # nothing at all
    ],
)
def test_text_that_is_not_a_fred_file_stops_with_a_clear_error(csv_text):
    # "with pytest.raises" means: the code inside must raise this error, or the test fails.
    # match checks that the message contains these words, so we know it is OUR clear error.
    with pytest.raises(ValueError, match="Not a FRED file"):
        read_series(csv_text)


def test_a_value_that_is_not_a_number_stops_with_an_error():
    csv_text = "observation_date,UNRATE\n2025-09-01,abc\n"

    # It must not quietly become an empty value: nobody would ever notice the bad data.
    with pytest.raises(ValueError):
        read_series(csv_text)
