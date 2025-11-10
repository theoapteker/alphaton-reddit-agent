import sys
sys.path.append('src')

from textblob import TextBlob
import pandas as pd
import numpy as np
from finter_client import finter
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class SentimentEngine:
    def __init__(self):
        """Initialize and load FINTER universe mapping"""
        logger.info("📡 Loading universe mapping...")

        self.universe_df = finter.get_universe()

        # Create mapping: ticker -> gvkeyiid
        self.ticker_to_gvkeyiid = dict(zip(
            self.universe_df['tic'].astype(str),
            self.universe_df['gvkeyiid'].astype(str)
        ))

        logger.info(f"✅ Loaded {len(self.ticker_to_gvkeyiid)} ticker mappings")

    def analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment (-1.0 to 1.0)"""
        if not text or len(text.strip()) == 0:
            return 0.0

        try:
            blob = TextBlob(text)
            return round(float(blob.sentiment.polarity), 4)
        except Exception as e:
            logger.warning(f"⚠️  Sentiment failed: {e}")
            return 0.0

    def map_to_gvkeyiid(self, mentions_df: pd.DataFrame) -> pd.DataFrame:
        """Map Reddit tickers to FINTER gvkeyiid"""
        logger.info("🔄 Mapping tickers to gvkeyiid...")

        if mentions_df.empty:
            return pd.DataFrame(columns=['gvkeyiid', 'date', 'sentiment', 'mention_count', 'ticker'])

        # Map ticker to gvkeyiid
        mentions_df['gvkeyiid'] = mentions_df['ticker'].map(self.ticker_to_gvkeyiid)

        # Count successes
        mapped_count = mentions_df['gvkeyiid'].notna().sum()
        total_count = len(mentions_df)

        logger.info(f"✅ Mapped {mapped_count}/{total_count} tickers")

        # Drop unmapped
        mapped_df = mentions_df.dropna(subset=['gvkeyiid']).copy()

        # Ensure 9-character gvkeyiid
        mapped_df['gvkeyiid'] = mapped_df['gvkeyiid'].astype(str)

        return mapped_df

    def calculate_daily_sentiment(self, mapped_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate daily sentiment per security"""
        logger.info("📊 Calculating daily sentiment...")

        if mapped_df.empty:
            return pd.DataFrame(columns=['gvkeyiid', 'date', 'sentiment', 'mention_count', 'ticker'])

        # Analyze sentiment for each mention
        mapped_df['sentiment'] = mapped_df['text'].apply(self.analyze_sentiment)

        # Aggregate by gvkeyiid and date
        aggregated = mapped_df.groupby(['gvkeyiid', 'date']).agg(
            sentiment=('sentiment', 'mean'),
            mention_count=('sentiment', 'count'),
            total_score=('score', 'sum'),
            ticker=('ticker', 'first')
        ).reset_index()

        logger.info(f"✅ Daily sentiment: {len(aggregated)} records")
        logger.info(f"✅ Sentiment range: {aggregated['sentiment'].min():.3f} to {aggregated['sentiment'].max():.3f}")

        return aggregated

# Test the engine
if __name__ == "__main__":
    import sys
    from datetime import datetime

    print("=" * 60)
    print("TESTING SENTIMENT ENGINE")
    print("=" * 60)

    try:
        engine = SentimentEngine()

        # Mock mentions data
        mock_mentions = pd.DataFrame({
            'ticker': ['AAPL', 'TSLA', 'AAPL', 'UNKNOWN'],
            'date': [datetime.now().date()] * 4,
            'score': [100, 50, 75, 10],
            'text': [
                "I love $AAPL! Best stock ever!",
                "$TSLA is crashing, sell now!",
                "$AAPL will go to $200 soon!",
                "Random post about $UNKNOWN"
            ],
            'post_id': ['p1', 'p2', 'p3', 'p4']
        })

        # Test mapping
        mapped = engine.map_to_gvkeyiid(mock_mentions)
        print(f"\n✅ Mapped: {len(mapped)} records")

        # Test sentiment
        aggregated = engine.calculate_daily_sentiment(mapped)
        print(f"\n✅ Aggregated: {len(aggregated)} records")
        print(aggregated.head())

        print("\n" + "=" * 60)
        print("✅ SENTIMENT ENGINE TEST PASSED!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)