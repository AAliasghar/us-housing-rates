"""Unit tests for the start date of an incremental download."""

from datetime import date

from pipeline.load import download_start


def test_the_first_load_has_no_start_date():
    assert download_start(None) is None


def test_the_download_starts_12_months_before_the_watermark():
    assert download_start(date(2026, 11, 19)) == date(2025, 11, 19)


def test_the_lookback_can_be_changed():
    assert download_start(date(2026, 11, 19), lookback_months=3) == date(2026, 8, 19)


def test_a_leap_day_becomes_the_last_day_of_february():
    assert download_start(date(2028, 2, 29)) == date(2027, 2, 28)
