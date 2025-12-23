"""
Tests for configuration modules.
"""

import pytest
from src.config.settings import Settings
from src.config.constants import FEATURE_COLS, WINDOW_SIZE, HORIZON


def test_feature_cols_count():
    """Test that we have exactly 47 features"""
    assert len(FEATURE_COLS) == 47, "Should have 47 features"


def test_window_size():
    """Test window size is correctly set"""
    assert WINDOW_SIZE == 60, "Window size should be 60 days"


def test_horizon():
    """Test prediction horizon is correctly set"""
    assert HORIZON == 7, "Prediction horizon should be 7 days"


def test_settings_paths_exist():
    """Test that Settings defines required paths"""
    assert hasattr(Settings, 'BASE_DIR')
    assert hasattr(Settings, 'DATA_DIR')
    assert hasattr(Settings, 'MODELS_DIR')
    assert hasattr(Settings, 'DAILY_RESULTS_DIR')
    assert hasattr(Settings, 'MODEL_PATH')
    assert hasattr(Settings, 'SCALER_PATH')
    assert hasattr(Settings, 'STOCK_LOOKUP_PATH')


def test_settings_api_keys():
    """Test that Settings defines API key attributes"""
    assert hasattr(Settings, 'WORLD_NEWS_API_KEY')
    assert hasattr(Settings, 'GEMINI_API_KEY')
    assert hasattr(Settings, 'UPSTOX_ACCESS_TOKEN')
