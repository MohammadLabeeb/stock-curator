"""
Historical Analysis Page - Trends and insights over time
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import load_all_predictions

st.set_page_config(page_title="Historical Analysis", page_icon="📊", layout="wide")

st.title("📊 Historical Analysis")
st.caption("Track stock recommendations and patterns over time")

# Load all historical data
all_data = load_all_predictions()

if not all_data:
    st.error("⚠️ No historical data available. Run the pipeline multiple times to see trends.")
    st.info("Run: `python -m src.pipeline.daily_pipeline`")
    st.stop()

# Date range selector
st.markdown("### 📅 Date Range")
all_dates = sorted(all_data.keys())
col1, col2 = st.columns(2)

with col1:
    start_date = st.selectbox("Start Date", all_dates, index=0)

with col2:
    end_date = st.selectbox("End Date", all_dates, index=len(all_dates) - 1)

# Filter data by date range
filtered_data = {k: v for k, v in all_data.items() if start_date <= k <= end_date}

if len(filtered_data) == 0:
    st.warning("No data in selected date range")
    st.stop()

# Top recommended stocks
st.markdown("---")
st.markdown("### 🏆 Top Recommended Stocks")

# Aggregate all LLM recommendations
all_llm_symbols = []

for data in filtered_data.values():
    llm_recs = data.get('llm_recommendations', [])
    for rec in llm_recs:
        all_llm_symbols.append(rec.get('trading_symbol', 'Unknown'))

if len(all_llm_symbols) > 0:
    # Top 10 most recommended stocks
    top_stocks = pd.Series(all_llm_symbols).value_counts().head(10)

    fig = go.Figure(go.Bar(
        x=top_stocks.values,
        y=top_stocks.index,
        orientation='h',
        marker_color='lightblue',
        text=top_stocks.values,
        textposition='outside'
    ))

    fig.update_layout(
        title='Top 10 Most Recommended Stocks',
        xaxis_title='Number of Recommendations',
        yaxis_title='Stock Symbol',
        height=400,
        yaxis={'categoryorder':'total ascending'}
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No LLM recommendations found in selected date range")

# Daily stock recommendations (new section)
st.markdown("---")
st.markdown("### 📅 Daily Stock Recommendations")

# Create data for daily recommendations
daily_stocks_data = []

for date in sorted(filtered_data.keys()):
    data = filtered_data[date]
    llm_recs = data.get('llm_recommendations', [])
    
    for rec in llm_recs:
        daily_stocks_data.append({
            'Date': date,
            'Stock': rec.get('trading_symbol', 'Unknown'),
            'Action': rec.get('action_to_take', 'Unknown'),
            'Confidence': rec.get('confidence', 0)
        })

if len(daily_stocks_data) > 0:
    daily_df = pd.DataFrame(daily_stocks_data)
    
    # Option to choose visualization type
    viz_type = st.radio("Visualization Type", ['Table', 'Heatmap'], horizontal=True)
    
    if viz_type == 'Table':
        # Show as a searchable table
        st.markdown("**All Recommendations** (searchable)")
        
        # Add filters
        col1, col2 = st.columns(2)
        with col1:
            # Filter out None values and sort
            stock_options = [s for s in daily_df['Stock'].unique() if s is not None]
            selected_stock = st.multiselect(
                "Filter by Stock",
                options=sorted(stock_options),
                default=[]
            )
        with col2:
            # Filter out None values and sort
            action_options = [a for a in daily_df['Action'].unique() if a is not None]
            selected_action = st.multiselect(
                "Filter by Action",
                options=sorted(action_options),
                default=[]
            )
        
        # Apply filters
        display_df = daily_df.copy()
        if selected_stock:
            display_df = display_df[display_df['Stock'].isin(selected_stock)]
        if selected_action:
            display_df = display_df[display_df['Action'].isin(selected_action)]
        
        # Sort by date (descending) and confidence (descending)
        display_df = display_df.sort_values(['Date', 'Confidence'], ascending=[False, False])
        
        # Display table
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Date": st.column_config.DateColumn("Date"),
                "Stock": st.column_config.TextColumn("Stock Symbol"),
                "Action": st.column_config.TextColumn("Action"),
                "Confidence": st.column_config.ProgressColumn(
                    "Confidence",
                    format="%.1f",
                    min_value=0,
                    max_value=1,
                )
            }
        )
        
        # Download button for filtered data
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Table (CSV)",
            data=csv,
            file_name=f"daily_stocks_{start_date}_to_{end_date}.csv",
            mime="text/csv"
        )
        
    else:  # Heatmap
        # Create a pivot table: Date x Stock
        # Count recommendations per stock per day
        pivot_data = daily_df.groupby(['Date', 'Stock']).size().reset_index(name='Count')
        pivot = pivot_data.pivot(index='Stock', columns='Date', values='Count').fillna(0)
        
        # Only show stocks with at least 2 mentions for cleaner viz
        stock_counts = pivot.sum(axis=1)
        pivot_filtered = pivot[stock_counts >= 1].sort_values(by=pivot.columns.tolist(), ascending=False)
        
        # Limit to top 15 stocks for readability
        pivot_filtered = pivot_filtered.head(15)
        
        if len(pivot_filtered) > 0:
            fig = go.Figure(data=go.Heatmap(
                z=pivot_filtered.values,
                x=pivot_filtered.columns,
                y=pivot_filtered.index,
                colorscale='Blues',
                text=pivot_filtered.values,
                texttemplate='%{text}',
                textfont={"size": 10},
                colorbar=dict(title="Count")
            ))
            
            fig.update_layout(
                title='Stock Recommendations Heatmap (Top 15 Stocks)',
                xaxis_title='Date',
                yaxis_title='Stock Symbol',
                height=500,
                xaxis={'side': 'bottom'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Darker color = more recommendations on that date")
        else:
            st.info("Not enough data for heatmap visualization. Try the Table view.")

else:
    st.info("No stock recommendations found in selected date range")

# Summary stats
st.markdown("---")
st.markdown("### 📊 Summary Statistics")

col1, col2, col3 = st.columns(3)

with col1:
    total_recs = len(daily_stocks_data)
    st.metric("Total Recommendations", total_recs)

with col2:
    unique_stocks = len(set(all_llm_symbols))
    st.metric("Unique Stocks", unique_stocks)

with col3:
    days_analyzed = len(filtered_data)
    st.metric("Days Analyzed", days_analyzed)
