# 📈 Stock Curator

> **AI-Powered Stock Analysis using LLM + Machine Learning**
> Combining LLM-based news intelligence with ML predictions for the Indian stock market (NIFTY)

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![ML](https://img.shields.io/badge/ML-XGBoost-orange.svg)](https://xgboost.ai/)
[![LLM](https://img.shields.io/badge/LLM-Gemini-green.svg)](https://ai.google.dev/)
[![Dashboard](https://img.shields.io/badge/Dashboard-Streamlit-red.svg)](https://streamlit.io/)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-yellow.svg)](https://github.com/features/actions)

---

## 🎯 Project Overview

**Stock Curator** is an AI-powered stock analysis tool that helps you discover investment opportunities by combining:
1. **GenAI-powered news extraction** using Google Gemini to identify stock recommendations from financial news
2. **ML-based directional forecasting** using XGBoost to predict 7-day price movements
3. **Automated daily pipeline** via GitHub Actions that runs before market open
4. **Interactive dashboard** deployed on Streamlit Cloud for real-time insights

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DAILY PIPELINE (GitHub Actions)                 │
│                            Runs at 8:00 AM IST                          │
└────────────┬────────────────────────────────────────────────────────────┘
             │
             ├──► 1. News Scraping (WorldNewsAPI)
             │    └─► Indian financial news from last 24 hours
             │
             ├──► 2. LLM Extraction (Google Gemini)
             │    └─► Extract stock recommendations, IPOs, earnings
             │
             ├──► 3. Stock Validation (NSE/BSE Master)
             │    └─► Verify symbols, get ISINs, filter IPOs
             │
             ├──► 4. Feature Engineering (47 indicators)
             │    ├─► Basic: SMA, EMA, RSI, MACD, Bollinger Bands
             │    ├─► Advanced: Hurst Exponent, OBV, Market Regime
             │    └─► Market Context: NIFTY 50 correlation
             │
             ├──► 5. ML Prediction (XGBoost)
             │    └─► 7-day directional forecast (UP/DOWN)
             │
             └──► 6. Results Storage (JSON)
                  └─► Commit to data/daily_results/
                       │
                       └──► Triggers Streamlit Cloud Auto-Deploy
                            │
                            └──► Dashboard Updates Within Minutes
```

---

## ✨ Key Features

### 🤖 **AI/ML Components**

| Component | Technology | Purpose | Performance |
|-----------|-----------|---------|-------------|
| **News Analysis** | Google Gemini 2.5 Flash | Extract stock recommendations from news | 99% validation rate |
| **Price Prediction** | XGBoost Classifier | Predict 7-day direction (UP/DOWN) | 70.08% accuracy |
| **Feature Engineering** | Custom Pipeline | 47 technical indicators (60-day window) | 15 advanced features |
| **Stock Validation** | NSE/BSE Master | Verify symbols, handle IPOs | 2,252 symbols |

### 🔄 **MLOps Pipeline**

- ✅ **Automated Daily Runs**: GitHub Actions cron job (8:00 AM IST, Mon-Fri)
- ✅ **Version Control**: Git-based model and data versioning
- ✅ **Continuous Deployment**: Streamlit Cloud auto-deploys on push
- ✅ **Experiment Tracking**: MLflow integration via Dagshub (optional)
- ✅ **Error Handling**: Automatic GitHub issue creation on failures
- ✅ **Monitoring**: Pipeline logs, prediction success rates

### 📊 **Interactive Dashboard**

- **Page 1: LLM Recommendations** - News-driven stock insights with filtering
- **Page 2: ML Predictions** - Directional forecasts with confidence scores and historical charts
- **Page 3: Historical Analysis** - Trends, top stocks, and pattern analysis

---

## 🛠️ Tech Stack

### **Machine Learning**
- **Framework**: XGBoost (scikit-learn compatible)
- **Feature Engineering**: Pandas, NumPy, TA-Lib patterns
- **Model**: Binary classifier (420KB), StandardScaler (1.6KB)
- **Training Data**: 2+ years of NSE/BSE historical data

### **Large Language Model**
- **Model**: Google Gemini 2.5 Flash
- **Task**: Named Entity Recognition + Sentiment Analysis
- **Input**: Financial news articles (Indian markets)
- **Output**: Structured stock recommendations (JSON)

### **Data Pipeline**
- **News Source**: WorldNewsAPI (100 req/day free tier)
- **Market Data**: Upstox API (historical OHLCV data)
- **Index Data**: NIFTY 50 for market context features
- **Storage**: Local JSON (5.7MB total, git-tracked)

### **Infrastructure**
- **Orchestration**: GitHub Actions (cron schedule)
- **Dashboard**: Streamlit Cloud (free hosting)
- **Package Management**: UV (10-100x faster than pip)
- **CI/CD**: Automated tests with Ruff linting
- **Deployment**: Zero-cost serverless architecture

---

## 🚀 Getting Started

### **Prerequisites**
- Python 3.10+
- Git
- API Keys (see [Setup Guide](#-api-keys-setup))

### **Installation**

```bash
# 1. Clone the repository
git clone https://github.com/MohammadLabeeb/stock-curator.git
cd stock-curator

# 2. Install dependencies (using UV - recommended)
pip install uv
uv sync

# OR using pip
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# 4. Run the pipeline locally
python -m src.pipeline.daily_pipeline

# 5. Launch the dashboard
streamlit run streamlit_app/app.py
```

### **🔑 API Keys Setup**

1. **World News API** (required)
   - Sign up: https://worldnewsapi.com/
   - Add to `.env`: `WORLD_NEWS_API_KEY=your_key_here`

2. **Google Gemini API** (required)
   - Get key: https://ai.google.dev/
   - Add to `.env`: `GEMINI_API_KEY=your_key_here`

3. **Upstox API** (required)
   - Developer portal: https://upstox.com/developer/
   - Generate access token
   - Add to `.env`: `UPSTOX_ACCESS_TOKEN=your_token_here`

---

## 📂 Project Structure

```
stock-curator/
├── src/                           # Source code
│   ├── config/                    # Settings, constants
│   ├── data/                      # Data fetching, validation
│   ├── features/                  # Feature engineering (47 indicators)
│   ├── llm/                       # Gemini integration, prompts
│   ├── models/                    # ML prediction, loading
│   └── pipeline/                  # Daily orchestration
│
├── streamlit_app/                 # Dashboard
│   ├── pages/                     # Multi-page app
│   │   ├── 1_📰_LLM_Recommendations.py
│   │   ├── 2_🤖_ML_Predictions.py
│   │   └── 3_📊_Historical_Analysis.py
│   ├── components/                # Reusable UI elements
│   └── utils/                     # Data loading, helpers
│
├── data/                          # Data storage
│   ├── models/                    # Trained ML models (git-tracked)
│   ├── daily_results/             # Pipeline outputs (git-tracked)
│   └── processed/                 # Stock master data (git-tracked)
│
├── .github/workflows/             # CI/CD automation
│   ├── daily_pipeline.yml         # Runs at 8 AM IST (Mon-Fri)
│   └── ci.yml                     # Tests & linting on PR
│
├── tests/                         # Unit tests
├── archive/
│   └── notebooks_backup/          # Research & development notebooks
│
├── pyproject.toml                 # Dependencies (UV format)
├── requirements.txt               # Pip-compatible requirements
└── README.md                      # You are here!
```

---

## 🔬 Technical Deep Dive

### **Feature Engineering Pipeline**

**47 Technical Indicators** computed from 60-day historical windows:

**Basic Indicators (32 features)**
- Moving Averages: SMA (5, 10, 20, 50), EMA (12, 26)
- Momentum: RSI (14), MACD, Momentum (10d, 20d)
- Volatility: Bollinger Bands (20, 2σ), ATR (14)
- Volume: Volume SMA, Volume Ratio, OBV
- Returns: Daily, 3d, 5d, 10d, Log Returns

**Advanced Indicators (15 features)**
- Market Context: NIFTY 50 correlation, relative strength, market regime
- Mean Reversion: RSI divergence, BB squeeze
- Trend Strength: MACD crossover, momentum strength
- Liquidity: Volume-price trend, volume breakouts
- Statistical: Returns skewness/kurtosis, Hurst exponent

### **LLM Extraction Pipeline**

**Prompt Engineering Strategy**:
1. **Context Setting**: Financial analyst expert in NSE/BSE markets
2. **Extraction Rules**: 7 categories (recommendations, IPOs, earnings, etc.)
3. **Action Mapping**: BUY/SELL/HOLD/WATCH/IPO_WATCH
4. **Deduplication**: Merge similar signals, split conflicting ones
5. **Output Format**: Structured JSON with confidence scores

**Validation Strategy**:
- Cross-reference with NSE/BSE master list (2,252 trading symbols)
- ISIN lookup for trading symbol verification
- IPO detection and flagging
- Equity vs derivative filtering

---

## 🎓 Learning Outcomes

This project demonstrates:

### **Machine Learning**
- [x] Binary classification
- [x] Feature engineering for time-series
- [x] Model evaluation and backtesting
- [x] Hyperparameter tuning
- [x] Model persistence and versioning

### **GenAI/LLMs**
- [x] Prompt engineering for financial NER
- [x] Structured output generation (JSON)
- [x] LLM API integration (Google Gemini)
- [x] Handling unstructured text data

### **MLOps**
- [x] Automated ML pipelines (GitHub Actions)
- [x] Model deployment
- [x] Continuous deployment (Streamlit Cloud)
- [x] Data versioning strategies

### **Software Engineering**
- [x] Production-ready Python code architecture
- [x] Error handling and logging
- [x] Unit testing and CI/CD
- [x] Documentation and type hints

### **Data Engineering**
- [x] ETL pipelines (Extract-Transform-Load)
- [x] Data validation and cleaning
- [x] Time-series data handling
- [x] Efficient data storage (JSON)

---

## 📊 Dashboard Screenshots

### Page 1: LLM Recommendations
> View stocks extracted from financial news with filtering by action, confidence, and news type.

### Page 2: ML Predictions
> 7-day directional forecasts with interactive candlestick and line+volume charts showing 60 days of historical data.

### Page 3: Historical Analysis
> Track trends over time, top recommended stocks, and daily performance metrics.

---

---

## 🤝 Contributing

This is a portfolio project, but suggestions and feedback are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

**Live Dashboard**: [Streamlit URL]

---

<div align="center">

**Built with ❤️ for the Indian Stock Market**

[⬆ Back to Top](#-stock-curator)

</div>
