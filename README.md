# US Housing and Mortgage Rates

When US mortgage rates move, how long until house prices follow? And can a simple model forecast price changes better than a plain baseline?

> **Status: work in progress, Stage 1 of 5.** So far there is one tested function that reads a FRED data file into a clean table. There is no download, analysis or model yet, and so no results.

## Data

All data will come from [FRED](https://fred.stlouisfed.org/), the Federal Reserve Bank of St. Louis data site. Raw data is not stored in this repo.

| Data | FRED series | Frequency |
|---|---|---|
| House prices | [`HPIPONM226S`](https://fred.stlouisfed.org/series/HPIPONM226S) | Monthly |
| 30-year mortgage rate | [`MORTGAGE30US`](https://fred.stlouisfed.org/series/MORTGAGE30US) | Weekly |

More inputs are planned, such as unemployment, inflation, housing supply and credit conditions.

## Run the tests

The tests need no internet.

```bash
python -m venv .venv
source .venv/Scripts/activate   # on Linux or macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -v
```

## Project structure

```
us-housing-rates/
├── pipeline/fred.py        # reads a FRED file into a table with date and value columns
├── tests/test_fred.py      # the rules that code must follow
├── requirements-dev.txt    # exact tool versions
└── pyproject.toml          # pytest settings
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
