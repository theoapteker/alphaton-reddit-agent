# Alphaton Reddit Agent

A quantitative trading strategy generator that analyzes Reddit sentiment to create FINTER-compliant alpha signals.

## Overview

This project combines social media sentiment analysis with quantitative finance to generate trading signals. It scrapes Reddit for stock mentions, analyzes sentiment using NLP, and generates FINTER-compliant alpha strategies that can be backtested and deployed.

## Key Features

- **Reddit Data Scraping**: Extracts stock mentions and discussions from Reddit
- **Sentiment Analysis**: Uses TextBlob for natural language sentiment scoring
- **FINTER Integration**: Generates fully compliant alpha strategies for the FINTER platform
- **Ticker Mapping**: Converts stock tickers to FINTER's gvkeyiid format
- **Trading Day Alignment**: Ensures all signals align with actual trading days
- **Position Sizing**: Implements proper position sizing with configurable leverage

## Project Structure

```
alphaton-reddit-agent/
├── src/
│   ├── alpha.py           # FINTER-compliant alpha strategy generator
│   ├── sentiment.py       # Sentiment analysis engine with ticker mapping
│   ├── scraper.py         # Reddit data scraper
│   └── finter_client.py   # FINTER API client
├── main.py                # Main entry point for the complete workflow
├── setup.sh               # Automated setup script
├── test_*.py              # Test suites for various components
├── requirements.txt       # Python dependencies
├── MCP_SERVERS.md        # Documentation for all available MCP servers
└── README.md             # This file
```

## Core Components

### 1. RedditSentimentAlpha (`src/alpha.py`)

FINTER-compliant alpha strategy that:
- Uses gvkeyiid (not tickers) for stock identification
- Shifts positions by 1 day to avoid look-ahead bias
- Uses trading days only (no weekends/holidays)
- Enforces max position size of $100M
- Passes FINTER's strict start-end validation

### 2. SentimentEngine (`src/sentiment.py`)

Handles sentiment analysis and data mapping:
- Analyzes text sentiment using TextBlob (scale: -1.0 to 1.0)
- Maps stock tickers to FINTER's gvkeyiid format
- Loads and maintains universe mapping from FINTER
- Processes Reddit mentions into structured sentiment data

### 3. Reddit Scraper (`src/scraper.py`)

Extracts stock-related content from Reddit:
- Scrapes relevant subreddits for stock discussions
- Identifies stock ticker mentions
- Collects post and comment data
- Timestamps all mentions for temporal analysis

### 4. FINTER Client (`src/finter_client.py`)

API client for FINTER platform:
- Retrieves trading days
- Fetches universe data (stock mappings)
- Handles authentication and rate limiting
- Provides data formatting utilities

## FINTER MCP Servers

This project integrates with 17+ MCP (Model Context Protocol) servers on the FINTER platform for:
- Market data and fundamentals
- Stock screening and thematic analysis
- Alpha generation and optimization
- Backtesting and model search
- Scheduling and automation

**See [MCP_SERVERS.md](MCP_SERVERS.md) for complete documentation of all available servers.**

## Installation

### Quick Setup (Recommended)

Run the automated setup script:
```bash
./setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies including `praw`, `textblob`, `pandas`, etc.
- Verify Python version compatibility

### Manual Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd alphaton-reddit-agent
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure Reddit API credentials:
Create a `.env` file in the project root:
```bash
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USERNAME=your_username
REDDIT_PASSWORD=your_password
```

5. Configure FINTER credentials (if required):
```bash
# Add your FINTER API credentials to environment variables
export FINTER_API_KEY="your_api_key"
```

### ⚠️ Important: Always Activate Virtual Environment

Before running any Python scripts, **always activate the virtual environment**:
```bash
source venv/bin/activate  # On Mac/Linux
# or
venv\Scripts\activate     # On Windows
```

If you see `ModuleNotFoundError: No module named 'praw'`, it means you forgot to activate the venv!

## Usage

### Quick Start

Run the complete workflow with the main entry point:
```bash
# Make sure virtual environment is activated!
source venv/bin/activate

