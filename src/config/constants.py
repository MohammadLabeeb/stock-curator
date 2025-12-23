"""
Constants used across the stock-curator project.
"""

# 47 feature names in exact order (as used during model training)
FEATURE_COLS = [
    # Basic OHLCV (6)
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
    "OI",
    # Moving Averages (10)
    "SMA_5",
    "SMA_10",
    "SMA_20",
    "SMA_50",
    "EMA_12",
    "EMA_26",
    "MACD",
    "MACD_Signal",
    "MACD_Hist",
    # RSI & Bollinger Bands (4)
    "RSI",
    "BB_Middle",
    "BB_Upper",
    "BB_Lower",
    # Volume indicators (2)
    "Volume_SMA_20",
    "Volume_Ratio",
    # Price-based features (10)
    "Daily_Return",
    "Price_Range",
    "Price_Change",
    "Return_3d",
    "Return_5d",
    "Return_10d",
    "Log_Return",
    "Volatility_5d",
    "Volatility_20d",
    "Momentum_10d",
    "Momentum_20d",
    # Advanced features - Market Context (3)
    "relative_strength_to_nifty50",
    "correlation_to_nifty50_20d",
    "market_regime",
    # Advanced features - Momentum & Mean Reversion (6)
    "rsi_divergence",
    "macd_crossover_signal",
    "bb_squeeze",
    "price_vs_sma50_pct",
    "momentum_strength",
    "support_resistance_distance",
    # Advanced features - Volume & Liquidity (3)
    "volume_price_trend",
    "on_balance_volume",
    "volume_breakout",
    # Advanced features - Statistical (3)
    "returns_skewness_20d",
    "returns_kurtosis_20d",
    "hurst_exponent",
]

# Model configuration
WINDOW_SIZE = 60  # Need 60 days of history for features
HORIZON = 7  # Predicting 7-day ahead direction

# News scraping
NEWS_SEARCH_KEYWORDS = (
    "nifty OR stock OR share OR sensex OR market OR equity OR buy OR sell"
)
NEWS_COUNTRY = "in"
NEWS_LANGUAGE = "en"
NEWS_COUNT = 20

# Timezone
IST_TIMEZONE = "Asia/Kolkata"
