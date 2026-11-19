# US Housing and Mortgage Rates

[![CI](https://github.com/AAliasghar/us-housing-rates/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/AAliasghar/us-housing-rates/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

When US mortgage rates move, how long until house prices follow? And can a simple model forecast price changes better than a plain baseline?

> **Status: work in progress, Stages 1 and 2 of 5 done.** The code downloads and cleans the data, joins it by month and saves it with one command (Stage 1), then measures how house prices changed after big moves in mortgage rates (Stage 2), all with tests. There is no model yet (Stage 4).

## Data

All data will come from [FRED](https://fred.stlouisfed.org/), the Federal Reserve Bank of St. Louis data site. Raw data is not stored in this repo.

| Data                  | FRED series                                                       | Frequency |
| --------------------- | ----------------------------------------------------------------- | --------- |
| House prices          | [`HPIPONM226S`](https://fred.stlouisfed.org/series/HPIPONM226S)   | Monthly   |
| 30-year mortgage rate | [`MORTGAGE30US`](https://fred.stlouisfed.org/series/MORTGAGE30US) | Weekly    |

More inputs are planned, such as unemployment, inflation, housing supply and credit conditions.

## Use it

Build the joined table with one command, from the project folder:

```bash
python -m pipeline.build
# Saved 428 months (1991-01 to 2026-08) to data/joined.csv   (run on 2026-11-14)
```

Or step by step in Python:

```python
from pipeline.fred import fetch_series
from pipeline.transform import join_series, to_monthly

weekly = fetch_series("MORTGAGE30US")   # a table with two columns: date and value
monthly = to_monthly(weekly)            # one row per month: date, value (the average), observations

house_prices = fetch_series("HPIPONM226S")
joined = join_series({"house_prices": house_prices, "mortgage_rate": monthly})
# one row per month: date, house_prices, mortgage_rate
# (checked 2026-11-12: 428 months, 1991-01 to 2026-08, no blanks)
```

`to_monthly` matches FRED's own monthly averages of `MORTGAGE30US` to the cent (checked 2026-11-11), in all 667 complete months up to October 2026. FRED leaves a month that is not over yet blank; `to_monthly` gives it a value, and `observations` shows how many weeks it is built from so far.

## Results so far (Stage 2)

**Question:** after a big move in mortgage rates, how did house prices change 3, 6, 12 and 24 months later?

**A big move** is the first month where the 30-year rate is at least 1 point higher (a rise) or lower (a fall) than 12 months before. A new move counts only 12 months or more after the previous one, so one long climb counts once. The first month is used because the move is already known then; a later, "bigger" month would use knowledge from the future.

That gives **6 big rises** (1994-05, 1999-08, 2004-06, 2006-06, 2013-12, 2022-03) and **11 big falls** (1992-01 to 2024-09).

Median % change in house prices after the move (run on 2026-11-19, data to 2026-08):

| | 3 months | 6 months | 12 months | 24 months |
|---|---|---|---|---|
| After a big rise (6 events) | 1.2 | 1.9 | 4.0 | 10.1 |
| After a big fall (11 events; 10 for 24 months) | 1.3 | 2.8 | 6.0 | 13.1 |
| Any month, for comparison (about 400) | 1.2 | 2.4 | 5.0 | 11.1 |

**What it shows:** house prices kept rising after big rate rises, but more slowly than usual (+4.0 % over 12 months against +5.0 % in a typical month). After big falls they rose a little faster (+6.0 %).

**What it does not show:**

- **Cause.** Other things move rates and prices at the same time. The two clear price drops came with the 2007-2008 housing crash (after the 2006-06 rise) and the 2009 financial crisis (after the 2009-04 fall, when rates were cut *because* of the crisis).
- **Certainty.** 6 rises and 11 falls are examples, not proof. One unusual event changes the median.
- **Prices in dollars.** `HPIPONM226S` is an index (1991-01 = 100), so only % changes are meaningful.

To reproduce, after `python -m pipeline.build`:

```python
from pipeline.store import load_table
from pipeline.events import big_moves
from pipeline.after_events import changes_after

table = load_table("data/joined.csv")
rises = big_moves(table["mortgage_rate"], points=1.0)     # points=-1.0 for falls
after = changes_after(table["house_prices"], rises, [3, 6, 12, 24])
after.median()
```

## Run the tests

The tests need no internet. GitHub also runs them on every push to `main` and every pull request (CI).

```bash
python -m venv .venv
source .venv/Scripts/activate   # on Linux or macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -v
```

## Project structure

```
us-housing-rates/
├── .github/workflows/ci.yml   # CI: runs the tests on GitHub
├── pipeline/fred.py           # downloads a FRED series and reads it into a table (date, value)
├── pipeline/transform.py      # monthly averages, and joining series by month
├── pipeline/store.py          # saves a table to a CSV file and reads it back
├── pipeline/build.py          # the whole pipeline in one command
├── pipeline/change.py         # % change from each month to N months later (Stage 2)
├── pipeline/events.py         # finds the first month of each big rate rise or fall
├── pipeline/after_events.py   # price change 3, 6, 12, 24 months after each big move
├── tests/                     # the rules the code must follow; they need no internet
├── requirements-dev.txt       # exact tool versions
└── pyproject.toml             # pytest settings
```

## Roadmap

- [x] Stage 1: download and clean the data, with tests
- [x] Stage 2: lag analysis: how prices change 3, 6, 12 and 24 months after a big move in rates
- [ ] Stage 3: pipeline with Postgres, Airflow and dbt, and CI
- [ ] Stage 4: machine learning: a baseline, linear regression and gradient boosting, tested forward in time
- [ ] Stage 5: results and their limits

## License

MIT. See [LICENSE](LICENSE).

## Author

Aliasghar Asgharinia ([@AAliasghar](https://github.com/AAliasghar))
