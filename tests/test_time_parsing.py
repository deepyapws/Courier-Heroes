from utils import parse_time_to_dt
from datetime import datetime


def test_parse_iso():
    dt = parse_time_to_dt('2025-12-16 11:13:47')
    assert isinstance(dt, datetime) and dt.year == 2025 and dt.month == 12 and dt.day == 16


def test_parse_dotted():
    dt = parse_time_to_dt('2025.12.16 11:13')
    assert isinstance(dt, datetime) and dt.hour == 11 and dt.minute == 13


def test_parse_slash_and_no_seconds():
    dt = parse_time_to_dt('2025/12/16 11:13')
    assert isinstance(dt, datetime) and dt.hour == 11 and dt.minute == 13


def test_parse_korean_like_or_partial():
    dt = parse_time_to_dt('2025년 12월 16일 11:13')
    assert isinstance(dt, datetime) and dt.day == 16


def test_parse_fuzzy_month_name():
    dt = parse_time_to_dt('16 Dec 2025 11:13')
    assert isinstance(dt, datetime) and dt.day == 16 and dt.month == 12


def test_parse_invalid_returns_none():
    dt = parse_time_to_dt('sometime today')
    assert dt is None
