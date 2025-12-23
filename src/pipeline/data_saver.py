"""
Data saving utilities for daily pipeline results.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict

from src.config.settings import Settings

logger = logging.getLogger(__name__)


def save_daily_results(date_str: str, llm_recs: List[Dict], ml_predictions: List[Dict]) -> Path:
    """
    Save combined LLM + ML results to JSON file.

    Args:
        date_str: Date string in YYYY-MM-DD format
        llm_recs: List of LLM recommendations (validated)
        ml_predictions: List of ML prediction dictionaries

    Returns:
        Path to saved file
    """
    Settings.DAILY_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Create combined signals (match LLM + ML)
    combined = []
    for ml_pred in ml_predictions:
        if ml_pred['status'] != 'SUCCESS':
            continue

        symbol = ml_pred['symbol']

        # Find matching LLM recommendation
        llm_rec = next((r for r in llm_recs if r.get('trading_symbol') == symbol), None)

        # Determine recommendation based on ML confidence only
        if ml_pred['direction'] == 'UP' and ml_pred['confidence'] >= 0.7:
            recommendation = 'STRONG_BUY'
        elif ml_pred['direction'] == 'DOWN' and ml_pred['confidence'] >= 0.7:
            recommendation = 'STRONG_SELL'
        else:
            recommendation = 'HOLD'

        combined.append({
            'symbol': symbol,
            'llm_action': llm_rec.get('action_to_take') if llm_rec else None,
            'llm_reason': llm_rec.get('reason_for_recommendation') if llm_rec else None,
            'ml_direction': ml_pred['direction'],
            'ml_confidence': ml_pred['confidence'],
            'recommendation': recommendation,
            'latest_price': ml_pred.get('latest_close')
        })

    # Create output structure
    output = {
        'metadata': {
            'date': date_str,
            'run_timestamp': datetime.now().isoformat(),
            'pipeline_version': '1.0.0',
            'total_news_articles': len(set([r.get('news_id') for r in llm_recs if r.get('news_id')])),
            'total_llm_recs': len(llm_recs),
            'total_validated': sum(1 for r in llm_recs if r.get('validated')),
            'total_ml_predictions': len([p for p in ml_predictions if p['status'] == 'SUCCESS']),
            'success_rate': len([p for p in ml_predictions if p['status'] == 'SUCCESS']) / len(ml_predictions) if ml_predictions else 0
        },
        'llm_recommendations': llm_recs,
        'ml_predictions': ml_predictions,
        'combined_signals': combined
    }

    # Save to file
    output_file = Settings.DAILY_RESULTS_DIR / f"{date_str}_predictions.json"

    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    logger.info(f"Saved daily results to {output_file}")
    logger.info(f"  LLM recommendations: {len(llm_recs)}")
    logger.info(f"  ML predictions: {len([p for p in ml_predictions if p['status'] == 'SUCCESS'])}")
    logger.info(f"  Combined signals: {len(combined)}")

    return output_file
