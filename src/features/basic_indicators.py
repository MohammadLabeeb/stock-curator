"""
Basic technical indicators (32 features).
Extracted from notebook: 10_production_ml_filter.ipynb
"""

import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def calculate_basic_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate basic technical indicators (first 32 features).

    Assumes df has OHLCV columns: Open, High, Low, Close, Volume, OI

    Features calculated:
    - Simple Moving Averages (SMA_5, SMA_10, SMA_20, SMA_50)
    - Exponential Moving Averages (EMA_12, EMA_26)
    - MACD (MACD, MACD_Signal, MACD_Hist)
    - RSI
    - Bollinger Bands (BB_Middle, BB_Upper, BB_Lower)
    - Volume indicators (Volume_SMA_20, Volume_Ratio)
    - Price-based features (Daily_Return, Price_Range, Price_Change, etc.)
    - Historical returns (Return_3d, Return_5d, Return_10d, Log_Return)
    - Volatility (Volatility_5d, Volatility_20d)
    - Momentum (Momentum_10d, Momentum_20d)

    Args:
        df: DataFrame with OHLCV data

    Returns:
        DataFrame with all basic features added
    """
    df = df.copy()

    # Simple Moving Averages
    df['SMA_5'] = df['Close'].rolling(5).mean()
    df['SMA_10'] = df['Close'].rolling(10).mean()
    df['SMA_20'] = df['Close'].rolling(20).mean()
    df['SMA_50'] = df['Close'].rolling(50).mean()

    # Exponential Moving Averages
    df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()

    # MACD
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

    # RSI
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = -delta.where(delta < 0, 0).rolling(14).mean()
    rs = gain / (loss + 1e-8)
    df['RSI'] = 100 - (100 / (1 + rs))

    # Bollinger Bands
    df['BB_Middle'] = df['Close'].rolling(20).mean()
    bb_std = df['Close'].rolling(20).std()
    df['BB_Upper'] = df['BB_Middle'] + (2 * bb_std)
    df['BB_Lower'] = df['BB_Middle'] - (2 * bb_std)

    # Volume indicators
    df['Volume_SMA_20'] = df['Volume'].rolling(20).mean()
    df['Volume_Ratio'] = df['Volume'] / (df['Volume_SMA_20'] + 1e-8)

    # Price-based features
    df['Daily_Return'] = df['Close'].pct_change() * 100
    df['Price_Range'] = df['High'] - df['Low']
    df['Price_Change'] = df['Close'] - df['Open']

    # Historical returns
    df['Return_3d'] = df['Close'].pct_change(3) * 100
    df['Return_5d'] = df['Close'].pct_change(5) * 100
    df['Return_10d'] = df['Close'].pct_change(10) * 100
    df['Log_Return'] = np.log(df['Close'] / df['Close'].shift(1)) * 100

    # Volatility
    df['Volatility_5d'] = df['Daily_Return'].rolling(5).std()
    df['Volatility_20d'] = df['Daily_Return'].rolling(20).std()

    # Momentum
    df['Momentum_10d'] = df['Close'] - df['Close'].shift(10)
    df['Momentum_20d'] = df['Close'] - df['Close'].shift(20)

    logger.debug(f"Calculated {32} basic features")
    return df