# Run the complete workflow
python main.py
```

This will:
1. Scrape Reddit for stock mentions (last 7 days)
2. Initialize sentiment engine with hardcoded ticker mappings
3. Map tickers to FINTER gvkeyiid format (for common stocks)
4. Analyze sentiment using TextBlob
5. Generate FINTER-compliant alpha signals

**Note:** Currently uses hardcoded ticker->gvkeyiid mappings for ~20 common stocks (AAPL, TSLA, etc.) as the FINTER `/id/convert` API endpoint is not working.

### Basic Alpha Generation (Programmatic)

```python
from src.sentiment import SentimentEngine
from src.alpha import RedditSentimentAlpha
import pandas as pd

# Initialize sentiment engine
# use_finter_mapping=False uses hardcoded common ticker mappings
# Set to True to try FINTER API (currently broken)
engine = SentimentEngine(use_finter_mapping=False)

# Load Reddit mentions data (from scraper)
mentions_df = pd.read_csv('reddit_mentions.csv')

# Map to FINTER format
finter_df = engine.map_to_gvkeyiid(mentions_df)

# Analyze sentiment
sentiment_df = engine.calculate_daily_sentiment(finter_df)

# Create alpha strategy
alpha = RedditSentimentAlpha(sentiment_df, leverage=1.0)

# Generate positions for date range
positions = alpha.get(start=20240101, end=20241231)
```

### Running Tests

```bash
# Test FINTER integration
python test_finter_working.py

# Test sentiment analysis
python test_reddit_direct.py

# Comprehensive alpha testing
python test_alpha_comprehensive.py
```

## Workflow

### Typical Alpha Development Process

1. **Data Collection**: Scrape Reddit for stock mentions
2. **Sentiment Analysis**: Analyze sentiment and map tickers
3. **Alpha Generation**: Create FINTER-compliant alpha using `RedditSentimentAlpha`
4. **Parameter Optimization**: Use QFlex MCP server to optimize parameters
5. **Backtesting**: Test alpha using Alpha Simulator MCP server
6. **Deployment**: Register model in FINTER for live trading

### Integration with MCP Servers

```python
# Example workflow using multiple MCP servers:

# 1. Generate alpha (FINTER MCP)
alpha_code = generate_alpha_code()

# 2. Optimize parameters (QFlex MCP)
optimized_params = optimize_parameters(alpha_code)

# 3. Backtest (Alpha Simulator MCP)
backtest_results = run_backtest(alpha_code, optimized_params)

# 4. Schedule execution (Scheduler MCP)
schedule_alpha_execution(alpha_code, email_results=True)
```

## Requirements

- Python 3.8+
- pandas
- numpy
- textblob
- requests
- Additional dependencies listed in `requirements.txt`

## FINTER Compliance

This project follows FINTER's strict requirements:

1. **gvkeyiid Usage**: All stock identifiers use FINTER's gvkeyiid format
2. **Trading Days**: Only valid trading days from FINTER API
3. **Position Shifting**: 1-day lag to prevent look-ahead bias
4. **Position Sizing**: Respects $100M maximum position limit
5. **Date Validation**: Proper start/end date arithmetic
6. **DataFrame Format**: Index=dates, Columns=gvkeyiid, Values=position_size

## Testing

The project includes comprehensive test suites:

- `test_alpha_comprehensive.py`: Full alpha strategy testing
- `test_finter_working.py`: FINTER API integration tests
- `test_reddit_direct.py`: Reddit scraper functionality
- `test_id_convert.py`: Ticker to gvkeyiid mapping tests
- `test_token.py`: Authentication and token management

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit your changes: `git commit -am 'Add new feature'`
3. Push to the branch: `git push origin feature/your-feature`
4. Submit a pull request

## Additional Resources

- [MCP Servers Documentation](MCP_SERVERS.md) - Complete guide to all FINTER MCP servers
- FINTER Platform Documentation - Official FINTER API documentation
- n8n Workflow Automation - Professor's n8n server for workflow integration

## License

[Specify your license here]

## Acknowledgments

- FINTER platform for MCP servers and alpha infrastructure
- Professor for n8n server access
- Reddit API for social sentiment data

## Contact

[Add your contact information or team details]
