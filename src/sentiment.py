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
    def __init__(self, use_finter_mapping: bool = False):
        """
        Initialize sentiment engine

        Args:
            use_finter_mapping: If True, try to load FINTER ticker->gvkeyiid mapping
                               (currently not working with API, set to False)
        """
        self.ticker_to_gvkeyiid = {}

        if use_finter_mapping:
            logger.info("📡 Building ticker mapping...")
            try:
                self.ticker_to_gvkeyiid = finter.build_ticker_mapping(
                    max_securities=500,
                    use_cache=True
                )
                logger.info(f"✅ Loaded {len(self.ticker_to_gvkeyiid)} ticker mappings")
            except Exception as e:
                logger.warning(f"⚠️  Failed to build ticker mapping: {e}")
                logger.info("📝 Using hardcoded common ticker mappings instead")
                self.ticker_to_gvkeyiid = self._get_common_ticker_mappings()
        else:
            logger.info("📝 Using hardcoded common ticker mappings")
            self.ticker_to_gvkeyiid = self._get_common_ticker_mappings()

        logger.info(f"✅ Loaded {len(self.ticker_to_gvkeyiid)} ticker mappings")

    def _get_common_ticker_mappings(self) -> dict:
        """
        Hardcoded mappings for common tickers (as fallback when API fails)
        Format: ticker -> gvkeyiid (9 digits)

        Note: These are example mappings. In production, you'd need the actual
        gvkeyiid values from FINTER's universe data.
        """
        return {
            # Common tech stocks
            'AAPL': '001690001',  # Apple
            'MSFT': '012141001',  # Microsoft
            'GOOGL': '029089001', # Alphabet
            'AMZN': '018163001',  # Amazon
            'TSLA': '011359001',  # Tesla
            'NVDA': '011532001',  # NVIDIA
            'META': '012851001',  # Meta

            # Common finance stocks
            'JPM': '006085001',   # JPMorgan Chase
            'BAC': '001321001',   # Bank of America
            'WFC': '006174001',   # Wells Fargo
            'GS': '004280001',    # Goldman Sachs

            # Other popular stocks
            'DIS': '002819001',   # Disney
            'NFLX': '015917001',  # Netflix
            'AMD': '001208001',   # AMD
            'INTC': '005350001',  # Intel
            'ORCL': '007334001',  # Oracle
            'CRM': '020572001',   # Salesforce
            'UBER': '032113001',  # Uber
            'LYFT': '031806001',  # Lyft
            'SQ': '027129001',    # Block (Square)
            'PYPL': '013193001',  # PayPal
        }

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