"""
LLM prompt templates for stock recommendation extraction.
Extracted from notebook: 01_data_ingestion_llm.ipynb
"""

from typing import List, Dict


def create_extraction_prompt(news_items: List[Dict]) -> str:
    """
    Create a comprehensive prompt for Gemini to extract stock recommendations from news.

    Args:
        news_items: List of news articles (each with 'id', 'title', 'text', 'summary')

    Returns:
        Formatted prompt string for the LLM
    """

    # Prepare news text
    news_text = ""
    for idx, item in enumerate(news_items, 1):
        news_text += f"\n\n--- NEWS ID: {item['id']} ---\n"
        news_text += f"Title: {item['title']}\n"
        news_text += f"Text: {item['text']}\n"
        # Summary field is optional in World News API response
        if "summary" in item and item["summary"]:
            news_text += f"Summary: {item['summary']}\n"

    prompt = f"""You are a financial analyst expert in Indian stock markets (NSE/BSE).
Extract stock information from financial news articles based on market-relevant events.

{news_text}

TASK:
Extract stocks mentioned in these contexts:

1. **EXPLICIT RECOMMENDATIONS**: Buy/Sell/Hold ratings with target prices
2. **IPO ANNOUNCEMENTS**: Upcoming listings, IPO launches
3. **EARNINGS/RESULTS**: Strong/weak quarterly results, earnings beats/misses
4. **CORPORATE ACTIONS**: Stock splits, dividends, buybacks
5. **CONTRACT WINS**: Major order announcements, government contracts
6. **ANALYST COVERAGE**: Stocks added to watchlists, coverage initiations
7. **SIGNIFICANT NEWS**: Strategic deals, expansions, regulatory approvals

EXTRACTION RULES:
- Extract ANY stock with market-relevant news (not just formal recommendations)
- Use exact company names as mentioned
- Infer sentiment from context (positive news → "BUY_SIGNAL", negative → "SELL_SIGNAL")
- Set appropriate action_to_take based on news type
- Extract IPOs even if just announced (set is_ipo=true, action="IPO_WATCH")

ACTION MAPPING:
- Explicit "Buy" recommendation → "BUY"
- Explicit "Sell" recommendation → "SELL"
- Explicit "Hold" recommendation → "HOLD"
- Positive news (earnings beat, contract win, etc.) → "BUY_SIGNAL"
- Negative news (earnings miss, loss, etc.) → "SELL_SIGNAL"
- Neutral/watchlist mention → "WATCH"
- IPO announcement → "IPO_WATCH"

**DEDUPLICATION:**
If same stock appears multiple times in one article:
- Conflicting signals: Create separate entries
- Similar signals: Merge with combined reasoning, average prices, lowest confidence

OUTPUT FORMAT (JSON):
[
{{
    "news_id": <news_id>,
    "stock_name": "<company name>",
    "is_ipo": true|false,
    "ipo_details": {{
        "expected_listing_date": "<date or null>",
        "price_range": "<range or null>",
        "issue_size": "<size or null>"
    }} or null,
    "news_type": "recommendation|ipo|earnings|contract|corporate_action|analyst_coverage|strategic",
    "reason_for_recommendation": "<specific catalyst/reason>",
    "action_to_take": "BUY|SELL|HOLD|BUY_SIGNAL|SELL_SIGNAL|WATCH|IPO_WATCH|null",
    "buy_price": <float or null>,
    "target_price": <float or null>,
    "target_price_range": {{"min": <float>, "max": <float>}} or null,
    "timeframe": "<timeframe or null>",
    "confidence": <0.0 to 1.0>,
    "sentiment": "positive|negative|neutral",
    "analyst_consensus": "unanimous|mixed|conflicting|null"
}}
]

EXAMPLES:

Example 1 - Earnings Beat:
"Reliance Industries reported strong Q2 earnings with 25% YoY profit growth"
{{
    "news_id": "12345",
    "stock_name": "Reliance Industries",
    "is_ipo": false,
    "news_type": "earnings",
    "reason_for_recommendation": "Strong Q2 earnings with 25% YoY profit growth",
    "action_to_take": "BUY_SIGNAL",
    "sentiment": "positive",
    "confidence": 0.75
}}

Example 2 - Contract Win:
"L&T awarded Rs 5000 crore highway construction contract by government"
{{
    "stock_name": "L&T",
    "is_ipo": false,
    "news_type": "contract",
    "reason_for_recommendation": "Awarded Rs 5000 crore government highway contract",
    "action_to_take": "BUY_SIGNAL",
    "sentiment": "positive",
    "confidence": 0.8
}}

Example 3 - Stock Split:
"Tata Motors announces 1:2 stock split to improve liquidity"
{{
    "stock_name": "Tata Motors",
    "is_ipo": false,
    "news_type": "corporate_action",
    "reason_for_recommendation": "1:2 stock split announced to improve liquidity",
    "action_to_take": "WATCH",
    "sentiment": "neutral",
    "confidence": 0.65
}}

Example 4 - Watchlist:
"Add these 5 stocks to your radar: HDFC Bank, Infosys..."
{{
    "stock_name": "HDFC Bank",
    "is_ipo": false,
    "news_type": "analyst_coverage",
    "reason_for_recommendation": "Added to analyst watchlist",
    "action_to_take": "WATCH",
    "sentiment": "positive",
    "confidence": 0.6
}}

Example 5 - IPO:
"Tata Capital's $1.7B IPO opens next week"
{{
    "stock_name": "Tata Capital Ltd.",
    "is_ipo": true,
    "ipo_details": {{"issue_size": "$1.7 billion"}},
    "news_type": "ipo",
    "reason_for_recommendation": "Upcoming $1.7B IPO from Tata Group",
    "action_to_take": "IPO_WATCH",
    "sentiment": "neutral",
    "confidence": 0.7
}}

Example 6 - Explicit Rating:
"Analysts recommend buying HDFC Bank with target ₹1800"
{{
    "stock_name": "HDFC Bank",
    "is_ipo": false,
    "news_type": "recommendation",
    "reason_for_recommendation": "Analyst buy recommendation",
    "action_to_take": "BUY",
    "target_price": 1800,
    "sentiment": "positive",
    "confidence": 0.9
}}

Example 7 - Negative News:
"Zomato reports quarterly loss, misses revenue estimates"
{{
    "stock_name": "Zomato",
    "is_ipo": false,
    "news_type": "earnings",
    "reason_for_recommendation": "Quarterly loss, missed revenue estimates",
    "action_to_take": "SELL_SIGNAL",
    "sentiment": "negative",
    "confidence": 0.75
}}

If NO market-relevant stocks found:
{{
    "news_id": <news_id>,
    "stock_name": null,
    "is_ipo": null,
    "ipo_details": null,
    "news_type": null,
    "reason_for_recommendation": null,
    "action_to_take": null,
    "buy_price": null,
    "target_price": null,
    "target_price_range": null,
    "timeframe": null,
    "confidence": 0.0,
    "sentiment": null,
    "analyst_consensus": null
}}

Return ONLY valid JSON, no additional text."""

    return prompt
