"""
Tests for utility modules.
"""

import pytest
from datetime import datetime
from src.utils.helpers import get_trading_date, format_ist_timestamp


def test_get_trading_date_format():
    """Test that trading date is in YYYY-MM-DD format"""
    date = get_trading_date()

    # Should be in YYYY-MM-DD format
    assert len(date) == 10
    assert date[4] == '-'
    assert date[7] == '-'

    # Should be parseable as a date
    datetime.strptime(date, '%Y-%m-%d')


def test_format_ist_timestamp_contains_ist():
    """Test that IST timestamp contains 'IST' marker"""
    timestamp = format_ist_timestamp()

    assert 'IST' in timestamp
    assert len(timestamp) > 10
