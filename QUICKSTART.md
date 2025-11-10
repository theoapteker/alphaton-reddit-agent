# 🚀 Quick Start Guide

Get your Reddit sentiment alpha strategy up and running in 5 steps!

## What This Project Does

This project:
1. **Scrapes Reddit** (r/wallstreetbets) for stock mentions
2. **Analyzes sentiment** using natural language processing
3. **Converts to FINTER format** (tickers → gvkeyiid)
4. **Generates alpha signals** that can be backtested on FINTER

The result: A tradeable strategy based on social media sentiment!

---

## Prerequisites

You'll need:
- Python 3.8 or higher
- A Reddit account + API credentials
- A FINTER account + JWT token

---

## Step 1: Install Dependencies

```bash
# Make sure you're in the project directory
cd alphaton-reddit-agent

# Create a virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt

# Download TextBlob corpora (needed for sentiment analysis)
python -m textblob.download_corpora
```

---

## Step 2: Get Reddit API Credentials

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Fill in:
   - **Name**: AlphatonAgent (or any name)
   - **Type**: Select "script"
   - **Description**: Sentiment analysis for trading
   - **About URL**: Leave blank
   - **Redirect URI**: http://localhost:8080
4. Click "Create app"
5. You'll see:
   - **Client ID**: The string under your app name (e.g., "abc123xyz")
   - **Client Secret**: The "secret" field

---

## Step 3: Get FINTER JWT Token

1. Log into your FINTER account at https://finter.quantit.io
2. Go to your account settings or API section
3. Generate or copy your JWT token
4. Save it securely

---

## Step 4: Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit the .env file with your credentials
nano .env  # or use any text editor
```

Your `.env` file should look like:

```
REDDIT_CLIENT_ID=abc123xyz
REDDIT_CLIENT_SECRET=your_secret_here
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
FINTER_JWT_TOKEN=your_long_jwt_token_here
```

**Important**: Never commit your `.env` file to git! It's already in `.gitignore`.

---

## Step 5: Run the Project

### Option A: Test Individual Components

Test FINTER connection:
```bash
python test_final.py
```

Test Reddit scraper:
```bash
python src/scraper.py
```

Test alpha generation:
```bash
python test_alpha_comprehensive.py
```

### Option B: Run Full Pipeline

Run everything end-to-end:
```bash
python main.py
```

This will:
1. ✅ Scrape Reddit for the last 7 days
2. ✅ Extract stock ticker mentions
3. ✅ Analyze sentiment for each mention
4. ✅ Map tickers to FINTER gvkeyiid
5. ✅ Generate FINTER-compliant alpha signals
6. ✅ Save results to CSV files

---

## Expected Output

After running `main.py`, you'll get:

```
📊 ALPHATON REDDIT AGENT - FULL PIPELINE
====================================

Step 1/5: Scraping Reddit...
   ✅ Scraped 150 posts from r/wallstreetbets

Step 2/5: Extracting ticker mentions...
   ✅ Found 87 ticker mentions
   📈 Top tickers: TSLA (15), AAPL (12), NVDA (10)...

Step 3/5: Analyzing sentiment...
   ✅ Analyzed 87 mentions

Step 4/5: Mapping to FINTER format...
   ✅ Mapped 82/87 tickers to gvkeyiid

Step 5/5: Generating alpha signals...
   ✅ Generated positions for 10 trading days
   💾 Saved to: output/reddit_sentiment_alpha_20241110.csv

🎉 PIPELINE COMPLETE!
```

---

## Understanding the Output

### Files Generated

1. **`reddit_posts.csv`**: Raw Reddit posts
2. **`ticker_mentions.csv`**: Extracted ticker mentions with sentiment
3. **`alpha_positions.csv`**: FINTER-ready position signals

### Alpha Positions Format

The alpha file contains:
- **Rows**: Trading days
- **Columns**: Stock gvkeyiid identifiers
- **Values**: Position sizes in dollars (positive = long, negative = short)

Example:
```
date        IQ001234  IQ005678  IQ009012
20241101    50000000  25000000  -10000000
20241102    45000000  30000000   0
```

---

## Next Steps: Using Your Alpha in FINTER

### 1. Upload to FINTER

```python
from src.finter_client import finter

