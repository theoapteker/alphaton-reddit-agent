#!/usr/bin/env python3
"""
Alphaton Reddit Agent - Main Entry Point

This script demonstrates the complete workflow:
1. Scrape Reddit for stock mentions
2. Analyze sentiment
3. Generate FINTER-compliant alpha signals
"""

import sys
import os
from datetime import datetime, timedelta
import pandas as pd

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scraper import RedditScraper
from sentiment import SentimentEngine
from alpha import RedditSentimentAlpha

def main():
    """
    Main workflow for generating alpha signals from Reddit sentiment
    """
    print("=" * 70)
    print("🚀 ALPHATON REDDIT AGENT")
    print("=" * 70)
    print()

    try:
        # Step 1: Scrape Reddit data
        print("📡 STEP 1: Scraping Reddit for stock mentions...")
        print("-" * 70)

        scraper = RedditScraper()

        # Scrape last 7 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        posts_df = scraper.scrape_date_range(start_date, end_date)
        mentions_df = scraper.extract_ticker_mentions(posts_df)

        if mentions_df.empty:
            print("\n⚠️  No stock mentions found. Try a different date range.")
            return 1

        print(f"\n✅ Found {len(mentions_df)} ticker mentions across {len(posts_df)} posts")
        print()

        # Step 2: Analyze sentiment
        print("🧠 STEP 2: Analyzing sentiment...")
        print("-" * 70)

        engine = SentimentEngine()
        sentiment_df = engine.analyze_sentiment(mentions_df)

        print(f"✅ Analyzed sentiment for {len(sentiment_df)} mentions")
        print()

        # Show top sentiment scores
        if not sentiment_df.empty:
            print("📊 Top 5 Most Positive Sentiment:")
            top_positive = sentiment_df.nlargest(5, 'sentiment')[['ticker', 'sentiment', 'score']]
            print(top_positive.to_string(index=False))
            print()

        # Step 3: Map to FINTER format
        print("🗺️  STEP 3: Mapping tickers to FINTER gvkeyiid...")
        print("-" * 70)

        finter_df = engine.map_to_gvkeyiid(sentiment_df)

        if finter_df.empty:
            print("⚠️  Could not map any tickers to FINTER universe")
            return 1

        print(f"✅ Mapped {len(finter_df)} mentions to FINTER format")
        print()

        # Step 4: Generate alpha signals
        print("📈 STEP 4: Generating FINTER-compliant alpha signals...")
        print("-" * 70)

        alpha = RedditSentimentAlpha(finter_df, leverage=1.0)

        # Generate positions for the date range
        start_date_finter = int(start_date.strftime("%Y%m%d"))
        end_date_finter = int(end_date.strftime("%Y%m%d"))

        positions_df = alpha.get(start=start_date_finter, end=end_date_finter)

        if not positions_df.empty:
            print(f"✅ Generated positions for {len(positions_df)} trading days")
            print(f"   Total unique stocks: {len(positions_df.columns)}")
            print()

            # Show summary statistics
            print("📊 Position Summary:")
            total_positions = positions_df.notna().sum().sum()
            avg_positions_per_day = positions_df.notna().sum(axis=1).mean()

            print(f"   Total positions: {total_positions}")
            print(f"   Avg positions per day: {avg_positions_per_day:.1f}")
            print(f"   Max position size: ${positions_df.abs().max().max():,.0f}")
            print()
        else:
            print("⚠️  No positions generated (check date alignment)")
            return 1

        # Success!
        print("=" * 70)
        print("✅ SUCCESS! Alpha generation complete")
        print("=" * 70)
        print()
        print("Next steps:")
        print("  1. Run backtests using test_alpha_comprehensive.py")
        print("  2. Optimize parameters using FINTER MCP servers")
        print("  3. Submit to FINTER for live trading:")
        print("     python submit_to_finter.py --model-name reddit_sentiment_v1")
        print()

        return 0

    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ ERROR: {str(e)}")
        print("=" * 70)
        print()
        print("Troubleshooting:")
        print("  1. Make sure you've activated the virtual environment:")
        print("     source venv/bin/activate")
        print()
        print("  2. Check that all dependencies are installed:")
        print("     pip install -r requirements.txt")
        print()
        print("  3. Verify your Reddit API credentials in .env file")
        print("     (Required: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET,")
        print("      REDDIT_USERNAME, REDDIT_PASSWORD)")
        print()

        import traceback
        traceback.print_exc()

        return 1

if __name__ == "__main__":
    sys.exit(main())
