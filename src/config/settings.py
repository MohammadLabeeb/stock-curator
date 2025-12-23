"""
Configuration settings for the stock-curator project.
Loads environment variables and defines paths.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Configuration settings"""

    # ==================== API Keys ====================
    WORLD_NEWS_API_KEY = os.getenv("WORLD_NEWS_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    UPSTOX_ACCESS_TOKEN = os.getenv("UPSTOX_ACCESS_TOKEN")

    # ==================== Paths ====================
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    MODELS_DIR = DATA_DIR / "models"
    DAILY_RESULTS_DIR = DATA_DIR / "daily_results"
    RAW_NEWS_DIR = DATA_DIR / "raw" / "news"
    PROCESSED_DIR = DATA_DIR / "processed"

    # Stock data
    STOCK_LOOKUP_PATH = PROCESSED_DIR / "stock_lookup.json"
    FILTERED_STOCK_DATA_PATH = PROCESSED_DIR / "filtered_stock_data.json"

    # Model paths
    MODEL_PATH = MODELS_DIR / "xgboost_stock_direction_predictor.pkl"
    SCALER_PATH = MODELS_DIR / "feature_scaler.pkl"

    # ==================== ML Configuration ====================
    WINDOW_SIZE = 60  # Need 60 days of history
    HORIZON = 7  # Predicting 7-day ahead direction

    @classmethod
    def validate(cls):
        """Validate that required settings are present"""
        missing = []

        if not cls.WORLD_NEWS_API_KEY:
            missing.append("WORLD_NEWS_API_KEY")
        if not cls.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")
        if not cls.UPSTOX_ACCESS_TOKEN:
            missing.append("UPSTOX_ACCESS_TOKEN")

        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

        # Check critical files exist
        if not cls.STOCK_LOOKUP_PATH.exists():
            raise FileNotFoundError(
                f"Stock lookup file not found: {cls.STOCK_LOOKUP_PATH}"
            )
        if not cls.MODEL_PATH.exists():
            raise FileNotFoundError(f"Model file not found: {cls.MODEL_PATH}")
        if not cls.SCALER_PATH.exists():
            raise FileNotFoundError(f"Scaler file not found: {cls.SCALER_PATH}")

        return True
