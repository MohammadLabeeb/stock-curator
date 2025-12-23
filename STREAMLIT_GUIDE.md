# Streamlit Dashboard Guide

## Overview

The Stock Curator dashboard provides an interactive interface to visualize LLM recommendations and ML predictions. The dashboard automatically updates when new predictions are committed to the repository.

## Running Locally

### Prerequisites

```bash
# Install dependencies
uv sync

# OR using pip
pip install -r requirements.txt
```

### Start the Dashboard

```bash
# Using UV (recommended)
.venv/bin/streamlit run streamlit_app/app.py

# OR if streamlit is in PATH
streamlit run streamlit_app/app.py
```

The dashboard will open in your browser at `http://localhost:8501`

## Dashboard Pages

### Home Page (app.py)

**What You'll See:**
- Project overview and description
- Model performance metrics (70.08% accuracy, 73.10% precision)
- Navigation guide to all pages
- System architecture flowchart
- Technology stack information

**Key Features:**
- Quick metrics at a glance
- Links to all dashboard pages in sidebar
- Educational content about the system

---

### Page 1: 📰 LLM Recommendations

**Purpose:** View stocks extracted from financial news by Google Gemini LLM

**Filters:**
- **Date Selector:** Choose which day's recommendations to view
- **Action Type:** Filter by BUY, SELL, HOLD, WATCH, IPO_WATCH, etc.
- **Min Confidence:** Slider to filter recommendations above a confidence threshold (0-100%)
- **News Type:** Filter by news category (earnings, contracts, IPO, etc.)

**What You'll See:**
- Total recommendations count
- Filtered results count
- Average confidence score
- Validation rate (how many stocks were successfully validated)
- Action distribution across BUY/SELL/HOLD/WATCH
- Detailed card for each recommendation showing:
  - Company name and trading symbol
  - Action to take (with color-coded emoji)
  - Confidence percentage
  - Reason for recommendation
  - Link to source news article (if available)
  - News type

**Actions:**
- Click "Download Filtered Results (CSV)" to export data
- Expand "View Raw Data" to see the full DataFrame

**Use Cases:**
- Find high-confidence BUY signals from news
- Identify stocks with negative news (SELL signals)
- Track IPO launches and watches
- Verify LLM extraction quality

---

### Page 2: 🤖 ML Predictions

**Purpose:** View 7-day directional forecasts from the XGBoost model

**Filters:**
- **Date Selector:** Choose which day's predictions to view
- **Direction:** Filter by UP, DOWN, or All
- **Min Confidence:** Slider to filter predictions above a confidence threshold (60-100%)
- **LLM-ML Agreement:** Filter by:
  - All predictions
  - Agree (LLM BUY + ML UP, or LLM SELL + ML DOWN)
  - Disagree (conflicting signals)
  - No LLM Data (ML-only predictions)

**What You'll See:**
- Total predictions count
- Number of UP predictions (📈)
- Number of DOWN predictions (📉)
- Average ML confidence
- LLM-ML agreement metrics:
  - Number of agreements ✅
  - Number of disagreements ⚠️
  - Stocks with no LLM data ⚪
  - Overall agreement rate
- Probability distribution histogram (UP vs DOWN)
- Detailed card for each prediction showing:
  - Stock symbol
  - Latest closing price
  - Direction (UP/DOWN with emoji)
  - Confidence percentage
  - Probability bar chart (UP vs DOWN probabilities)
  - LLM action (if available) with agreement indicator

**Actions:**
- Click "Download Filtered Predictions (CSV)" to export data
- Expand "View Raw Data" to see the full DataFrame

**Use Cases:**
- Find high-confidence ML predictions
- Identify stocks where LLM and ML agree (stronger signals)
- Spot conflicts between news sentiment and technical indicators
- Filter for specific directional forecasts (only UP or only DOWN)

---

### Page 3: 📊 Historical Analysis

**Purpose:** Analyze trends and patterns across multiple days

**Filters:**
- **Start Date:** Select the beginning of the date range
- **End Date:** Select the end of the date range

**What You'll See:**

**Summary Metrics:**
- Total LLM recommendations across all days
- Total ML predictions across all days
- Average validation rate
- Number of days analyzed

**Charts:**

1. **Daily Recommendation & Prediction Counts** (Line Chart)
   - Tracks how many LLM recommendations and ML predictions were made each day
   - Useful for: Identifying high-activity days, spotting trends in market coverage

2. **ML Predictions: UP vs DOWN by Date** (Stacked Bar Chart)
   - Shows the proportion of UP vs DOWN predictions each day
   - Useful for: Understanding overall market sentiment, spotting bullish/bearish periods

3. **Confidence Trends Over Time** (Line Chart)
   - Plots average ML confidence and LLM confidence over time
   - Useful for: Identifying if model confidence is improving, spotting uncertainty periods

4. **Top 10 Most Mentioned Stocks** (Horizontal Bar Chart)
   - Ranks stocks by how often they appear in LLM recommendations
   - Useful for: Finding frequently discussed stocks, identifying market focus areas

5. **LLM Action Distribution** (Pie Chart)
   - Shows breakdown of BUY/SELL/HOLD/WATCH actions
   - Useful for: Understanding overall recommendation sentiment

