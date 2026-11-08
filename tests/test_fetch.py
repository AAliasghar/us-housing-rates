"""Tests for fred_url and fetch_series. Read this file first: it shows what the code must do.

ROAD MAP of this file
    Test 1  The address for a series is FRED's CSV link.
    Test 2  A series name with odd characters is refused.
    Test 3  fetch_series downloads the right address and returns a clean table.
    Test 4  A web page instead of data stops with a clear error.
    Test 5  A bad series name is refused before anything is downloaded.

    These tests never use the internet. Instead of the real download, tests 3 to 5 give
    fetch_series a small fake download function, written right inside the test. The fake
    remembers which address it was asked for, and returns text that we chose.
"""

import pytest

from pipeline.fred import fetch_series, fred_url


def test_the_address_for_a_series_is_the_fred_csv_link():
    # This is the same address used to check every series by hand.
    assert fred_url("MORTGAGE30US") == "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"


# parametrize runs the same test once for each input in the list.
@pytest.mark.parametrize(
    "series_id",
    [
        "",  # nothing at all
        "MORTGAGE 30US",  # a space
        "MORTGAGE30US&cosd=2020-01-01",  # extra text that would change the address
    ],
)
def test_a_series_name_with_odd_characters_is_refused(series_id):
    with pytest.raises(ValueError, match="series name"):
        fred_url(series_id)


def test_fetch_series_downloads_the_right_address_and_returns_a_clean_table():
    # 1. Input: a fake download. It writes down each address it is given, and returns made-up text.
    asked_for = []

    def fake_download(url):
        asked_for.append(url)
        return "observation_date,MORTGAGE30US\n2026-10-29,7.20\n2026-11-05,7.18\n"

    # 2. Run: hand the fake to fetch_series instead of the real download.
    table = fetch_series("MORTGAGE30US", download=fake_download)

    # 3. Check: it asked for the right address once, and the text became a clean table.
    assert asked_for == ["https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"]
    assert list(table.columns) == ["date", "value"]
    assert table["value"].tolist() == [7.20, 7.18]


def test_a_web_page_instead_of_data_stops_with_a_clear_error():
    # FRED answers an unknown series with error 404, and download_text already stops on that.
    # This test covers a web page that arrives without an error code, for example after FRED moves its address.
    def fake_download(url):
        return '<html lang="en">\n<body>Sorry, not found</body>\n</html>\n'

    with pytest.raises(ValueError, match="Not a FRED file"):
        fetch_series("GOLDAMGBD228NLBM", download=fake_download)


def test_a_bad_series_name_is_refused_before_anything_is_downloaded():
    asked_for = []

    def fake_download(url):
        asked_for.append(url)
        return "observation_date,X\n2026-11-05,1.0\n"

    with pytest.raises(ValueError, match="series name"):
        fetch_series("MORTGAGE 30US", download=fake_download)

    # Nothing was downloaded: no time wasted, and no strange address sent to FRED.
    assert asked_for == []
