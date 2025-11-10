#!/usr/bin/env python3
"""
Alphaton Reddit Agent - Main Pipeline
Scrapes Reddit, analyzes sentiment, generates FINTER alpha
"""

import sys
sys.path.append('src')

import pandas as pd
from datetime import datetime, timedelta
import logging
import os

from scraper import RedditScraper
from sentiment import SentimentEngine
from alpha import RedditSentimentAlpha

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_banner():
    """Print fancy banner"""
    print("\n" + "=" * 60)
    print("📊 ALPHATON REDDIT AGENT - FULL PIPELINE")
    print("=" * 60 + "\n")

def print_step(step_num, total_steps, description):
    """Print step header"""
    print(f"\n{'─' * 60}")
    print(f"Step {step_num}/{total_steps}: {description}")
    print('─' * 60)

def save_output(df, filename, description):
    """Save DataFrame to CSV"""
    os.makedirs('output', exist_ok=True)
    filepath = f'output/{filename}'
    df.to_csv(filepath, index=True)
    logger.info(f"💾 Saved {description} to: {filepath}")
    return filepath

def main():
    """Run the complete pipeline"""
    try:
        print_banner()

        # Configuration
        LOOKBACK_DAYS = 7
        ALPHA_START_DATE = 20241101  # Adjust as needed
        ALPHA_END_DATE = 20241110    # Adjust as needed
        LEVERAGE = 1.0

        total_steps = 5

        # ═══════════════════════════════════════════════════════════
        # STEP 1: Scrape Reddit
        # ═══════════════════════════════════════════════════════════
        print_step(1, total_steps, "Scraping Reddit for stock mentions")

        scraper = RedditScraper()

        # Define date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=LOOKBACK_DAYS)

        logger.info(f"📅 Date range: {start_date.date()} to {end_date.date()}")

        # Scrape posts
        posts_df = scraper.scrape_date_range(start_date, end_date)

        if posts_df.empty:
            logger.error("❌ No posts scraped! Check Reddit connection.")
            return

        logger.info(f"✅ Scraped {len(posts_df)} posts from r/wallstreetbets")
        save_output(posts_df, 'reddit_posts.csv', 'raw Reddit posts')

        # ═══════════════════════════════════════════════════════════
        # STEP 2: Extract Ticker Mentions
        # ═══════════════════════════════════════════════════════════
        print_step(2, total_steps, "Extracting ticker mentions")

        mentions_df = scraper.extract_ticker_mentions(posts_df)

        if mentions_df.empty:
            logger.error("❌ No ticker mentions found!")
            logger.info("💡 Try expanding the date range or checking a different subreddit")
            return

        logger.info(f"✅ Found {len(mentions_df)} ticker mentions")

        # Show top tickers
        top_tickers = mentions_df['ticker'].value_counts().head(10)
        print("\n📈 Top 10 Most Mentioned Tickers:")
        for ticker, count in top_tickers.items():
            print(f"   ${ticker}: {count} mentions")

        # ═══════════════════════════════════════════════════════════
        # STEP 3: Analyze Sentiment
        # ═══════════════════════════════════════════════════════════
        print_step(3, total_steps, "Analyzing sentiment")

        engine = SentimentEngine()

        # Add sentiment scores
        logger.info("🧠 Running sentiment analysis on text...")
        mentions_df['sentiment'] = mentions_df['text'].apply(engine.analyze_sentiment)

        # Show sentiment distribution
        avg_sentiment = mentions_df['sentiment'].mean()
        pos_count = (mentions_df['sentiment'] > 0.1).sum()
        neg_count = (mentions_df['sentiment'] < -0.1).sum()
        neu_count = len(mentions_df) - pos_count - neg_count

        print(f"\n😊 Sentiment Distribution:")
        print(f"   Positive: {pos_count} ({pos_count/len(mentions_df)*100:.1f}%)")
        print(f"   Neutral:  {neu_count} ({neu_count/len(mentions_df)*100:.1f}%)")
        print(f"   Negative: {neg_count} ({neg_count/len(mentions_df)*100:.1f}%)")
        print(f"   Average:  {avg_sentiment:.3f}")

        save_output(mentions_df, 'ticker_mentions_with_sentiment.csv', 'mentions with sentiment')

        # ═══════════════════════════════════════════════════════════
        # STEP 4: Map to FINTER Format
        # ═══════════════════════════════════════════════════════════
        print_step(4, total_steps, "Mapping tickers to FINTER gvkeyiid")

        sentiment_df = engine.map_to_gvkeyiid(mentions_df)

        if sentiment_df.empty:
            logger.error("❌ No tickers could be mapped to FINTER universe!")
            logger.info("💡 This might mean the mentioned stocks aren't in FINTER's universe")
            return

        mapped_count = sentiment_df['gvkeyiid'].notna().sum()
        logger.info(f"✅ Mapped {mapped_count}/{len(mentions_df)} tickers to gvkeyiid")

        # Show mapping stats
        print(f"\n🔄 Mapping Statistics:")
        print(f"   Successfully mapped: {mapped_count}")
        print(f"   Failed to map: {len(mentions_df) - mapped_count}")

        # Show sample mappings
        if not sentiment_df.empty:
            print("\n📋 Sample Ticker → gvkeyiid Mappings:")
            sample = sentiment_df[['ticker', 'gvkeyiid']].drop_duplicates().head(5)
            for _, row in sample.iterrows():
                print(f"   ${row['ticker']} → {row['gvkeyiid']}")

        save_output(sentiment_df, 'finter_sentiment_data.csv', 'FINTER-formatted sentiment')

        # ═══════════════════════════════════════════════════════════
        # STEP 5: Generate Alpha Signals
        # ═══════════════════════════════════════════════════════════
        print_step(5, total_steps, "Generating FINTER alpha signals")

        # Create alpha strategy
        alpha = RedditSentimentAlpha(
            sentiment_df=sentiment_df,
            leverage=LEVERAGE
        )

        logger.info(f"📊 Generating positions for {ALPHA_START_DATE} to {ALPHA_END_DATE}")

        # Generate position signals
        positions_df = alpha.get(start=ALPHA_START_DATE, end=ALPHA_END_DATE)

        if positions_df.empty:
            logger.error("❌ No positions generated!")
            return

        # Show position stats
        num_days = len(positions_df)
        num_stocks = len(positions_df.columns)
        total_positions = positions_df.notna().sum().sum()
        avg_position_size = positions_df.abs().mean().mean()

        print(f"\n📊 Alpha Statistics:")
        print(f"   Trading days: {num_days}")
        print(f"   Unique stocks: {num_stocks}")
        print(f"   Total positions: {total_positions}")
        print(f"   Avg position size: ${avg_position_size:,.0f}")

        # Show sample positions for first day
        first_day = positions_df.index[0]
        first_day_positions = positions_df.loc[first_day].dropna().sort_values(ascending=False)

        if len(first_day_positions) > 0:
            print(f"\n💼 Sample Positions ({first_day}):")
            for gvkeyiid, position in first_day_positions.head(5).items():
                direction = "LONG" if position > 0 else "SHORT"
                print(f"   {gvkeyiid}: ${position:,.0f} ({direction})")

        # Save positions
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        positions_file = save_output(
            positions_df,
            f'reddit_sentiment_alpha_{timestamp}.csv',
            'alpha positions'
        )

        # ═══════════════════════════════════════════════════════════
        # SUCCESS!
        # ═══════════════════════════════════════════════════════════
        print("\n" + "=" * 60)
        print("🎉 PIPELINE COMPLETE!")
        print("=" * 60)
        print(f"\n✅ All files saved to: output/")
        print(f"\n📈 Next Steps:")
        print(f"   1. Review the generated positions in: {positions_file}")
        print(f"   2. Upload to FINTER for backtesting")
        print(f"   3. Use QFlex MCP to optimize parameters")
        print(f"   4. Use Alpha Simulator MCP to test performance")
        print(f"\n💡 To customize, edit the configuration variables at the top of main.py")
        print()

    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
