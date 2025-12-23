"""
LLM-based stock recommendation extraction using Google Gemini.
Extracted from notebook: 01_data_ingestion_llm.ipynb
"""

import json
import logging
from typing import List, Dict

import google.generativeai as genai

from src.config.settings import Settings
from src.llm.prompts import create_extraction_prompt

logger = logging.getLogger(__name__)


def configure_gemini():
    """Configure the Gemini API with the API key."""
    if not Settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not set in environment variables")

    genai.configure(api_key=Settings.GEMINI_API_KEY)
    logger.info("Gemini API configured successfully")


def extract_recommendations(news_items: List[Dict]) -> List[Dict]:
    """
    Extract stock recommendations from news articles using Gemini LLM.

    Args:
        news_items: List of news articles (each with 'id', 'title', 'text', 'summary')

    Returns:
        List of extracted recommendations (dictionaries)

    Raises:
        ValueError: If Gemini API key is not set
        json.JSONDecodeError: If LLM response is not valid JSON
        Exception: If API call fails
    """
    configure_gemini()

    # Create the extraction prompt
    prompt = create_extraction_prompt(news_items)

    logger.info(f"Extracting recommendations from {len(news_items)} news articles...")

    try:
        # Use Gemini 2.5 Flash for fast and efficient extraction
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)

        # Extract JSON from response
        response_text = response.text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]

        # Parse JSON
        recommendations = json.loads(response_text.strip())

        # Filter out null recommendations
        valid_recommendations = [
            rec for rec in recommendations
            if rec.get('stock_name') is not None
        ]

        logger.info(f"Successfully extracted {len(valid_recommendations)} recommendations")

        return valid_recommendations

    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        logger.error(f"Response: {response.text}")
        raise

    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}")
        raise


def save_llm_recommendations(recommendations: List[Dict], date_str: str):
    """
    Save LLM recommendations to file.

    Args:
        recommendations: List of recommendation dictionaries
        date_str: Date string in YYYY-MM-DD format
    """
    output_dir = Settings.PROCESSED_DIR / "recommendations"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"llm_recommendations_{date_str}.json"

    with open(output_file, 'w') as f:
        json.dump(recommendations, f, indent=4)

    logger.info(f"Saved {len(recommendations)} LLM recommendations to {output_file}")
