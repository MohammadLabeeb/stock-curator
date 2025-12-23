"""
Advanced technical indicators (15 features).
Extracted from notebooks: 09_advanced_technical_features.ipynb and 10_production_ml_filter.ipynb
"""

import numpy as np
import pandas as pd
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def calculate_advanced_features(df: pd.DataFrame, nifty50_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    Calculate advanced technical features (15 features).

    Features calculated:
    - Market Context (3): relative_strength_to_nifty50, correlation_to_nifty50_20d, market_regime
    - Momentum & Mean Reversion (6): rsi_divergence, macd_crossover_signal, bb_squeeze,
                                      price_vs_sma50_pct, momentum_strength, support_resistance_distance
    - Volume & Liquidity (3): volume_price_trend, on_balance_volume, volume_breakout
    - Statistical (3): returns_skewness_20d, returns_kurtosis_20d, hurst_exponent

    Args:
        df: DataFrame with basic features already calculated
        nifty50_df: Optional DataFrame with NIFTY 50 data (Date, Nifty50_Close)

    Returns:
        DataFrame with all advanced features added
    """
    df = df.copy()

    # ========== MARKET CONTEXT FEATURES (3) ==========
    if nifty50_df is not None:
        # Merge NIFTY 50 data
        df = df.merge(nifty50_df, on='Date', how='left')
        df['Nifty50_Return'] = df['Nifty50_Close'].pct_change() * 100

        # Relative strength to NIFTY 50
        df['relative_strength_to_nifty50'] = df['Daily_Return'] - df['Nifty50_Return']

        # Correlation to NIFTY 50 (20-day rolling)
        df['correlation_to_nifty50_20d'] = df['Daily_Return'].rolling(20).corr(df['Nifty50_Return'])

        # Market regime (bullish/bearish based on NIFTY SMA crossover)
        nifty_sma_20 = df['Nifty50_Close'].rolling(20).mean()
        nifty_sma_50 = df['Nifty50_Close'].rolling(50).mean()
        df['market_regime'] = 0
        df.loc[nifty_sma_20 > nifty_sma_50, 'market_regime'] = 1  # Bullish
        df.loc[nifty_sma_20 < nifty_sma_50, 'market_regime'] = -1  # Bearish

        # Drop intermediate columns
        df.drop(columns=['Nifty50_Close', 'Nifty50_Return'], inplace=True)
    else:
        # If NIFTY data not available, use default values
        logger.warning("NIFTY 50 data not provided, using default values for market context features")
        df['relative_strength_to_nifty50'] = 0.0
        df['correlation_to_nifty50_20d'] = 0.0
        df['market_regime'] = 0

    # ========== MOMENTUM & MEAN REVERSION (6) ==========

    # RSI Divergence (RSI direction vs price direction)
    rsi_change = df['RSI'].diff(5)
    price_change = df['Close'].pct_change(5)
    df['rsi_divergence'] = np.sign(rsi_change) - np.sign(price_change)

    # MACD Crossover Signal
    df['macd_crossover_signal'] = 0
    macd_cross_up = (df['MACD'] > df['MACD_Signal']) & (df['MACD'].shift(1) <= df['MACD_Signal'].shift(1))
    macd_cross_down = (df['MACD'] < df['MACD_Signal']) & (df['MACD'].shift(1) >= df['MACD_Signal'].shift(1))
    df.loc[macd_cross_up, 'macd_crossover_signal'] = 1
    df.loc[macd_cross_down, 'macd_crossover_signal'] = -1

    # Bollinger Band Squeeze (normalized BB width)
    bb_width = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle']
    df['bb_squeeze'] = bb_width.rolling(20).apply(
        lambda x: (x.iloc[-1] - x.min()) / (x.max() - x.min() + 1e-8),
        raw=False
    )

    # Price vs SMA50 (percentage deviation)
    df['price_vs_sma50_pct'] = ((df['Close'] - df['SMA_50']) / df['SMA_50']) * 100

    # Momentum Strength (change in momentum)
    df['momentum_strength'] = df['Momentum_10d'].diff(5)

    # Support/Resistance Distance
    high_20 = df['High'].rolling(20).max()
    low_20 = df['Low'].rolling(20).min()
    df['support_resistance_distance'] = np.where(
        df['Close'] > df['Close'].shift(1),
        (high_20 - df['Close']) / df['Close'],  # Distance to resistance
        (df['Close'] - low_20) / df['Close']   # Distance to support
    )

    # ========== VOLUME & LIQUIDITY (3) ==========

    # Volume Price Trend (cumulative volume * price direction)
    price_direction = np.sign(df['Close'].diff())
    df['volume_price_trend'] = (df['Volume'] * price_direction).cumsum()

    # On-Balance Volume
    obv = np.where(
        df['Close'] > df['Close'].shift(1),
        df['Volume'],
        np.where(df['Close'] < df['Close'].shift(1), -df['Volume'], 0)
    )
    df['on_balance_volume'] = obv.cumsum()

    # Volume Breakout (volume > 2x average)
    df['volume_breakout'] = (df['Volume'] > 2 * df['Volume_SMA_20']).astype(int)

    # ========== STATISTICAL (3) ==========

    # Returns Skewness (20-day)
    df['returns_skewness_20d'] = df['Daily_Return'].rolling(20).skew()

    # Returns Kurtosis (20-day)
    df['returns_kurtosis_20d'] = df['Daily_Return'].rolling(20).kurt()

    # Hurst Exponent (measure of mean reversion vs trending)
    def calculate_hurst(ts, lags=range(2, 20)):
        """Calculate Hurst exponent for a time series"""
        if len(ts) < max(lags):
            return 0.5

        tau = []
        lagvec = []

        for lag in lags:
            pp = np.subtract(ts[lag:], ts[:-lag])
            lagvec.append(lag)
            tau.append(np.std(pp))

        try:
            poly = np.polyfit(np.log(lagvec), np.log(tau), 1)
            return poly[0]
        except:
            return 0.5

    df['hurst_exponent'] = df['Close'].rolling(60).apply(
        lambda x: calculate_hurst(x.values),
        raw=False
    )

    # Drop NaN rows (from rolling calculations)
    df = df.dropna()

    logger.debug(f"Calculated {15} advanced features, {len(df)} rows remaining")
    return df


def calculate_all_features(df: pd.DataFrame, nifty50_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    Calculate all features (basic + advanced).

    Args:
        df: DataFrame with OHLCV data
        nifty50_df: Optional DataFrame with NIFTY 50 data

    Returns:
        DataFrame with all 47 features
    """
    from src.features.basic_indicators import calculate_basic_features

    # First calculate basic features
    df = calculate_basic_features(df)

    # Then calculate advanced features
    df = calculate_advanced_features(df, nifty50_df)

    logger.info(f"Calculated all 47 features, {len(df)} rows remaining")
    return df
