#!/usr/bin/env python3
"""
FINTER Live Trading Submission Script

This script runs the complete pipeline and submits the alpha to FINTER for live trading:
1. Scrape Reddit for stock mentions
2. Analyze sentiment
3. Generate FINTER-compliant alpha signals
4. Validate positions
5. Submit to FINTER production

Usage:
    python submit_to_finter.py --model-name reddit_sentiment_v1 --days 30

Options:
    --model-name    Name for the model (default: reddit_sentiment_v1)
    --days          Days of historical data to analyze (default: 30)
    --leverage      Position leverage multiplier (default: 1.0)
    --universe      FINTER universe (default: us_stock)
    --dry-run       Run pipeline without submitting to FINTER
"""

import sys
import os
import argparse
from datetime import datetime, timedelta
import pandas as pd
import json

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scraper import RedditScraper
from sentiment import SentimentEngine
from alpha import RedditSentimentAlpha
from finter_client import FinterAPI

def main():
    """
    Complete workflow for FINTER submission
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Submit Reddit Sentiment Alpha to FINTER')
    parser.add_argument('--model-name', default='reddit_sentiment_v1',
                        help='Model name for FINTER (default: reddit_sentiment_v1)')
    parser.add_argument('--days', type=int, default=30,
                        help='Days of historical data (default: 30)')
    parser.add_argument('--leverage', type=float, default=1.0,
                        help='Position leverage (default: 1.0)')
    parser.add_argument('--universe', default='us_stock',
                        help='FINTER universe (default: us_stock)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Run without submitting to FINTER')

    args = parser.parse_args()

    print("=" * 80)
    print("🚀 FINTER LIVE TRADING SUBMISSION")
    print("=" * 80)
    print(f"\nModel Name: {args.model_name}")
    print(f"Historical Data: Last {args.days} days")
    print(f"Leverage: {args.leverage}x")
    print(f"Universe: {args.universe}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE SUBMISSION'}")
    print()

    try:
        # =====================================================================
        # STEP 1: Scrape Reddit data
        # =====================================================================
        print("📡 STEP 1: Scraping Reddit for stock mentions...")
        print("-" * 80)

        scraper = RedditScraper()

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=args.days)

        print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

        posts_df = scraper.scrape_date_range(start_date, end_date)
        mentions_df = scraper.extract_ticker_mentions(posts_df)

        if mentions_df.empty:
            print("\n❌ ERROR: No stock mentions found. Try a different date range.")
            return 1

        print(f"✅ Found {len(mentions_df)} ticker mentions across {len(posts_df)} posts")
        print()

        # =====================================================================
        # STEP 2: Analyze sentiment
        # =====================================================================
        print("🧠 STEP 2: Analyzing sentiment...")
        print("-" * 80)

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

        # =====================================================================
        # STEP 3: Map to FINTER format
        # =====================================================================
        print("🗺️  STEP 3: Mapping tickers to FINTER gvkeyiid...")
        print("-" * 80)

        finter_df = engine.map_to_gvkeyiid(sentiment_df)

        if finter_df.empty:
            print("❌ ERROR: Could not map any tickers to FINTER universe")
            return 1

        print(f"✅ Mapped {len(finter_df)} mentions to FINTER format")

        # Show top mapped stocks
        if 'gvkeyiid' in finter_df.columns:
            unique_stocks = finter_df['gvkeyiid'].nunique()
            print(f"   Unique stocks: {unique_stocks}")
        print()

        # =====================================================================
        # STEP 4: Generate alpha signals
        # =====================================================================
        print("📈 STEP 4: Generating FINTER-compliant alpha signals...")
        print("-" * 80)

        alpha = RedditSentimentAlpha(finter_df, leverage=args.leverage)

        # Generate positions for the date range
        start_date_finter = int(start_date.strftime("%Y%m%d"))
        end_date_finter = int(end_date.strftime("%Y%m%d"))

        positions_df = alpha.get(start=start_date_finter, end=end_date_finter)

        if positions_df.empty:
            print("❌ ERROR: No positions generated (check date alignment)")
            return 1

        print(f"✅ Generated positions for {len(positions_df)} trading days")
        print(f"   Total unique stocks: {len(positions_df.columns)}")
        print()

        # Show summary statistics
        print("📊 Position Summary:")
        total_positions = positions_df.notna().sum().sum()
        avg_positions_per_day = positions_df.notna().sum(axis=1).mean()
        max_position = positions_df.abs().max().max()
        total_gross_exposure = positions_df.abs().sum(axis=1).mean()

        print(f"   Total positions: {total_positions}")
        print(f"   Avg positions per day: {avg_positions_per_day:.1f}")
        print(f"   Max position size: ${max_position:,.0f}")
        print(f"   Avg gross exposure: ${total_gross_exposure:,.0f}")
        print()

        # =====================================================================
        # STEP 5: Validate alpha
        # =====================================================================
        print("✅ STEP 5: Validating alpha strategy...")
        print("-" * 80)

        validation_result = alpha.validate(start=start_date_finter, end=end_date_finter)

        if not validation_result['is_valid']:
            print("❌ ERROR: Validation failed!")
            print(f"   Max difference: ${validation_result['max_difference']:.2f}")
            print(f"   Threshold: ${validation_result['threshold']:.2f}")
            print()
            print("This alpha does not meet FINTER's start-end dependency requirements.")
            return 1

        print(f"✅ Validation passed!")
        print(f"   Max difference: ${validation_result['max_difference']:.2f}")
        print(f"   Threshold: ${validation_result['threshold']:.2f}")
        print()

        # =====================================================================
        # STEP 6: Save positions
        # =====================================================================
        print("💾 STEP 6: Saving positions...")
        print("-" * 80)

        # Save positions to JSON (FINTER format)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        positions_file = f"positions_{args.model_name}_{timestamp}.json"

        positions_json = positions_df.to_json(orient='split', date_format='iso')

        with open(positions_file, 'w') as f:
            f.write(positions_json)

        print(f"✅ Positions saved to: {positions_file}")
        print(f"   File size: {len(positions_json)} bytes")
        print()

        # =====================================================================
        # STEP 7: Submit to FINTER
        # =====================================================================
        if args.dry_run:
            print("🔍 DRY RUN MODE - Skipping FINTER submission")
            print("-" * 80)
            print()
            print("The following would be submitted:")
            print(f"  Model Name: {args.model_name}")
            print(f"  Universe: {args.universe}")
            print(f"  Docker Image: public.ecr.aws/d2s6t0y4/reddit-agent:v1")
            print(f"  Schedule: 0 16 * * * (daily at 4 PM UTC)")
            print(f"  Position File: {positions_file}")
            print()
        else:
            print("🚀 STEP 7: Submitting to FINTER for live trading...")
            print("-" * 80)

            finter = FinterAPI()

            # Submit model
            result = finter.submit_model(
                model_name=args.model_name,
                universe=args.universe,
                docker_image="public.ecr.aws/d2s6t0y4/reddit-agent:v1"
            )

            print(f"✅ Successfully submitted to FINTER!")
            print(f"   Model ID: {result.get('model_id')}")
            print(f"   Validation URL: {result.get('validation_url')}")
            print()

        # =====================================================================
        # SUCCESS!
        # =====================================================================
        print("=" * 80)
        print("✅ SUBMISSION COMPLETE!")
        print("=" * 80)
        print()

        if not args.dry_run:
            print("Your alpha is now live on FINTER! 🎉")
            print()
            print("Next steps:")
            print("  1. Monitor performance via FINTER dashboard")
            print("  2. Check validation URL for detailed metrics")
            print("  3. Review daily execution logs")
            print()
            print("Schedule: Runs daily at 4 PM UTC (0 16 * * *)")
        else:
            print("To submit for real, run without --dry-run flag:")
            print(f"  python submit_to_finter.py --model-name {args.model_name}")

        print()
        return 0

    except Exception as e:
        print()
        print("=" * 80)
        print(f"❌ ERROR: {str(e)}")
        print("=" * 80)
        print()
        print("Troubleshooting:")
        print("  1. Make sure you've activated the virtual environment:")
        print("     source venv/bin/activate")
        print()
        print("  2. Check that all dependencies are installed:")
        print("     pip install -r requirements.txt")
        print()
        print("  3. Verify your credentials:")
        print("     - Reddit API: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET")
        print("     - FINTER API: FINTER_JWT_TOKEN")
        print()
        print("  4. Ensure FINTER API is accessible")
        print()

        import traceback
        traceback.print_exc()

        return 1

if __name__ == "__main__":
    sys.exit(main())
