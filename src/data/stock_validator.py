"""
Stock symbol validation and enrichment.
Extracted from notebook: 01_data_ingestion_llm.ipynb
"""

import json
import re
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple

from src.config.settings import Settings

logger = logging.getLogger(__name__)

# Global variable to cache stock lookup dictionary
_stock_lookup_cache = None


def load_stock_lookup() -> Dict:
    """
    Load and cache stock lookup dictionary.

    Returns:
        Dictionary with 'by_name' and 'by_symbol' mappings
    """
    global _stock_lookup_cache

    if _stock_lookup_cache is not None:
        return _stock_lookup_cache

    if not Settings.STOCK_LOOKUP_PATH.exists():
        raise FileNotFoundError(
            f"Stock lookup file not found: {Settings.STOCK_LOOKUP_PATH}"
        )

    with open(Settings.STOCK_LOOKUP_PATH, "r") as f:
        _stock_lookup_cache = json.load(f)

    logger.info(
        f"Loaded stock lookup with {len(_stock_lookup_cache['by_symbol'])} stocks"
    )
    return _stock_lookup_cache


def create_lookup_dict(stocks_db: List[Dict]) -> Dict:
    """
    Create lookup dictionaries for efficient stock validation.

    Args:
        stocks_db: List of stock dictionaries from filtered_stock_data.json

    Returns:
        Dictionary with 'by_name' and 'by_symbol' lookup mappings
    """
    lookup = {
        "by_name": {},
        "by_symbol": {},
    }

    for stock in stocks_db:
        # Normalize names for matching
        normalized_name = stock["name"].lower().strip()
        lookup["by_name"][normalized_name] = stock
        lookup["by_symbol"][stock["trading_symbol"].upper()] = stock

        # Add common variations
        # Remove "LIMITED", "LTD", "PVT" etc.
        short_name = normalized_name.replace(" limited", "").replace(" ltd", "")
        short_name = short_name.replace(" pvt", "").strip()
        lookup["by_name"][short_name] = stock

    return lookup


