-- Raw FRED observations, stored exactly as downloaded: one row per series and date.
-- Run at the start of every load, so it must be safe to run again (IF NOT EXISTS).

CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.fred_observations (
    series_id  TEXT        NOT NULL,
    date       DATE        NOT NULL,
    value      NUMERIC,                               -- NULL where FRED has no value
    loaded_at  TIMESTAMPTZ NOT NULL DEFAULT now(),    -- when this value last changed
    PRIMARY KEY (series_id, date)
);
