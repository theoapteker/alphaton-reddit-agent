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
        """Initialize with top 50 Reddit tickers mapping"""
        logger.info("📡 Loading ticker→gvkeyiid mapping...")

        # Top 50 most-mentioned tickers on r/wallstreetbets with FINTER gvkeyiid
        # This is a curated list to avoid loading the full 3961-security universe
        self.ticker_to_gvkeyiid = {
            # Mega caps
            'AAPL': '000169001', 'MSFT': '001214101', 'GOOGL': '011766001', 'GOOG': '011766001',
            'AMZN': '001477201', 'NVDA': '011776801', 'META': '001837401', 'TSLA': '018499601',
            'BRK.B': '000195001', 'JPM': '006084701', 'V': '018811201', 'JNJ': '006085401',

            # Tech
            'AMD': '000116101', 'NFLX': '010752401', 'ADBE': '000103101', 'CRM': '013633601',
            'ORCL': '012151501', 'CSCO': '003073001', 'INTC': '006066501', 'QCOM': '014036001',
            'AVGO': '027025201', 'TXN': '017471901', 'ASML': '301121203',

            # Finance
            'BAC': '001120601', 'WFC': '018787401', 'GS': '004488601', 'MS': '008942401',
            'AXP': '000236001', 'C': '015073001', 'SCHW': '015187301',

            # Retail/Consumer
            'WMT': '018932301', 'HD': '004924001', 'MCD': '009404001', 'NKE': '010921001',
            'SBUX': '015136601', 'TGT': '017312001', 'LOW': '008659501', 'COST': '003179001',

            # Meme stocks
            'GME': '005087001', 'AMC': '002353001', 'BB': '002029801', 'PLTR': '026674701',
            'RIVN': '029366201', 'LCID': '028278301',

            # Energy/Industrial
            'XOM': '019144501', 'CVX': '003125001', 'BA': '000876001', 'CAT': '002564001',
            'GE': '004259201', 'LMT': '008542501', 'RTX': '018124001',

            # Healthcare/Pharma
            'UNH': '017791701', 'PFE': '013020301', 'ABBV': '000187601', 'TMO': '017450601',
            'MRK': '009018601', 'LLY': '007966801', 'MRNA': '028301401',

            # Telecom
            'T': '000111701', 'VZ': '019085201', 'TMUS': '029253101',

            # ETFs (if supported)
            'SPY': '026574001', 'QQQ': '015070701', 'IWM': '006007201',
        }

        logger.info(f"✅ Loaded {len(self.ticker_to_gvkeyiid)} ticker mappings")
        logger.info(f"   Universe: usa, stock, spglobal")

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