def validate_and_enrich_stock(
    stock_name: str, is_ipo: bool = False
) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Validate stock name and return enriched data from NSE master list.

    This function implements comprehensive fuzzy matching logic including:
    - Exact symbol matching
    - Exact name matching
    - Normalized name matching (removing Ltd, Limited, etc.)
    - Abbreviation matching
    - Acronym matching (e.g., SBI -> State Bank of India)
    - Special handling for banks and insurance companies

    Args:
        stock_name: Company name or symbol from LLM
        is_ipo: Whether this is an IPO (not yet listed)

    Returns:
        Tuple of (stock_dict, match_method) or (None, None) if not found
    """
    stock_lookup = load_stock_lookup()

    if not stock_name:
        return None, None

    # Handle IPOs
    if is_ipo:
        ipo_stock = {
            "name": stock_name,
            "trading_symbol": "IPO_PENDING",
            "instrument_key": None,
            "isin": None,
            "is_ipo": True,
        }
        return ipo_stock, "ipo_stock"

    stock_name = stock_name.strip()

    # Try exact symbol match first
    if stock_name.upper() in stock_lookup["by_symbol"]:
        return stock_lookup["by_symbol"][stock_name.upper()], "symbol match"

    # Try exact name match
    normalized = stock_name.lower()
    if normalized in stock_lookup["by_name"]:
        return stock_lookup["by_name"][normalized], "name match"

    # Helper functions for fuzzy matching
    def normalize_for_matching(text):
        """Remove common suffixes and standardize text"""
        text = text.lower()
        # Remove common suffixes
        text = re.sub(
            r"\s+(ltd\.?|limited|pvt\.?|private|inc\.?|incorporated|corp\.?|corporation)$",
            "",
            text,
        )
        # Remove extra whitespace and special characters
        text = re.sub(r"[&\-\.\,]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def extract_key_words(text):
        """Extract significant words, handling abbreviations"""
        text = normalize_for_matching(text)
        words = text.split()
        # Remove very common filler words
        stop_words = {"and", "the", "of", "a", "an", "in", "on", "at", "to", "for"}
        return [w for w in words if w not in stop_words and len(w) > 1]

    def is_abbreviation_match(word, abbreviated):
        """Check if abbreviated form matches word"""
        if word.startswith(abbreviated) or abbreviated.startswith(word):
            return True
        # Check if it could be an abbreviation (first few letters match)
        if len(abbreviated) >= 4 and len(word) >= 4:
            return abbreviated[:4] == word[:4]
        return False

    def matches_acronym(acronym, full_name):
        """Check if acronym matches the first letters of words in full name"""
        acronym = acronym.upper()
        words = extract_key_words(full_name)

        if len(acronym) != len(words):
            return False

        for i, word in enumerate(words):
            if i >= len(acronym):
                return False
            if word[0].upper() != acronym[i]:
                return False

        return True

    normalized_input = normalize_for_matching(stock_name)
    input_words = extract_key_words(stock_name)

    # Special handling for bank stocks
    bank_keywords = ["hdfc", "icici", "sbi", "axis", "kotak", "bank"]
    is_bank_query = any(keyword in normalized_input for keyword in bank_keywords)

    if is_bank_query:
        # For bank queries, prioritize actual banks over ETFs/AMCs
        best_match = None
        best_score = 0

        for key, stock in stock_lookup["by_name"].items():
            key_lower = key.lower()
            normalized_key = normalize_for_matching(key)

            # Skip ETFs and AMCs when looking for banks
            if "etf" in key_lower or "amc" in key_lower or "pramc" in key_lower:
                continue

            # For insurance companies, only match if "insurance" or "life" is in the query
            if "insurance" in key_lower or "life" in key_lower:
                if (
                    "insurance" not in normalized_input
                    and "life" not in normalized_input
                ):
                    continue

            # Must contain "bank" for bank queries
            if "bank" not in key_lower:
                continue

            # Check short_name field if available
            short_name_match = False
            if "short_name" in stock:
                short_name_lower = stock["short_name"].lower()
                if (
                    normalized_input == short_name_lower
                    or stock_name.upper() == stock["short_name"].upper()
                ):
                    return stock, "short name match"
                if (
                    normalized_input in short_name_lower
                    or short_name_lower in normalized_input
                ):
                    short_name_match = True

            # Check for acronym match (e.g., SBI -> State Bank India)
            acronym_match = False
            if len(stock_name) <= 5 and stock_name.isalpha() and stock_name.isupper():
                if matches_acronym(stock_name, key):
                    acronym_match = True

            key_words = extract_key_words(key)

            # Calculate match score
            matches = 0
            for input_word in input_words:
                for key_word in key_words:
                    if input_word == key_word or is_abbreviation_match(
                        input_word, key_word
                    ):
                        matches += 1
                        break

            # For short queries like "HDFC", "ICICI", "SBI", be more lenient
            if len(input_words) <= 2:
                for input_word in input_words:
                    if input_word in normalized_key:
                        matches += 2  # Boost score for direct substring match

            score = matches / max(len(input_words), 1)

            # Boost for acronym match
            if acronym_match:
                score += 1.0

            # Boost for short name match
            if short_name_match:
                score += 0.8

            # Prioritize stocks with "bank ltd" or "bank limited" (actual banks)
            if "bank ltd" in key_lower or "bank limited" in key_lower:
                score += 0.5

            if score > best_score:
                best_score = score
                best_match = stock

        if best_match and best_score > 0.5:
            return best_match, "bank priority match"

    # General fuzzy matching for all stocks
    best_match = None
    best_score = 0

    for key, stock in stock_lookup["by_name"].items():
        normalized_key = normalize_for_matching(key)
        key_words = extract_key_words(key)

        # Check short_name field if available
        if "short_name" in stock:
            short_name_lower = stock["short_name"].lower()
            if (
                normalized_input == short_name_lower
                or stock_name.upper() == stock["short_name"].upper()
            ):
                return stock, "short name match"

        # Calculate matching score based on word overlap with abbreviation support
        matches = 0
        for input_word in input_words:
            for key_word in key_words:
                if input_word == key_word or is_abbreviation_match(
                    input_word, key_word
                ):
                    matches += 1
                    break

        # Need at least half of the input words to match
        if len(input_words) == 0:
            continue

        score = matches / len(input_words)

        # Boost score if there's also a substring match
        if normalized_input in normalized_key or normalized_key in normalized_input:
            score += 0.3

        # Also check if most of the key words are matched (for abbreviated cases)
        if len(key_words) > 0:
            reverse_score = matches / len(key_words)
            score = max(score, reverse_score)

        if score > best_score:
            best_score = score
            best_match = stock

    # Lower threshold for better recall
    if best_match and best_score > 0.4:
        return best_match, "fuzzy match"

    return None, None


def validate_stocks(llm_recommendations: List[Dict]) -> List[Dict]:
    """
    Validate and enrich all LLM recommendations with stock data.

    Args:
        llm_recommendations: List of recommendations from LLM

    Returns:
        List of validated and enriched recommendations
    """
    validated = []

    logger.info(f"Validating {len(llm_recommendations)} LLM recommendations...")

    for rec in llm_recommendations:
        stock_name = rec.get("stock_name")
        is_ipo = rec.get("is_ipo", False)

        if not stock_name:
            continue

        stock_data, method = validate_and_enrich_stock(stock_name, is_ipo=is_ipo)

        if stock_data:
            enriched_rec = {
                **rec,
                "equity_name": stock_data["name"],
                "instrument_key": stock_data.get("instrument_key"),
                "trading_symbol": stock_data["trading_symbol"],
                "isin": stock_data.get("isin"),
                "validated": True,
                "validation_method": method,
                "extraction_timestamp": datetime.now().isoformat(),
            }
            validated.append(enriched_rec)
        else:
            # Stock not found
            enriched_rec = {
                **rec,
                "equity_name": stock_name,
                "instrument_key": None,
                "trading_symbol": None,
                "isin": None,
                "validated": False,
                "validation_error": "Stock not found in master database",
                "extraction_timestamp": datetime.now().isoformat(),
            }
            validated.append(enriched_rec)

    success_count = sum(1 for r in validated if r["validated"])
    logger.info(
        f"Validation complete: {success_count}/{len(validated)} stocks validated "
        f"({success_count / len(validated) * 100:.1f}%)"
    )

    return validated


def save_validated_recommendations(recommendations: List[Dict], date_str: str):
    """
    Save validated recommendations to file.

    Args:
        recommendations: List of validated recommendation dictionaries
        date_str: Date string in YYYY-MM-DD format
    """
    output_dir = Settings.PROCESSED_DIR / "recommendations"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save all recommendations
    all_output_file = output_dir / f"all_recommendations_{date_str}.json"
    with open(all_output_file, "w") as f:
        json.dump(recommendations, f, indent=2)

    # Save only validated recommendations
    validated_only = [r for r in recommendations if r.get("validated")]
    validated_output_file = output_dir / f"validated_recommendations_{date_str}.json"
    with open(validated_output_file, "w") as f:
        json.dump(validated_only, f, indent=2)

    logger.info(
        f"Saved {len(validated_only)} validated recommendations to {validated_output_file}"
    )
