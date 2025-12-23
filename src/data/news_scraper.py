"""
News scraping functionality using World News API.
Extracts from notebook: 01_data_ingestion_llm.ipynb
"""

import re
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

import requests

from src.config.settings import Settings
from src.config.constants import (
    NEWS_SEARCH_KEYWORDS,
    NEWS_COUNTRY,
    NEWS_LANGUAGE,
    NEWS_COUNT,
)

logger = logging.getLogger(__name__)


def scrape_news(days_back: int = 1, save_to_file: bool = True) -> List[Dict]:
    """
    Scrape financial news from World News API.

    Args:
        days_back: Number of days back to search (default: 1)
        save_to_file: Whether to save raw news to file (default: True)

    Returns:
        List of news articles (dictionaries)

    Raises:
        requests.RequestException: If API call fails
        ValueError: If API key is not set
    """
    if not Settings.WORLD_NEWS_API_KEY:
        raise ValueError("WORLD_NEWS_API_KEY not set in environment variables")

    # Calculate date range
    published_after = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

    # API parameters
    params = {
        "text": NEWS_SEARCH_KEYWORDS,
        "source-country": NEWS_COUNTRY,
        "language": NEWS_LANGUAGE,
        "earliest-publish-date": published_after,
        "number": NEWS_COUNT,
    }

    headers = {"x-api-key": Settings.WORLD_NEWS_API_KEY}

    logger.info(f"Scraping news from {published_after} to now...")

    try:
        response = requests.get(
            "https://api.worldnewsapi.com/search-news",
            params=params,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()

        data = response.json()
        articles = data.get("news", [])

        logger.info(f"Successfully scraped {len(articles)} articles")

        # Clean article text (remove "Read more", "About", "Also Read" sections)
        for article in articles:
            if "text" in article:
                article["text"] = re.split(
                    r"Read more|About|Also Read", article["text"], flags=re.IGNORECASE
                )[0].strip()

        # Save to file if requested
        if save_to_file:
            today = datetime.now().strftime("%Y-%m-%d")
            Settings.RAW_NEWS_DIR.mkdir(parents=True, exist_ok=True)
            output_file = Settings.RAW_NEWS_DIR / f"worldnewsapi_{today}.json"

            with open(output_file, "w") as f:
                json.dump(data, f, indent=4)

            logger.info(f"Saved raw news to {output_file}")

        return articles

    except requests.RequestException as e:
        logger.error(f"Failed to scrape news: {e}")
        raise


def load_news_from_file(date_str: Optional[str] = None) -> List[Dict]:
    """
    Load previously scraped news from file.

    Args:
        date_str: Date string in YYYY-MM-DD format (default: today)

    Returns:
        List of news articles

    Raises:
        FileNotFoundError: If news file doesn't exist
    """
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    news_file = Settings.RAW_NEWS_DIR / f"worldnewsapi_{date_str}.json"

    if not news_file.exists():
        raise FileNotFoundError(f"News file not found: {news_file}")

    with open(news_file, "r") as f:
        data = json.load(f)

    articles = data.get("news", [])
    logger.info(f"Loaded {len(articles)} articles from {news_file}")

    return articles
