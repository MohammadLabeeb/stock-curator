"""
Helper utilities for the stock-curator project.
"""

import re
import pytz
from datetime import datetime
from typing import Any

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
    return get_current_ist_time().strftime("%Y-%m-%d")


def format_ist_timestamp() -> str:
    """
    Get formatted IST timestamp.

    Returns:
        Timestamp string like "2025-12-22 15:30:45 IST"
    """
    return get_current_ist_time().strftime("%Y-%m-%d %H:%M:%S IST")


def sanitize_log_message(message: Any, max_length: int = 500) -> str:
    """
    Sanitize log messages to prevent API key leakage.
    
    This function:
    - Masks potential API keys and tokens
    - Truncates long messages
    - Removes sensitive headers
    
    Args:
        message: Message to sanitize (string or any object that can be converted to string)
        max_length: Maximum length of the sanitized message
    
    Returns:
        Sanitized message string
    """
    # Convert to string if not already
    msg = str(message)
    
    # Pattern to match potential API keys (various formats)
    # Matches: Bearer tokens, API keys, x-api-key headers, etc.
    # Order matters - more specific patterns should come first
    patterns = [
        (r'Bearer [A-Za-z0-9\-._~+/]+=*', 'Bearer [REDACTED]'),
        (r'x-api-key:\s*[A-Za-z0-9_\-]+', 'x-api-key: [REDACTED]'),  # Must come before general api_key pattern
        (r'["\']?[aA][pP][iI][_-]?[kK][eE][yY]["\']?\s*[:=]\s*["\']?([A-Za-z0-9_\-]{8,})["\']?', 'api_key=[REDACTED]'),
        (r'["\']?[tT][oO][kK][eE][nN]["\']?\s*[:=]\s*["\']?([A-Za-z0-9_\-]{8,})["\']?', 'token=[REDACTED]'),
        (r'["\']?[sS][eE][cC][rR][eE][tT]["\']?\s*[:=]\s*["\']?([A-Za-z0-9_\-]{8,})["\']?', 'secret=[REDACTED]'),
        (r'["\']?[pP][aA][sS][sS][wW][oO][rR][dD]["\']?\s*[:=]\s*["\']?([A-Za-z0-9_\-]{8,})["\']?', 'password=[REDACTED]'),
        (r'AIza[0-9A-Za-z\-_]{35}', '[GOOGLE_API_KEY_REDACTED]'),  # Google API keys
        (r'sk-[A-Za-z0-9]{20,}', '[SECRET_KEY_REDACTED]'),  # Generic secret keys
    ]
    
    # Apply all patterns
    for pattern, replacement in patterns:
        msg = re.sub(pattern, replacement, msg)
    
    # Truncate if too long (calculate hidden chars before truncating)
    if len(msg) > max_length:
        hidden_chars = len(msg) - max_length
        msg = msg[:max_length] + f"... (truncated, {hidden_chars} chars hidden)"
    
    return msg
