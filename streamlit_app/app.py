"""
Stock Curator - AI-Powered Stock Analysis Dashboard

Main entry point for the Streamlit application.
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Stock Curator",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .info-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">📈 Stock Curator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Stock Analysis using LLM + Machine Learning</div>', unsafe_allow_html=True)

# Introduction
st.markdown("---")

st.markdown("### 🎯 What is Stock Curator?")
st.markdown("""
Stock Curator is an **AI-powered stock analysis tool** that helps you discover investment opportunities by:

1. **📰 News Analysis** - Automatically collects financial news from Indian markets
2. **🤖 Smart Extraction** - Google Gemini AI identifies stock recommendations from news
3. **✅ Validation** - Verifies stock symbols against NSE master list (99% accuracy)
4. **📊 Price Prediction** - Machine learning forecasts 7-day price direction
5. **🔄 Daily Updates** - Fresh analysis every weekday at 8 AM IST
""")

# Navigation Guide
st.markdown("---")
st.markdown("### 🧭 Navigation")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 📰 LLM Recommendations")
    st.markdown("""
    View stocks extracted from financial news:
    - News-driven recommendations
    - Buy/Sell/Hold signals
    - Confidence scores
    - News sources & reasons
    """)

with col2:
    st.markdown("#### 🤖 ML Predictions")
    st.markdown("""
    Machine learning directional forecasts:
    - 7-day UP/DOWN predictions
    - Confidence scores
    - Latest stock prices
    - LLM recommendation comparison
    """)

with col3:
    st.markdown("#### 📊 Historical Analysis")
    st.markdown("""
    Track patterns over time:
    - Top recommended stocks
    - Daily stock recommendations
    - Historical trends
    """)

# How It Works
st.markdown("---")
st.markdown("### ⚙️ How It Works")

st.markdown("""
```
📅 Every Weekday at 8:00 AM IST
    ↓
📰 Scrape Financial News (World News API)
    ↓
🤖 Extract Recommendations (Google Gemini)
    ↓
✅ Validate Stock Symbols (99% success rate)
    ↓
📊 Fetch Market Data (Upstox API + NIFTY 50)
    ↓
🧮 Engineer 47 Features (Technical Indicators)
    ↓
🎯 Predict Direction (XGBoost Model)
    ↓
💾 Save Results (JSON format)
    ↓
📈 Update Dashboard (You're looking at it!)
```
""")

# Features
st.markdown("---")
st.markdown("### ✨ Key Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**🎨 Interactive Visualizations**")
    st.markdown("- Dynamic charts with Plotly")
    st.markdown("- Filterable tables")
    st.markdown("- Real-time data updates")

    st.markdown("")
    st.markdown("**🔍 Smart Filtering**")
    st.markdown("- By action type (BUY/SELL/WATCH)")
    st.markdown("- By confidence threshold")
    st.markdown("- By date range")

with col2:
    st.markdown("**🤝 Agreement Analysis**")
    st.markdown("- LLM vs ML comparison")
    st.markdown("- Conflict detection")
    st.markdown("- Recommendation synthesis")

    st.markdown("")
    st.markdown("**📈 Historical Tracking**")
    st.markdown("- Multi-day trends")
    st.markdown("- Top stocks analysis")
    st.markdown("- Performance metrics")

# Tech Stack
st.markdown("---")
st.markdown("### 🛠️ Technology Stack")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Data & APIs**")
    st.markdown("- World News API")
    st.markdown("- Google Gemini 2.5")
    st.markdown("- Upstox Market Data")

with col2:
    st.markdown("**ML & Processing**")
    st.markdown("- XGBoost Classifier")
    st.markdown("- Scikit-learn")
    st.markdown("- Pandas & NumPy")

with col3:
    st.markdown("**MLOps & Deployment**")
    st.markdown("- GitHub Actions")
    st.markdown("- Streamlit Cloud")
    st.markdown("- MLflow (Dagshub)")

# Getting Started
st.markdown("---")
st.markdown("### 🚀 Get Started")

st.info("""
**👈 Use the sidebar** to navigate between different pages:
- Start with **LLM Recommendations** to see what the news says
- Then check **ML Predictions** to see what the model thinks
- Finally explore **Historical Analysis** for trends over time
""")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p><strong>Stock Curator</strong> - AI-Powered Stock Analysis System</p>
    <p>Built with ❤️ using Streamlit | Data updated weekdays at 8:00 AM IST</p>
    <p style='font-size: 0.8rem;'>⚠️ Disclaimer: This is for educational purposes only. Not financial advice.</p>
</div>
""", unsafe_allow_html=True)
