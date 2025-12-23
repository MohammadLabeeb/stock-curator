"""
Data loading utilities for Streamlit dashboard.
Loads prediction data from the GitHub repository.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
import streamlit as st


@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_daily_predictions(date_str: str) -> Optional[Dict]:
    """
    Load predictions for a specific date.

    Args:
        date_str: Date string in YYYY-MM-DD format

    Returns:
        Dictionary with predictions or None if not found
    """
    file_path = Path(f"data/daily_results/{date_str}_predictions.json")

    if not file_path.exists():
        return None

    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading data for {date_str}: {str(e)}")
        return None


@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_all_predictions() -> Dict[str, Dict]:
    """
    Load all historical predictions.

    Returns:
        Dictionary mapping dates to prediction data
    """
    results_dir = Path("data/daily_results")

    if not results_dir.exists():
        return {}

    all_data = {}

    for file_path in sorted(results_dir.glob("*_predictions.json")):
        date = file_path.stem.replace("_predictions", "")

        try:
            with open(file_path, 'r') as f:
                all_data[date] = json.load(f)
        except Exception as e:
            st.warning(f"Could not load {file_path.name}: {str(e)}")
            continue

    return all_data


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_available_dates() -> List[str]:
    """
    Get list of dates with available predictions.

    Returns:
        Sorted list of date strings (most recent first)
    """
    results_dir = Path("data/daily_results")

    if not results_dir.exists():
        return []

    dates = [
        f.stem.replace("_predictions", "")
        for f in sorted(results_dir.glob("*_predictions.json"))
    ]

    return sorted(dates, reverse=True)  # Most recent first


def get_latest_date() -> Optional[str]:
    """
    Get the most recent date with predictions.

    Returns:
        Latest date string or None if no data
    """
    dates = get_available_dates()
    return dates[0] if dates else None


def clear_cache():
    """Clear all cached data (useful for forcing refresh)"""
    st.cache_data.clear()
