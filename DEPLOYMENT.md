# Deployment Guide - Stock Curator

This guide covers deploying the Stock Curator MLOps system to production using GitHub Actions and Streamlit Cloud.

## Table of Contents
1. [GitHub Actions Setup](#github-actions-setup)
2. [Streamlit Cloud Deployment](#streamlit-cloud-deployment)
3. [Dagshub MLflow Setup](#dagshub-mlflow-setup)
4. [Troubleshooting](#troubleshooting)

---

## GitHub Actions Setup

The daily pipeline runs automatically at **8:00 AM IST on weekdays** (Monday-Friday) via GitHub Actions.

**Schedule:** Markets are closed on weekends, so the pipeline only runs Monday through Friday.

### 1. Configure GitHub Secrets

Navigate to your repository on GitHub:
```
Settings → Secrets and variables → Actions → New repository secret
```

Add the following secrets:

| Secret Name | Description | Required |
|------------|-------------|----------|
| `WORLD_NEWS_API_KEY` | API key from [WorldNewsAPI.com](https://worldnewsapi.com/) | ✅ Yes |
| `GEMINI_API_KEY` | API key from [Google AI Studio](https://ai.google.dev/) | ✅ Yes |
| `UPSTOX_ACCESS_TOKEN` | Access token from [Upstox Developer](https://upstox.com/developer/) | ✅ Yes |
| `DAGSHUB_USER` | Your Dagshub username | ⚪ Optional |
| `DAGSHUB_TOKEN` | Dagshub access token | ⚪ Optional |

### 2. Getting API Keys

#### World News API
1. Visit https://worldnewsapi.com/
2. Sign up for a free account
3. Navigate to Dashboard → API Keys
4. Copy your API key
5. Free tier: 100 requests/day

#### Google Gemini API
1. Visit https://ai.google.dev/
2. Click "Get API key in Google AI Studio"
3. Create a new API key
4. Copy the key
5. Free tier: 1,500 requests/day

#### Upstox API
1. Visit https://upstox.com/developer/
2. Create a developer account
3. Create a new app
4. Generate access token
5. Copy the access token
6. Note: Token may need periodic renewal

### 3. Enable GitHub Actions

The workflows are already configured in `.github/workflows/`. To enable:

1. Go to **Actions** tab in your GitHub repository
2. If prompted, click **"I understand my workflows, go ahead and enable them"**
3. You should see two workflows:
   - **Daily Stock Curation Pipeline** (runs at 8:00 AM IST on weekdays)
   - **CI - Tests and Linting** (runs on push/PR)

### 4. Manual Trigger (Testing)

To test the pipeline before waiting for the cron schedule:

1. Go to **Actions** tab
2. Select **"Daily Stock Curation Pipeline"**
3. Click **"Run workflow"** dropdown
4. Select branch (usually `main`)
5. Click **"Run workflow"**

The pipeline will execute and commit results back to the repository.

### 5. What the Pipeline Does

**Daily Pipeline** (`.github/workflows/daily_pipeline.yml`):
- ✅ Runs at 8:00 AM IST on weekdays (Mon-Fri)
- ✅ Skips weekends (markets closed Saturday-Sunday)
- ✅ Scrapes news from World News API
- ✅ Extracts recommendations via Gemini LLM
- ✅ Validates stocks against NSE master list
- ✅ Fetches NIFTY 50 data for market context
- ✅ Runs ML predictions on all validated stocks
- ✅ Commits results to `data/daily_results/{date}_predictions.json`
- ✅ Creates GitHub issue if pipeline fails
- ✅ Uploads artifacts for 90-day retention

**CI Pipeline** (`.github/workflows/ci.yml`):
- ✅ Lints code with `ruff`
- ✅ Runs all unit tests
- ✅ Validates module imports
- ✅ Uploads coverage to Codecov

### 6. Monitoring

**View Pipeline Runs:**
- Go to **Actions** tab
- Click on a specific run to see logs

**Check Results:**
- Results are committed to `data/daily_results/`
- Each day creates a new file: `YYYY-MM-DD_predictions.json`

**Failure Notifications:**
- Automatic GitHub issue created on failure
- Issue includes run link and debugging steps

---

## Streamlit Cloud Deployment

Deploy the interactive dashboard to Streamlit Cloud (100% free).

### 1. Prepare for Deployment

Ensure these files exist (they should already):
- ✅ `requirements.txt` (generated from `pyproject.toml`)
- ✅ `streamlit_app/app.py` (main dashboard file)
- ✅ `.streamlit/config.toml` (Streamlit configuration)

### 2. Deploy to Streamlit Cloud

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Add Streamlit dashboard"
   git push
   ```

2. **Visit Streamlit Cloud**
   - Go to https://share.streamlit.io
   - Sign in with GitHub

3. **Create New App**
   - Click **"New app"**
   - Select your repository: `stock-curator`
   - Set branch: `main`
   - Set main file path: `streamlit_app/app.py`
   - Click **"Deploy!"**

4. **Wait for Deployment**
   - Initial deployment takes 2-3 minutes
   - Streamlit will clone your repo and install dependencies

5. **Access Your Dashboard**
   - You'll get a URL like: `https://your-app-name.streamlit.app`
   - Dashboard auto-updates when you push to GitHub

### 3. How It Works

**Data Source:**
- Streamlit Cloud clones your GitHub repo
- Reads data directly from `data/daily_results/*.json`
- No API calls needed (data is local to the deployment)

**Auto-Updates:**
- When GitHub Actions commits new predictions
- Streamlit Cloud pulls the latest code
- Dashboard shows updated data within minutes

**Caching:**
- Data is cached for 1 hour (`@st.cache_data(ttl=3600)`)
- Reduces load times for users
- Automatically refreshes after cache expires

### 4. Dashboard Features

**Page 1: LLM Recommendations**
- View stocks extracted from news
- Filter by action type (BUY, SELL, WATCH, etc.)
- Filter by confidence threshold and news type
- See news sources and reasons
- Download filtered results as CSV
- Action distribution charts

**Page 2: ML Predictions**
- 7-day directional forecasts (UP/DOWN)
- Confidence levels and probabilities
- Compare with LLM recommendations
- See agreement/conflict indicators
- Filter by direction and LLM-ML agreement
- Probability distribution charts
- Download predictions as CSV

**Page 3: Historical Analysis**
- Daily recommendation/prediction count trends
- UP vs DOWN prediction trends over time
- Confidence trends (LLM vs ML)
- Top 10 most mentioned stocks
- LLM action distribution pie chart
- Stock-level LLM-ML agreement analysis
- Date range filtering
- Download historical data as CSV

---

## Dagshub MLflow Setup

(Optional) Track experiments and metrics in Dagshub.

### 1. Create Dagshub Account

1. Visit https://dagshub.com/signup
2. Sign up (free for public repos)
3. Free tier: 10GB storage

### 2. Create Repository

1. Click **"New Repository"**
2. Name: `stock-curator`
3. Enable **MLflow** in repository settings

### 3. Get Access Token

1. Go to Settings → Access Tokens
2. Click **"Create Token"**
3. Copy the token

### 4. Add to GitHub Secrets

Add these secrets to GitHub Actions:
- `DAGSHUB_USER`: Your Dagshub username
- `DAGSHUB_TOKEN`: The access token you just created

### 5. Verify Integration

The pipeline will automatically log metrics to Dagshub:
- Number of LLM recommendations
- Validation rate
- Number of ML predictions
- Average confidence

View them at:
```
https://dagshub.com/YOUR_USERNAME/stock-curator/experiments
```

---

## Troubleshooting

### GitHub Actions Failures

**Problem:** Pipeline fails with "Configuration validation failed"
- **Solution:** Check that all required secrets are set (WORLD_NEWS_API_KEY, GEMINI_API_KEY, UPSTOX_ACCESS_TOKEN)

**Problem:** "KeyError" or "Missing field"
- **Solution:** API response format may have changed. Check logs and update code if needed

**Problem:** "Rate limit exceeded"
- **Solution:**
  - World News API: 100 req/day (1 req/day used)
  - Gemini API: 1,500 req/day (1 req/day used)
  - Wait 24 hours for rate limit reset

**Problem:** Pipeline runs but doesn't commit
- **Solution:** Check that `contents: write` permission is set in workflow file

### Streamlit Deployment Issues

**Problem:** "Module not found"
- **Solution:** Ensure module is in `requirements.txt`. Run `uv pip compile pyproject.toml -o requirements.txt`

**Problem:** "File not found"
- **Solution:** Ensure `data/daily_results/` directory exists and is tracked in git

**Problem:** Dashboard shows no data
- **Solution:** Run the pipeline at least once to generate data files

### API Token Issues

**Problem:** Upstox token expired
- **Solution:** Upstox tokens may expire. Generate a new token from Upstox Developer Portal

**Problem:** Gemini API quota exceeded
- **Solution:** Free tier has daily limits. Wait 24 hours or upgrade plan

---

## Maintenance

### Weekly
- ✅ Check GitHub Actions runs (automated)
- ✅ Monitor failure notifications

### Monthly
- ⚪ Review API usage and quotas
- ⚪ Check Streamlit app performance
- ⚪ Review model accuracy metrics

### As Needed
- 🔄 Retrain model with new data
- 🔄 Update dependencies (`uv sync`)
- 🔄 Renew Upstox token if expired

---

## Support

**Issues:** https://github.com/YOUR_USERNAME/stock-curator/issues

**Documentation:**
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Streamlit Docs](https://docs.streamlit.io/)
- [Dagshub Docs](https://dagshub.com/docs/)

---

**Last Updated:** December 2025
**Version:** 1.0.0
