"""
Stock data fetching from Upstox API.
Extracted from notebook: 10_production_ml_filter.ipynb
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.config.settings import Settings
from src.data.stock_validator import load_stock_lookup

logger = logging.getLogger(__name__)


def create_session_with_retries(
    retries: int = 3, backoff_factor: float = 0.3
) -> requests.Session:
    """
    Create a requests session with retry logic.

    Args:
        retries: Number of retries for failed requests
        backoff_factor: Backoff factor for exponential backoff

    Returns:
        Configured requests Session
    """
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=(500, 502, 504),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


# Global session for reuse
_session = create_session_with_retries()


def get_isin_for_symbol(symbol: str) -> Optional[str]:
    """
    Convert stock symbol to ISIN code using stock lookup.

    Args:
        symbol: Stock trading symbol (e.g., 'RELIANCE')

    Returns:
        ISIN code or None if not found
    """
    stock_lookup = load_stock_lookup()

    if symbol in stock_lookup["by_symbol"]:
        return stock_lookup["by_symbol"][symbol].get("isin")
    else:
        logger.warning(f"ISIN not found for symbol: {symbol}")
        return None


def fetch_stock_data(
    symbol: str, days: int = 200, access_token: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """
    Fetch historical stock data from Upstox API using ISIN.

    Args:
        symbol: Stock symbol (e.g., 'RELIANCE')
        days: Number of days to fetch (default 200 to ensure 60+ after feature engineering)
        access_token: Upstox API token (defaults to Settings.UPSTOX_ACCESS_TOKEN)

    Returns:
        DataFrame with OHLCV data, or None if failed
    """
    if access_token is None:
        access_token = Settings.UPSTOX_ACCESS_TOKEN

    if not access_token:
        logger.error("UPSTOX_ACCESS_TOKEN not set")
        return None

    # Convert symbol to ISIN
    isin = get_isin_for_symbol(symbol)
    if isin is None:
        return None

    # Calculate date range
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    # Build URL using ISIN
    instrument_key = f"NSE_EQ%7C{isin}"  # Use ISIN, not symbol
    url = f"https://api.upstox.com/v3/historical-candle/{instrument_key}/days/1/{end_date}/{start_date}"

    headers = {"Accept": "application/json", "Authorization": f"Bearer {access_token}"}

    try:
        response = _session.get(url, headers=headers, timeout=15)

        if response.status_code == 200:
            data = response.json()

            if data.get("status") == "success" and "data" in data:
                candles = data["data"].get("candles", [])

                if not candles:
                    logger.warning(f"No data returned for {symbol}")
                    return None

                # Convert to DataFrame
                df = pd.DataFrame(
                    candles,
                    columns=["Date", "Open", "High", "Low", "Close", "Volume", "OI"],
                )
                df["Date"] = pd.to_datetime(df["Date"])
                df = df.sort_values("Date").reset_index(drop=True)
                df["Symbol"] = symbol

                logger.debug(f"Fetched {len(df)} days of data for {symbol}")
                return df
            else:
                logger.error(
                    f"API error for {symbol}: {data.get('message', 'Unknown')}"
                )
                return None
        else:
            logger.error(f"HTTP {response.status_code} for {symbol}")
            return None

    except Exception as e:
        logger.error(f"Exception fetching {symbol}: {str(e)}")
        return None


def fetch_nifty50_data(
    days: int = 200, access_token: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """
    Fetch NIFTY 50 index data for market context features.

    Args:
        days: Number of days to fetch
        access_token: Upstox API token (defaults to Settings.UPSTOX_ACCESS_TOKEN)

    Returns:
        DataFrame with Date and Nifty50_Close columns, or None if failed
    """
    if access_token is None:
        access_token = Settings.UPSTOX_ACCESS_TOKEN

    if not access_token:
        logger.error("UPSTOX_ACCESS_TOKEN not set")
        return None

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    instrument_key_encoded = "NSE_INDEX%7CNifty%2050"
    url = f"https://api.upstox.com/v3/historical-candle/{instrument_key_encoded}/days/1/{end_date}/{start_date}"

    headers = {"Accept": "application/json", "Authorization": f"Bearer {access_token}"}

    try:
        response = _session.get(url, headers=headers, timeout=15)

        if response.status_code == 200:
            data = response.json()

            if data.get("status") == "success" and "data" in data:
                candles = data["data"].get("candles", [])

                if not candles:
                    logger.warning("No NIFTY 50 data returned")
                    return None

                df = pd.DataFrame(
                    candles,
                    columns=["Date", "Open", "High", "Low", "Close", "Volume", "OI"],
                )
                df["Date"] = pd.to_datetime(df["Date"])
                df = df.sort_values("Date").reset_index(drop=True)
                df = df[["Date", "Close"]]
                df.rename(columns={"Close": "Nifty50_Close"}, inplace=True)

                logger.info(f"Fetched {len(df)} days of NIFTY 50 data")
                return df
            else:
                logger.error(
                    f"API error for NIFTY 50: {data.get('message', 'Unknown')}"
                )
                return None
        else:
            logger.error(f"HTTP {response.status_code} for NIFTY 50")
            return None

    except Exception as e:
        logger.error(f"Exception fetching NIFTY 50: {str(e)}")
        return None
