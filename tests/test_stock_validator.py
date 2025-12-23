"""
Tests for stock validation module.
"""

import pytest
from src.data.stock_validator import validate_and_enrich_stock


def test_validate_ipo_stock():
    """Test that IPO stocks are handled correctly"""
    stock, method = validate_and_enrich_stock("Test IPO Company", is_ipo=True)

    assert stock is not None
    assert stock['name'] == "Test IPO Company"
    assert stock['trading_symbol'] == 'IPO_PENDING'
    assert stock['is_ipo'] is True
    assert method == "ipo_stock"


def test_validate_none_stock():
    """Test that None input returns None"""
    stock, method = validate_and_enrich_stock(None)

    assert stock is None
    assert method is None


def test_validate_empty_stock():
    """Test that empty string input returns None"""
    stock, method = validate_and_enrich_stock("")

    assert stock is None
    assert method is None


# Note: Testing actual stock validation requires the stock_lookup.json file
# which may not be available in CI environment. These tests would need mocking.