# Register your alpha
alpha_code = open('output/alpha_positions.csv').read()
finter.register_alpha(
    name="Reddit Sentiment Alpha",
    code=alpha_code,
    description="Social sentiment from r/wallstreetbets"
)
```

### 2. Optimize Parameters (using QFlex MCP)

Use the QFlex MCP server to tune hyperparameters:
- Sentiment threshold
- Position sizing
- Holding period
- Rebalancing frequency

### 3. Backtest (using Alpha Simulator MCP)

Test your alpha on historical data:
```python
results = alpha_simulator.backtest(
    alpha_id="your_alpha_id",
    start_date=20230101,
    end_date=20241101
)
```

### 4. Schedule Execution (using Scheduler MCP)

Set up daily runs:
```python
scheduler.schedule_job(
    alpha_id="your_alpha_id",
    frequency="daily",
    time="09:00",  # Run at market open
    email_results=True
)
```

---

## Troubleshooting

### "Reddit authentication failed"
- Check your Reddit credentials in `.env`
- Make sure you created a "script" type app
- Verify your Reddit password is correct

### "FINTER_JWT_TOKEN not found"
- Make sure `.env` file exists
- Check token is copied correctly (no extra spaces)
- Verify token hasn't expired

### "No ticker mentions found"
- Reddit might not have had stock mentions in your date range
- Try expanding the date range in `main.py`
- Check if r/wallstreetbets is accessible

### "Failed to map ticker X"
- Some tickers might not be in FINTER's universe
- Check if ticker is valid US stock
- FINTER focuses on larger cap stocks

### "ModuleNotFoundError"
- Make sure you activated the virtual environment
- Run `pip install -r requirements.txt` again

---

## Customization

### Change Subreddit
Edit `src/scraper.py` line 34:
```python
self.subreddit = self.reddit.subreddit("stocks")  # or "investing", etc.
```

### Adjust Date Range
Edit `main.py`:
```python
start_date = datetime.now() - timedelta(days=14)  # 2 weeks instead of 7 days
```

### Modify Sentiment Weights
Edit `src/alpha.py` to change how sentiment maps to positions:
```python
position_size = sentiment * mention_count * 10_000_000  # Adjust multiplier
```

### Change Position Sizing
Edit alpha initialization:
```python
alpha = RedditSentimentAlpha(sentiment_df, leverage=2.0)  # 2x leverage
```

---

## Project Structure Recap

```
alphaton-reddit-agent/
├── src/
│   ├── scraper.py         # Reddit data collection
│   ├── sentiment.py       # NLP sentiment analysis
│   ├── alpha.py           # FINTER alpha generator
│   └── finter_client.py   # API client
├── main.py                # Run full pipeline
├── .env                   # Your credentials (create this!)
├── .env.example           # Template
├── requirements.txt       # Dependencies
└── QUICKSTART.md         # This file!
```

---

## Getting Help

1. **Check the docs**: See `README.md` and `MCP_SERVERS.md`
2. **Run tests**: Execute test files to isolate issues
3. **Check logs**: Look for error messages in console output
4. **Verify credentials**: Most issues are credential-related

---

## What You've Built

Congratulations! You now have:

✅ An automated Reddit sentiment scraper
✅ A sentiment analysis engine
✅ A FINTER-compliant alpha generator
✅ Integration with 17+ FINTER MCP servers
✅ A complete quant trading pipeline

**Next**: Experiment with different parameters, add more data sources, or combine with other MCP servers to create more sophisticated strategies!

---

## Advanced Usage

### Combine with Other MCP Servers

```python
# Use Market Voice for additional sentiment
market_voice_data = get_market_voice_sentiment('TSLA')

# Get fundamental data
fundamentals = stock_fundamental.get_data('TSLA')

# Combine signals
combined_alpha = reddit_alpha * 0.5 + fundamental_alpha * 0.5
```

### Add More Data Sources

- Twitter/X sentiment
- News headlines
- Analyst ratings
- Options flow
- Insider trading

### Create Ensemble Strategies

Use Model Search MCP to combine multiple alphas:
```python
meta_model = model_search.combine_models([
    'reddit_sentiment_alpha',
    'news_sentiment_alpha',
    'momentum_alpha'
])
```

---

Happy alpha hunting! 🚀📈
