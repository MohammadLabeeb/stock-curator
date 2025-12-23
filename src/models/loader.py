"""
Model and scaler loading utilities.
"""

import pickle
import logging
from typing import Tuple, Any

from src.config.settings import Settings

logger = logging.getLogger(__name__)

# Global cache for models
_model_cache = None
_scaler_cache = None


def load_model_and_scaler() -> Tuple[Any, Any]:
    """
    Load the trained XGBoost model and feature scaler.

    Returns:
        Tuple of (model, scaler)

    Raises:
        FileNotFoundError: If model or scaler files don't exist
    """
    global _model_cache, _scaler_cache

    # Return cached versions if available
    if _model_cache is not None and _scaler_cache is not None:
        logger.debug("Using cached model and scaler")
        return _model_cache, _scaler_cache

    # Check files exist
    if not Settings.MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found: {Settings.MODEL_PATH}")
    if not Settings.SCALER_PATH.exists():
        raise FileNotFoundError(f"Scaler file not found: {Settings.SCALER_PATH}")

    # Load model
    with open(Settings.MODEL_PATH, "rb") as f:
        _model_cache = pickle.load(f)

    # Load scaler
    with open(Settings.SCALER_PATH, "rb") as f:
        _scaler_cache = pickle.load(f)

    logger.info("Model and scaler loaded successfully")
    return _model_cache, _scaler_cache


def clear_cache():
    """Clear the model and scaler cache."""
    global _model_cache, _scaler_cache
    _model_cache = None
    _scaler_cache = None
    logger.info("Model cache cleared")
