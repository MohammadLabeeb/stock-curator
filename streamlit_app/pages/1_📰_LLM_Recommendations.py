"""
LLM Recommendations Page - Display stocks extracted from news via Gemini LLM
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import load_daily_predictions, get_available_dates
from components.stock_cards import render_llm_recommendation_card

st.set_page_config(page_title="LLM Recommendations", page_icon="📰", layout="wide")

st.title("📰 LLM Stock Recommendations")
st.caption("Stocks extracted from financial news using Google Gemini 2.5 Flash")

# Date selector
available_dates = get_available_dates()
if not available_dates:
    st.error("⚠️ No data available. Run the pipeline at least once to generate predictions.")
    st.info("Run: `python -m src.pipeline.daily_pipeline`")
    st.stop()

selected_date = st.selectbox("📅 Select Date", available_dates, index=0)

# Load data
data = load_daily_predictions(selected_date)
if not data or 'llm_recommendations' not in data:
    st.error("❌ Failed to load LLM recommendations for this date")
    st.stop()

llm_recs = pd.DataFrame(data['llm_recommendations'])

if len(llm_recs) == 0:
    st.warning("No LLM recommendations found for this date")
    st.stop()

# Filters
st.markdown("### 🔍 Filters")
col1, col2 = st.columns(2)

with col1:
    actions = ['All'] + sorted(llm_recs['action_to_take'].unique().tolist())
    selected_action = st.selectbox("Action Type", actions)

with col2:
    # News type filter
    if 'news_type' in llm_recs.columns:
        news_types = ['All'] + sorted(llm_recs['news_type'].dropna().unique().tolist())
        selected_news_type = st.selectbox("News Type", news_types)
    else:
        selected_news_type = 'All'

# Apply filters
filtered = llm_recs.copy()
if selected_action != 'All':
    filtered = filtered[filtered['action_to_take'] == selected_action]
if selected_news_type != 'All':
    filtered = filtered[filtered['news_type'] == selected_news_type]

# Sort by confidence (descending)
if 'confidence' in filtered.columns:
    filtered = filtered.sort_values('confidence', ascending=False)

# Display recommendations
st.markdown("---")
st.markdown(f"### 📋 Recommendations ({len(filtered)} stocks)")

if len(filtered) == 0:
    st.info("No recommendations match the selected filters. Try adjusting the filters above.")
else:
    for _, rec in filtered.iterrows():
        render_llm_recommendation_card(rec.to_dict())

# Action distribution
st.markdown("---")
st.markdown("### 📊 Action Distribution")

action_counts = llm_recs['action_to_take'].value_counts()
col1, col2, col3, col4, col5 = st.columns(5)

cols = [col1, col2, col3, col4, col5]
for i, (action, count) in enumerate(action_counts.items()):
    if i < len(cols):
        action_emoji = {
            'BUY': '🟢', 'BUY_SIGNAL': '🟢',
            'SELL': '🔴', 'SELL_SIGNAL': '🔴',
            'HOLD': '🟡', 'WATCH': '⚪', 'IPO_WATCH': '🔵'
        }
        emoji = action_emoji.get(action, '⚪')
        cols[i].metric(f"{emoji} {action}", count)

# Download button
st.markdown("---")
st.markdown("### 💾 Export Data")

csv = filtered.to_csv(index=False)
st.download_button(
    label="📥 Download Filtered Results (CSV)",
    data=csv,
    file_name=f"llm_recommendations_{selected_date}.csv",
    mime="text/csv"
)

# Raw data viewer
with st.expander("🔍 View Raw Data"):
    st.dataframe(filtered, use_container_width=True)
