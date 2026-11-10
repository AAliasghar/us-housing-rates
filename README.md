# US Housing and Mortgage Rates

[![CI](https://github.com/AAliasghar/us-housing-rates/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/AAliasghar/us-housing-rates/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

When US mortgage rates move, how long until house prices follow? And can a simple model forecast price changes better than a plain baseline?

> **Status: work in progress, Stage 1 of 5.** So far the code downloads a FRED series, reads it into a clean table, and turns weekly values into monthly averages, with tests. There is no analysis or model yet, and so no results.

## Data

All data will come from [FRED](https://fred.stlouisfed.org/), the Federal Reserve Bank of St. Louis data site. Raw data is not stored in this repo.

| Data | FRED series | Frequency |
|---|---|---|
| House prices | [`HPIPONM226S`](https://fred.stlouisfed.org/series/HPIPONM226S) | Monthly |
| 30-year mortgage rate | [`MORTGAGE30US`](https://fred.stlouisfed.org/series/MORTGAGE30US) | Weekly |

More inputs are planned, such as unemployment, inflation, housing supply and credit conditions.

## Use it

From the project folder:

```python
from pipeline.fred import fetch_series
from pipeline.transform import to_monthly

weekly = fetch_series("MORTGAGE30US")   # a table with two columns: date and value
monthly = to_monthly(weekly)            # one row per month: date, value (the average), observations
```

`to_monthly` matches FRED's own monthly averages of `MORTGAGE30US` to the cent, in all 667 complete months up to October 2026. FRED leaves a month that is not over yet blank; `to_monthly` gives it a value, and `observations` shows how many weeks it is built from so far.

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
├── pipeline/transform.py      # turns weekly values into monthly averages
├── tests/                     # the rules the code must follow; they need no internet
├── requirements-dev.txt       # exact tool versions
└── pyproject.toml             # pytest settings
```

## Roadmap

- [ ] Stage 1: download and clean the data, with tests
- [ ] Stage 2: lag analysis: how prices change 3, 6, 12 and 24 months after a big move in rates
- [ ] Stage 3: pipeline with Postgres, Airflow and dbt, and CI
- [ ] Stage 4: machine learning: a baseline, linear regression and gradient boosting, tested forward in time
- [ ] Stage 5: results and their limits

## License

MIT. See [LICENSE](LICENSE).

## Author

Aliasghar Asgharinia ([@AAliasghar](https://github.com/AAliasghar))
