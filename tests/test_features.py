"""
Tests for feature engineering modules.
"""

import pytest
import pandas as pd
import numpy as np
from src.features.basic_indicators import calculate_basic_features


def create_sample_dataframe(rows=100):
    """Create sample OHLCV data for testing"""
    return pd.DataFrame({
        'Open': np.random.uniform(100, 110, rows),
        'High': np.random.uniform(110, 120, rows),
        'Low': np.random.uniform(90, 100, rows),
        'Close': np.random.uniform(100, 110, rows),
        'Volume': np.random.uniform(1000, 2000, rows),
        'OI': np.random.uniform(500, 1000, rows)
    })


def test_calculate_basic_features():
    """Test that basic features are calculated correctly"""
    df = create_sample_dataframe()
    result = calculate_basic_features(df)

    # Check that all expected features exist
    expected_features = [
        'SMA_5', 'SMA_10', 'SMA_20', 'SMA_50',
        'EMA_12', 'EMA_26', 'MACD', 'MACD_Signal', 'MACD_Hist',
        'RSI', 'BB_Middle', 'BB_Upper', 'BB_Lower',
        'Volume_SMA_20', 'Volume_Ratio',
        'Daily_Return', 'Price_Range', 'Price_Change',
        'Return_3d', 'Return_5d', 'Return_10d', 'Log_Return',
        'Volatility_5d', 'Volatility_20d',
        'Momentum_10d', 'Momentum_20d'
    ]

    for feature in expected_features:
        assert feature in result.columns, f"Feature {feature} not found"


def test_rsi_bounds():
    """Test that RSI values are within valid range [0, 100]"""
    df = create_sample_dataframe()
    result = calculate_basic_features(df)

    rsi_values = result['RSI'].dropna()
    assert (rsi_values >= 0).all(), "RSI should be >= 0"
    assert (rsi_values <= 100).all(), "RSI should be <= 100"


def test_bollinger_bands_relationship():
    """Test that BB_Upper > BB_Middle > BB_Lower"""
    df = create_sample_dataframe()
    result = calculate_basic_features(df)

    # Remove NaN rows
    valid_rows = result.dropna(subset=['BB_Upper', 'BB_Middle', 'BB_Lower'])

    assert (valid_rows['BB_Upper'] >= valid_rows['BB_Middle']).all(), "BB_Upper should be >= BB_Middle"
    assert (valid_rows['BB_Middle'] >= valid_rows['BB_Lower']).all(), "BB_Middle should be >= BB_Lower"


def test_volume_ratio_positive():
    """Test that volume ratio is positive"""
    df = create_sample_dataframe()
    result = calculate_basic_features(df)

    volume_ratio = result['Volume_Ratio'].dropna()
    assert (volume_ratio > 0).all(), "Volume ratio should be positive"
