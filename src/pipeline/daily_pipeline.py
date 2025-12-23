"""
Main daily pipeline orchestrator.
Coordinates: News scraping → LLM extraction → Validation → ML prediction → Save results
"""

import logging

from src.config.settings import Settings
from src.data.news_scraper import scrape_news
from src.llm.extractor import extract_recommendations
from src.data.stock_validator import validate_stocks
from src.data.stock_fetcher import fetch_nifty50_data
from src.models.predictor import predict_all_stocks
from src.pipeline.data_saver import save_daily_results
from src.utils.logging_config import setup_logging
from src.utils.helpers import get_trading_date, format_ist_timestamp

logger = logging.getLogger(__name__)


def main():
    """
    Main entry point for the daily stock curation pipeline.

    Steps:
    1. Setup logging
    2. Validate configuration
    3. Check if already ran today
    4. Scrape news from World News API
    5. Extract recommendations via Gemini LLM
    6. Validate stock symbols against NSE master list
    7. Fetch NIFTY 50 data for market context
    8. Run ML predictions on validated stocks
    9. Save combined results to JSON

    Returns:
        Path to output file or None if skipped/failed
    """
    # 1. Setup
    setup_logging(level="INFO")
    logger.info("=" * 80)
    logger.info("STOCK CURATOR - DAILY PIPELINE")
    logger.info(f"Started at: {format_ist_timestamp()}")
    logger.info("=" * 80)

    # 2. Validate configuration
    try:
        Settings.validate()
        logger.info("Configuration validated")
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        return None

    # 3. Check if already ran today
    today = get_trading_date()
    result_file = Settings.DAILY_RESULTS_DIR / f"{today}_predictions.json"

    if result_file.exists():
        logger.info(f"Already ran for {today}, skipping")
        logger.info(f"Existing results: {result_file}")
        return result_file

    logger.info(f"Running pipeline for date: {today}")

    try:
        # 4. Scrape news
        logger.info("\n" + "=" * 80)
        logger.info("STEP 1/5: Scraping financial news")
        logger.info("=" * 80)
        news_articles = scrape_news()
        logger.info(f"✓ Scraped {len(news_articles)} articles")

        # 5. LLM extraction
        logger.info("\n" + "=" * 80)
        logger.info("STEP 2/5: Extracting recommendations via LLM")
        logger.info("=" * 80)
        llm_recs = extract_recommendations(news_articles)
        logger.info(f"✓ Extracted {len(llm_recs)} recommendations")

        # 5.5 Add news URLs to recommendations
        news_url_map = {
            str(article.get("id")): article.get("url") for article in news_articles
        }
        for rec in llm_recs:
            news_id = str(rec.get("news_id", ""))
            if news_id in news_url_map:
                rec["news_url"] = news_url_map[news_id]
        logger.info("✓ Added news URLs to recommendations")

        # 6. Validate stocks
        logger.info("\n" + "=" * 80)
        logger.info("STEP 3/5: Validating stock symbols")
        logger.info("=" * 80)
        validated_recs = validate_stocks(llm_recs)
        validated_count = sum(1 for r in validated_recs if r.get("validated"))
        logger.info(f"✓ Validated {validated_count}/{len(validated_recs)} stocks")

        # Handle case when no recommendations found
        if len(validated_recs) == 0:
            logger.warning("⚠ No stock recommendations found in news articles")
            logger.warning("This could be due to:")
            logger.warning("  - Weekend/holiday with no relevant news")
            logger.warning(
                "  - News articles not containing stock-specific information"
            )
            logger.warning("  - LLM unable to extract stocks from available news")
            logger.info("\nSaving empty results and exiting gracefully...")
            output_file = save_daily_results(today, [], [])
            logger.info(f"✓ Empty results saved to {output_file}")
            logger.info("=" * 80)
            logger.info("Pipeline completed (no recommendations to process)")
            logger.info("=" * 80)
            return

        # 7. Fetch NIFTY 50 for market context
        logger.info("\n" + "=" * 80)
        logger.info("STEP 4/5: Fetching NIFTY 50 data")
        logger.info("=" * 80)
        nifty50_df = fetch_nifty50_data()
        if nifty50_df is not None:
            logger.info(f"✓ Fetched {len(nifty50_df)} days of NIFTY 50 data")
        else:
            logger.warning("⚠ NIFTY 50 data not available, using defaults")

        # 8. ML predictions
        logger.info("\n" + "=" * 80)
        logger.info("STEP 5/5: Running ML predictions")
        logger.info("=" * 80)
        ml_predictions = predict_all_stocks(validated_recs, nifty50_df)
        success_count = sum(1 for p in ml_predictions if p["status"] == "SUCCESS")
        logger.info(f"✓ Predicted {success_count}/{len(ml_predictions)} stocks")

        # 9. Save results
        logger.info("\n" + "=" * 80)
        logger.info("SAVING RESULTS")
        logger.info("=" * 80)
        output_file = save_daily_results(today, validated_recs, ml_predictions)
        logger.info(f"✓ Results saved to {output_file}")

        # Final summary
        logger.info("\n" + "=" * 80)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        logger.info(f"Date: {today}")
        logger.info(f"News articles: {len(news_articles)}")
        logger.info(f"LLM recommendations: {len(llm_recs)}")
        logger.info(f"Validated stocks: {validated_count}")
        logger.info(f"ML predictions: {success_count}")
        logger.info(f"Output: {output_file}")
        logger.info(f"Finished at: {format_ist_timestamp()}")
        logger.info("=" * 80)

        return output_file

    except Exception as e:
        logger.error(f"\n{'=' * 80}")
        logger.error("PIPELINE FAILED")
        logger.error(f"{'=' * 80}")
        logger.error(f"Error: {str(e)}", exc_info=True)
        logger.error(f"{'=' * 80}")
        raise


if __name__ == "__main__":
    main()
