"""
Reusable UI components for displaying stock information.
"""

import streamlit as st
from typing import Dict


def render_llm_recommendation_card(rec: Dict):
    """
    Render a card for an LLM recommendation.

    Args:
        rec: Recommendation dictionary
    """
    # Action color mapping
    action_colors = {
        'BUY': '🟢',
        'BUY_SIGNAL': '🟢',
        'SELL': '🔴',
        'SELL_SIGNAL': '🔴',
        'HOLD': '🟡',
        'WATCH': '⚪',
        'IPO_WATCH': '🔵'
    }

    action_emoji = action_colors.get(rec['action_to_take'], '⚪')

    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            st.markdown(f"**{rec['equity_name']}** ({rec['trading_symbol']})")
            st.caption(rec['reason_for_recommendation'])

            if rec.get('news_url'):
                st.markdown(f"[📰 View Article]({rec['news_url']})", unsafe_allow_html=True)

        with col2:
            st.markdown(f"{action_emoji} **{rec['action_to_take']}**")
            if rec.get('news_type'):
                st.caption(f"Type: {rec['news_type']}")

        with col3:
            confidence_pct = rec['confidence'] * 100
            st.metric("Confidence", f"{confidence_pct:.0f}%")

        st.markdown("---")


def render_ml_prediction_card(pred: Dict, llm_action: str = None):
    """
    Render a card for an ML prediction.

    Args:
        pred: Prediction dictionary
        llm_action: Optional LLM action for comparison
    """
    direction_emoji = "📈" if pred['direction'] == 'UP' else "📉"
    direction_color = "green" if pred['direction'] == 'UP' else "red"

    with st.container():
        col1, col2, col3, col4 = st.columns([2, 1, 1, 2])

        with col1:
            st.markdown(f"**{pred['symbol']}**")
            if pred.get('latest_close'):
                st.caption(f"Latest: ₹{pred['latest_close']:,.2f}")

        with col2:
            st.markdown(f"{direction_emoji} **{pred['direction']}**")

        with col3:
            confidence_pct = pred['confidence'] * 100
            st.metric("Confidence", f"{confidence_pct:.1f}%")

        with col4:
            # Probability bar
            prob_up = pred['probability_up'] * 100
            prob_down = pred['probability_down'] * 100

            st.markdown(f"""
            <div style="background-color: #f0f2f6; border-radius: 4px; padding: 0.5rem;">
                <div style="font-size: 0.8rem; margin-bottom: 0.25rem;">
                    UP: {prob_up:.1f}% | DOWN: {prob_down:.1f}%
                </div>
                <div style="display: flex; height: 8px; border-radius: 4px; overflow: hidden;">
                    <div style="width: {prob_up}%; background-color: green;"></div>
                    <div style="width: {prob_down}%; background-color: red;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Show LLM comparison if provided
        if llm_action:
            agreement_emoji = "✅" if (
                (llm_action in ['BUY', 'BUY_SIGNAL'] and pred['direction'] == 'UP') or
                (llm_action in ['SELL', 'SELL_SIGNAL'] and pred['direction'] == 'DOWN')
            ) else "⚠️"

            st.caption(f"{agreement_emoji} LLM: {llm_action}")

        st.markdown("---")


def render_combined_signal_card(signal: Dict):
    """
    Render a card for combined LLM + ML signals.

    Args:
        signal: Combined signal dictionary
    """
    agreement_emoji = "✅" if signal['agreement'] else "⚠️"

    # Recommendation color
    rec_colors = {
        'STRONG_BUY': '🟢',
        'STRONG_SELL': '🔴',
        'HOLD': '🟡'
    }
    rec_emoji = rec_colors.get(signal['recommendation'], '⚪')

    with st.container():
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

        with col1:
            st.markdown(f"**{signal['symbol']}**")
            if signal.get('latest_price'):
                st.caption(f"₹{signal['latest_price']:,.2f}")

        with col2:
            st.markdown(f"LLM: **{signal.get('llm_action', 'N/A')}**")

        with col3:
            ml_conf = signal.get('ml_confidence', 0) * 100
            st.markdown(f"ML: **{signal['ml_direction']}** ({ml_conf:.0f}%)")

        with col4:
            st.markdown(f"{agreement_emoji} {rec_emoji} **{signal['recommendation']}**")

        if signal.get('llm_reason'):
            with st.expander("📝 Details"):
                st.markdown(f"**Reason:** {signal['llm_reason']}")

        st.markdown("---")


def render_metrics_row(label: str, value: str, delta: str = None):
    """
    Render a metrics row.

    Args:
        label: Metric label
        value: Metric value
        delta: Optional delta value
    """
    st.metric(label=label, value=value, delta=delta)
