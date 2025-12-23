"""
Helper utilities for the stock-curator project.
"""

import pytz
from datetime import datetime
from typing import Optional

from src.config.constants import IST_TIMEZONE


def get_current_ist_time() -> datetime:
    """
    Get current time in IST timezone.

    Returns:
        datetime object in IST
    """
    ist = pytz.timezone(IST_TIMEZONE)
    return datetime.now(ist)


def get_trading_date() -> str:
    """
    Get current trading date in YYYY-MM-DD format.

    Returns:
        Date string in IST timezone
    """
    return get_current_ist_time().strftime('%Y-%m-%d')


def format_ist_timestamp() -> str:
    """
    Get formatted IST timestamp.

    Returns:
        Timestamp string like "2025-12-22 15:30:45 IST"
    """
    return get_current_ist_time().strftime('%Y-%m-%d %H:%M:%S IST')
