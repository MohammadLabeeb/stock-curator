"""
ML prediction functionality using trained XGBoost model.
Extracted from notebook: 10_production_ml_filter.ipynb
"""

import logging
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.config.constants import WINDOW_SIZE, FEATURE_COLS
from src.data.stock_fetcher import fetch_stock_data
from src.features.advanced_indicators import calculate_all_features
from src.models.loader import load_model_and_scaler

logger = logging.getLogger(__name__)


def prepare_stock_for_prediction(
    symbol: str,
    nifty50_df: Optional[pd.DataFrame] = None
) -> Tuple[Optional[np.ndarray], Optional[float], str, Optional[pd.DataFrame]]:
    """
    Full pipeline: Fetch data → Calculate features → Prepare for model.

    Args:
        symbol: Stock symbol (e.g., 'RELIANCE')
        nifty50_df: Optional NIFTY 50 DataFrame for market context features

    Returns:
        Tuple of (features_array, latest_close_price, symbol, historical_ohlcv)
        Returns (None, None, symbol, None) if preparation fails
    """
    # 1. Fetch stock data (250 days for buffer)
    df = fetch_stock_data(symbol, days=250)

    if df is None or len(df) < 70:
        logger.warning(f"{symbol}: Insufficient data")
        return None, None, symbol, None

    # 2. Calculate all features (basic + advanced)
    try:
        df = calculate_all_features(df, nifty50_df)
    except Exception as e:
        logger.error(f"{symbol}: Feature calculation failed - {str(e)}")
        return None, None, symbol, None

    if len(df) < WINDOW_SIZE:
        logger.warning(f"{symbol}: Not enough rows after feature engineering ({len(df)} < {WINDOW_SIZE})")
        return None, None, symbol, None

    # 3. Extract last 60 days of features
    features_df = df[FEATURE_COLS].tail(WINDOW_SIZE)

    if features_df.isnull().any().any():
        logger.warning(f"{symbol}: NaN values in features")
        return None, None, symbol, None

    # 4. Convert to array (shape: 60, 47)
    features_array = features_df.values
    latest_close = df['Close'].iloc[-1]

    # 5. Extract historical OHLCV data (last 60 days)
    historical_ohlcv = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].tail(WINDOW_SIZE).copy()
    # Convert Date to string format and set as index
    historical_ohlcv['Date'] = pd.to_datetime(historical_ohlcv['Date']).dt.strftime('%Y-%m-%d')
    historical_ohlcv = historical_ohlcv.set_index('Date')

    logger.debug(f"{symbol}: Successfully prepared features (shape: {features_array.shape})")
    return features_array, latest_close, symbol, historical_ohlcv


def predict_stock_direction(features_array: np.ndarray, model, scaler) -> Dict:
    """
    Predict 7-day direction for a single stock.

    Args:
        features_array: numpy array of shape (60, 47)
        model: Trained XGBoost model
        scaler: Fitted StandardScaler

    Returns:
        Dictionary with prediction, probability, and confidence:
        {
            'prediction': int (0 or 1),
            'direction': str ('UP' or 'DOWN'),
            'probability_up': float,
            'probability_down': float,
            'confidence': float (max probability)
        }
    """
    # 1. Reshape to (1, 60, 47) for single sample
    X = features_array.reshape(1, WINDOW_SIZE, -1)

    # 2. Scale features
    # Scaler was trained on (samples*60, 47), so we need to scale 47 features
    X_2d = X.reshape(-1, 47)  # Shape: (60, 47)
    X_scaled_2d = scaler.transform(X_2d)  # Scale each of the 47 features

    # 3. Reshape back to 3D then flatten for XGBoost
    X_scaled = X_scaled_2d.reshape(1, WINDOW_SIZE, -1)  # (1, 60, 47)
    X_flat = X_scaled.reshape(1, -1)  # (1, 2820)

    # 4. Predict
    prediction = model.predict(X_flat)[0]  # 0 or 1
    probabilities = model.predict_proba(X_flat)[0]  # [prob_down, prob_up]

    return {
        'prediction': int(prediction),
        'direction': 'UP' if prediction == 1 else 'DOWN',
        'probability_up': float(probabilities[1]),
        'probability_down': float(probabilities[0]),
        'confidence': float(max(probabilities))
    }


def predict_all_stocks(
    validated_recommendations: List[Dict],
    nifty50_df: Optional[pd.DataFrame] = None
) -> List[Dict]:
    """
    Get ML predictions for all validated LLM stock recommendations.

    Args:
        validated_recommendations: List of validated stock recommendations
        nifty50_df: Optional NIFTY 50 DataFrame

    Returns:
        List of prediction dictionaries
    """
    # Load model and scaler
    model, scaler = load_model_and_scaler()

    # Extract unique symbols
    symbols = list(set([
        rec['trading_symbol']
        for rec in validated_recommendations
        if rec.get('validated') and rec.get('trading_symbol') != 'IPO_PENDING'
    ]))

    logger.info(f"Predicting for {len(symbols)} stocks...")

    results = []

    for i, symbol in enumerate(symbols, 1):
        logger.info(f"[{i}/{len(symbols)}] Processing {symbol}...")

        # Prepare features
        features, latest_close, _, historical_ohlcv = prepare_stock_for_prediction(symbol, nifty50_df)

        if features is None:
            results.append({
                'symbol': symbol,
                'status': 'FAILED',
                'direction': 'N/A',
                'confidence': None,
                'probability_up': None,
                'probability_down': None,
                'latest_close': None,
                'historical_data': None,
                'error': 'Insufficient data or feature engineering failed'
            })
            logger.warning(f"{symbol}: FAILED (insufficient data)")
            continue

        # Predict
        try:
            pred = predict_stock_direction(features, model, scaler)

            results.append({
                'symbol': symbol,
                'status': 'SUCCESS',
                'direction': pred['direction'],
                'confidence': pred['confidence'],
                'probability_up': pred['probability_up'],
                'probability_down': pred['probability_down'],
                'latest_close': latest_close,
                'historical_data': historical_ohlcv.to_dict('index') if historical_ohlcv is not None else None,
                'error': None
            })

            direction_emoji = '📈' if pred['direction'] == 'UP' else '📉'
            logger.info(f"{direction_emoji} {symbol}: {pred['direction']} (confidence: {pred['confidence']:.1%})")

        except Exception as e:
            logger.error(f"{symbol}: Prediction failed - {str(e)}")
            results.append({
                'symbol': symbol,
                'status': 'FAILED',
                'direction': 'N/A',
                'confidence': None,
                'probability_up': None,
                'probability_down': None,
                'latest_close': latest_close,
                'historical_data': None,
                'error': str(e)
            })

    # Summary
    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    logger.info(f"Prediction complete: {success_count}/{len(symbols)} successful")

    return results
