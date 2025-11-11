import sys
sys.path.append('src')

from textblob import TextBlob
import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class SentimentEngine:
    # Hardcoded ticker to gvkeyiid mapping
    TICKER_MAPPING = {
        'HON': '000130001',
        'AMD': '000116101',
        'AMGN': '000160201',
        'AAPL': '000169001',
        'BRK.B': '000217602',
        'JPM': '000296801',
        'CVX': '000299101',
        'CAT': '000281701',
        'KO': '000314401',
        'DIS': '000398001',
        'XOM': '000450301',
        'GE': '000504701',
        'HD': '000568001',
        'JNJ': '000626601',
        'INTC': '000600801',
        'IBM': '000606601',
        'LRCX': '000656501',
        'LLY': '000673001',
        'BAC': '000764701',
        'MCD': '000715401',
        'MRK': '000725701',
        'WFC': '000800701',
        'NKE': '000790601',
        'PEP': '000847901',
        'T': '000989901',
        'ABBV': '001610101',
        'PG': '000876201',
        'TXN': '001049901',
        'TMO': '001053001',
        'UNH': '001090301',
        'MSFT': '001214101',
        'ORCL': '001214201',
        'LIN': '002512401',
        'QCOM': '002480001',
        'BABA': '002053090',
        'ANET': '002074801',
        'UBER': '003507701',
        'WMT': '001125901',
        'COST': '002902801',
        'ASML': '006121490',
        'AMZN': '006476801',
        'NFLX': '014757901',
        'NVDA': '011776801',
        'V': '017953401',
        'MA': '016022501',
        'GOOGL': '016032901',
        'META': '017061701',
        'CRM': '015785501',
        'TSLA': '018499601',
        'AVGO': '018071101'
    }

    def __init__(self):
        """Initialize with hardcoded ticker mapping"""
        logger.info("📡 Loading hardcoded ticker mapping...")

        # Use the hardcoded mapping
        self.ticker_to_gvkeyiid = self.TICKER_MAPPING.copy()

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