6. **Top 15 Stocks: LLM-ML Agreement Rate** (Bar Chart with Colors)
   - For stocks that appear in both LLM and ML predictions
   - Shows agreement rate (0-100%) with green=high agreement, red=low agreement
   - Displays number of comparisons (n=X) above each bar
   - Useful for: Finding stocks with consistent signals, identifying controversial stocks

**Agreement Summary:**
- Total comparisons (stocks appearing in both LLM and ML)
- Number of agreements
- Overall agreement rate

**Actions:**
- Click "Download Trend Data (CSV)" to export time-series data
- Click "Download Agreement Data (CSV)" to export LLM-ML agreement analysis
- Expand "View Trend Data" to see the raw DataFrame

**Use Cases:**
- Track system performance over weeks/months
- Identify most frequently recommended stocks
- Analyze agreement patterns between LLM and ML
- Spot trends in market coverage and sentiment
- Create reports for specific time periods

---

## Data Sources

The dashboard reads data from:
```
data/daily_results/YYYY-MM-DD_predictions.json
```

Each JSON file contains:
- **metadata**: Run timestamp, counts, etc.
- **llm_recommendations**: Array of LLM-extracted stocks
- **ml_predictions**: Array of ML directional forecasts
- **combined_signals**: Merged LLM+ML analysis

## Caching

The dashboard uses `@st.cache_data(ttl=3600)` to cache data for 1 hour:
- Reduces file I/O on repeated page loads
- Automatically refreshes after 1 hour
- To force refresh: Use browser's refresh button or restart Streamlit

## Deployment to Streamlit Cloud

### Step 1: Push to GitHub

Ensure all code is committed:
```bash
git add .
git commit -m "Add Streamlit dashboard"
git push
```

### Step 2: Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Click "New app"
4. Select your repository: `stock-curator`
5. Set branch: `main` (or `dev`)
6. Set main file path: `streamlit_app/app.py`
7. Click "Deploy!"

### Step 3: Wait for Deployment

- Initial deployment takes 2-3 minutes
- Streamlit will:
  - Clone your repository
  - Install dependencies from `requirements.txt`
  - Start the app
  - Provide a public URL (e.g., `https://stock-curator.streamlit.app`)

### Step 4: Auto-Updates

Once deployed, the dashboard will automatically update when:
- GitHub Actions commits new predictions to `data/daily_results/`
- You push code changes to GitHub

Streamlit Cloud pulls updates every few minutes.

## Troubleshooting

### Dashboard shows "No data available"

**Cause:** No prediction files in `data/daily_results/`

**Solution:**
```bash
# Run the pipeline to generate data
python -m src.pipeline.daily_pipeline

# Or trigger GitHub Actions workflow manually
```

### Dashboard shows old data

**Cause:** Streamlit cache hasn't expired

**Solution:**
- Wait 1 hour for automatic cache refresh
- Restart Streamlit: Press `Ctrl+C` and re-run
- Clear cache: Press `C` in the Streamlit terminal

### Module import errors

**Cause:** Dependencies not installed

**Solution:**
```bash
# Reinstall dependencies
uv sync

# Or
pip install -r requirements.txt
```

### Port already in use

**Cause:** Another Streamlit instance is running

**Solution:**
```bash
# Kill existing Streamlit processes
pkill -f streamlit

# Or run on different port
streamlit run streamlit_app/app.py --server.port 8502
```

## Testing Components

To test dashboard components without running the full app:

```bash
.venv/bin/python test_streamlit_components.py
```

This will verify:
- ✅ Data loader functions work
- ✅ UI components import successfully
- ✅ All page files have valid syntax

## Customization

### Changing Theme Colors

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#1f77b4"        # Accent color
backgroundColor = "#ffffff"      # Main background
secondaryBackgroundColor = "#f0f2f6"  # Sidebar, boxes
textColor = "#262730"           # Text color
```

### Changing Cache Duration

Edit `streamlit_app/utils/data_loader.py`:

```python
@st.cache_data(ttl=3600)  # Change 3600 to desired seconds
def load_daily_predictions(date_str: str):
    ...
```

### Adding New Filters

Example: Add sector filter to Page 1

1. Load sector data in your JSON
2. Add filter widget:
   ```python
   sectors = ['All'] + sorted(llm_recs['sector'].unique().tolist())
   selected_sector = st.selectbox("Sector", sectors)
   ```
3. Apply filter:
   ```python
   if selected_sector != 'All':
       filtered = filtered[filtered['sector'] == selected_sector]
   ```

## Performance Tips

**For Large Datasets:**
- Use pagination for long lists
- Reduce chart data points
- Increase cache TTL to reduce recomputation

**For Faster Loading:**
- Enable `use_container_width=True` for charts
- Use `st.dataframe()` instead of `st.table()` for large tables
- Lazy-load expensive computations

## Security Notes

**Public Deployment:**
- Dashboard is read-only (no user input to backend)
- No API keys or secrets in frontend code
- All data is pre-computed and stored in JSON

**Private Deployment:**
- Use Streamlit Cloud's "Share with specific people" feature
- Set repository to private on GitHub
- Add authentication via Streamlit's built-in auth (Enterprise plan)

## Support

**Issues:** https://github.com/YOUR_USERNAME/stock-curator/issues

**Streamlit Docs:** https://docs.streamlit.io/

---

**Last Updated:** December 2025
**Dashboard Version:** 1.0.0
