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

        # Hardcoded mapping for the 50 stocks we have keys for
        # Format: gvkey (6 digits) + iid (3 digits) = gvkeyiid (9 digits)
        self.ticker_to_gvkeyiid = {
            'HON': '001300001', 'AMD': '001161001', 'AMGN': '001602001',
            'AAPL': '001690001', 'BRK.B': '002176002', 'JPM': '002968001',
            'CVX': '002991001', 'CAT': '002817001', 'KO': '003144001',
            'DIS': '003980001', 'XOM': '004503001', 'GE': '005047001',
            'HD': '005680001', 'JNJ': '006266001', 'INTC': '006008001',
            'IBM': '006066001', 'LRCX': '006565001', 'LLY': '006730001',
            'BAC': '007647001', 'MCD': '007154001', 'MRK': '007257001',
            'WFC': '008007001', 'NKE': '007906001', 'PEP': '008479001',
            'T': '009899001', 'ABBV': '016101001', 'PG': '008762001',
            'TXN': '010499001', 'TMO': '010530001', 'UNH': '010903001',
            'MSFT': '012141001', 'ORCL': '012142001', 'LIN': '025124001',
            'QCOM': '024800001', 'BABA': '020530090', 'ANET': '020748001',
            'UBER': '035077001', 'WMT': '011259001', 'COST': '029028001',
            'ASML': '061214090', 'AMZN': '064768001', 'NFLX': '147579001',
            'NVDA': '117768001', 'V': '179534001', 'MA': '160225001',
            'GOOGL': '160329001', 'META': '170617001', 'CRM': '157855001',
            'TSLA': '184996001', 'AVGO': '180711001'
        }

        logger.info(f"✅ Universe: {len(self.ticker_to_gvkeyiid)} securities")

    def _analyze_text_sentiment(self, text: str) -> float:
        """Analyze sentiment of a single text (-1.0 to 1.0)"""
        if not text or len(str(text).strip()) == 0:
            return 0.0

        try:
            blob = TextBlob(str(text))
            return round(float(blob.sentiment.polarity), 4)
        except Exception as e:
            logger.warning(f"⚠️  Sentiment failed: {e}")
            return 0.0

    def analyze_sentiment(self, mentions_df: pd.DataFrame) -> pd.DataFrame:
        """Analyze sentiment for all mentions in DataFrame"""
        logger.info("🧠 Analyzing sentiment...")

        if mentions_df.empty:
            logger.warning("⚠️  No mentions to analyze")
            return pd.DataFrame(columns=['ticker', 'date', 'score', 'text', 'post_id', 'sentiment'])

        # Create a copy to avoid modifying original
        result_df = mentions_df.copy()

        # Analyze sentiment for each text
        result_df['sentiment'] = result_df['text'].apply(self._analyze_text_sentiment)

        logger.info(f"✅ Analyzed {len(result_df)} mentions")
        logger.info(f"   Sentiment range: {result_df['sentiment'].min():.3f} to {result_df['sentiment'].max():.3f}")

        return result_df

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

        # Analyze sentiment for each mention if not already done
        if 'sentiment' not in mapped_df.columns:
            mapped_df['sentiment'] = mapped_df['text'].apply(self._analyze_text_sentiment)

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