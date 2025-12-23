"""
ML Predictions Page - Display 7-day directional forecasts from XGBoost model
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import load_daily_predictions, get_available_dates
from components.stock_cards import render_ml_prediction_card
from components.charts import create_candlestick_chart, create_line_chart_with_volume

st.set_page_config(page_title="ML Predictions", page_icon="🤖", layout="wide")

st.title("🤖 ML Predictions (7-Day Direction)")
st.caption("XGBoost Classifier predicting stock price direction for the next 7 days")

# Date selector
available_dates = get_available_dates()
if not available_dates:
    st.error("⚠️ No data available. Run the pipeline at least once to generate predictions.")
    st.info("Run: `python -m src.pipeline.daily_pipeline`")
    st.stop()

selected_date = st.selectbox("📅 Select Date", available_dates, index=0)

# Load data
data = load_daily_predictions(selected_date)
if not data or 'ml_predictions' not in data:
    st.error("❌ Failed to load ML predictions for this date")
    st.stop()

ml_preds = pd.DataFrame(data['ml_predictions'])
llm_recs = pd.DataFrame(data.get('llm_recommendations', []))

if len(ml_preds) == 0:
    st.warning("No ML predictions found for this date")
    st.stop()

# Create LLM action lookup
llm_action_map = {}
if len(llm_recs) > 0:
    for _, rec in llm_recs.iterrows():
        llm_action_map[rec['trading_symbol']] = rec['action_to_take']

# Add LLM action to ML predictions
ml_preds['llm_action'] = ml_preds['symbol'].map(llm_action_map)

# Filters
st.markdown("### 🔍 Filters")
col1, col2 = st.columns(2)

with col1:
    direction_filter = st.selectbox("Direction", ['All', 'UP', 'DOWN'])

with col2:
    min_conf = st.slider("Minimum Confidence", 0.0, 1.0, 0.5, 0.05)

# Apply filters
filtered = ml_preds.copy()

if direction_filter != 'All':
    filtered = filtered[filtered['direction'] == direction_filter]

filtered = filtered[filtered['confidence'] >= min_conf]

# Sort by confidence
filtered = filtered.sort_values('confidence', ascending=False)

# Display metrics
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📊 Total Predictions", len(ml_preds))

with col2:
    up_count = len(ml_preds[ml_preds['direction'] == 'UP'])
    st.metric("📈 UP Predictions", up_count)

with col3:
    down_count = len(ml_preds[ml_preds['direction'] == 'DOWN'])
    st.metric("📉 DOWN Predictions", down_count)

with col4:
    avg_conf = ml_preds['confidence'].mean()
    st.metric("📈 Avg Confidence", f"{avg_conf:.1%}")

# Display predictions
st.markdown("---")
st.markdown(f"### 📋 Predictions ({len(filtered)} stocks)")

if len(filtered) == 0:
    st.info("No predictions match the selected filters. Try adjusting the filters above.")
else:
    for _, pred in filtered.iterrows():
        llm_action = pred['llm_action'] if pd.notna(pred['llm_action']) else None
        render_ml_prediction_card(pred.to_dict(), llm_action)

        # Add chart if historical data available
        if pred.get('historical_data'):
            with st.expander(f"📊 View {pred['symbol']} Price Chart (Last 60 Days)"):
                chart_type = st.radio(
                    "Chart Type",
                    ["Candlestick", "Line + Volume"],
                    horizontal=True,
                    key=f"chart_{pred['symbol']}"
                )

                if chart_type == "Candlestick":
                    fig = create_candlestick_chart(
                        pred['historical_data'],
                        pred['symbol'],
                        pred['direction'],
                        pred['confidence']
                    )
                else:
                    fig = create_line_chart_with_volume(
                        pred['historical_data'],
                        pred['symbol'],
                        pred['direction'],
                        pred['confidence']
                    )

                if fig:
                    st.plotly_chart(fig, use_container_width=True)

                    # Add stats
                    hist_df = pd.DataFrame.from_dict(pred['historical_data'], orient='index')
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("60-Day High", f"₹{hist_df['High'].max():.2f}")
                    with col2:
                        st.metric("60-Day Low", f"₹{hist_df['Low'].min():.2f}")
                    with col3:
                        price_change = ((hist_df['Close'].iloc[-1] - hist_df['Close'].iloc[0]) / hist_df['Close'].iloc[0]) * 100
                        st.metric("60-Day Change", f"{price_change:+.2f}%")
                    with col4:
                        avg_volume = hist_df['Volume'].mean()
                        st.metric("Avg Volume", f"{avg_volume:,.0f}")

        st.markdown("---")

# Model Performance
st.markdown("---")
st.markdown("### 📊 Model Performance")

metric_col1, metric_col2, metric_col3 = st.columns(3)

with metric_col1:
    st.metric(
        label="Accuracy",
        value="70.08%",
        help="Percentage of correct directional predictions"
    )

with metric_col2:
    st.metric(
        label="Precision",
        value="73.10%",
        help="Accuracy of positive (UP) predictions"
    )

with metric_col3:
    st.metric(
        label="Win Rate",
        value="70.81%",
        help="Overall success rate in backtesting"
    )

st.info("**Model Details:** 47 Technical Features | 60-Day Window | 7-Day Prediction Horizon")

# Download button
st.markdown("---")
st.markdown("### 💾 Export Data")

csv = filtered.to_csv(index=False)
st.download_button(
    label="📥 Download Filtered Predictions (CSV)",
    data=csv,
    file_name=f"ml_predictions_{selected_date}.csv",
    mime="text/csv"
)

# Raw data viewer
with st.expander("🔍 View Raw Data"):
    st.dataframe(filtered, use_container_width=True)
