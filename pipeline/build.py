"""Build the joined table in one command: download, make monthly, join, save.

Run it from the project folder:

    python -m pipeline.build

ROAD MAP of this file
    build   Download both series, make the mortgage rates monthly, join them, and save the result.
"""

from pipeline.fred import fetch_series
from pipeline.store import save_table
from pipeline.transform import join_series, to_monthly

# Where the joined table is saved. The data/ folder is in .gitignore, so it is never uploaded.
OUTPUT_PATH = "data/joined.csv"


# build: the whole pipeline in one function.
#
#   1. Download house prices (already monthly) and mortgage rates (weekly).
#   2. Turn the weekly mortgage rates into monthly averages.
#   3. Join both by month.
#   4. Save the result to a file, and give it back.
#
# "fetch=fetch_series" works like download= in fetch_series: the real download by default,
# and a fake one in the tests, so they need no internet.
def build(path=OUTPUT_PATH, fetch=fetch_series):
    # 1. Download.
    house_prices = fetch("HPIPONM226S")
    weekly_rate = fetch("MORTGAGE30US")

    # 2. Monthly averages.
    mortgage_rate = to_monthly(weekly_rate)

    # 3. Join by month.
    joined = join_series({"house_prices": house_prices, "mortgage_rate": mortgage_rate})

    # 4. Save, and give it back.
    save_table(joined, path)
    return joined


# This part runs only when the file is started as a program (python -m pipeline.build),
# not when another file imports build, like the tests do.
if __name__ == "__main__":
    result = build()
    first = result["date"].min().strftime("%Y-%m")
    last = result["date"].max().strftime("%Y-%m")
    print(f"Saved {len(result)} months ({first} to {last}) to {OUTPUT_PATH}")
