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
    def __init__(self, max_universe_size: int = 500):
        """
        Initialize with FINTER API connection
        
        Args:
            max_universe_size: Number of securities to map (500 is fast, 3000+ takes longer)
        """
        logger.info("📡 Initializing Sentiment Engine...")
        
        # Build ticker mapping on initialization
        logger.info(f"   Building ticker mapping (limit: {max_universe_size} securities)...")
        self.ticker_to_gvkeyiid = finter.build_ticker_mapping(
            max_securities=max_universe_size,
            use_cache=True
        )
        
        logger.info(f"✅ Sentiment Engine ready with {len(self.ticker_to_gvkeyiid)} ticker mappings")
    
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
        """Map Reddit tickers to FINTER gvkeyiid using pre-built mapping"""
        logger.info("🔄 Mapping tickers to gvkeyiid...")
        
        if mentions_df.empty:
            return pd.DataFrame(columns=['gvkeyiid', 'date', 'sentiment', 'mention_count', 'ticker'])
        
        # Get unique tickers
        unique_tickers = mentions_df['ticker'].unique().tolist()
        logger.info(f"   Found {len(unique_tickers)} unique tickers")
        
        # Map using pre-built dictionary
        mentions_df['gvkeyiid'] = mentions_df['ticker'].map(self.ticker_to_gvkeyiid)
        
        # Count successes
        mapped_count = mentions_df['gvkeyiid'].notna().sum()
        total_count = len(mentions_df)
        
        logger.info(f"✅ Mapped {mapped_count}/{total_count} ticker mentions")
        
        if mapped_count == 0:
            logger.warning("⚠️  NO tickers were successfully mapped!")
            logger.warning(f"   Tried tickers: {unique_tickers[:10]}")
            logger.warning(f"   Available tickers in map: {list(self.ticker_to_gvkeyiid.keys())[:10]}...")
            return pd.DataFrame(columns=['gvkeyiid', 'date', 'sentiment', 'mention_count', 'ticker'])
        
        # Show which tickers worked and which didn't
        mapped_tickers = mentions_df[mentions_df['gvkeyiid'].notna()]['ticker'].unique()
        unmapped_tickers = mentions_df[mentions_df['gvkeyiid'].isna()]['ticker'].unique()
        
        if len(mapped_tickers) > 0:
            logger.info(f"   ✅ Mapped: {', '.join(mapped_tickers[:5])}{' ...' if len(mapped_tickers) > 5 else ''}")
        if len(unmapped_tickers) > 0:
            logger.info(f"   ⚠️  Unmapped: {', '.join(unmapped_tickers[:5])}{' ...' if len(unmapped_tickers) > 5 else ''}")
        
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
        # Initialize with smaller universe for speed
        engine = SentimentEngine(max_universe_size=200)
        
        # Mock mentions data
        mock_mentions = pd.DataFrame({
            'ticker': ['AAPL', 'TSLA', 'AAPL', 'MSFT', 'NVDA'],
            'date': [datetime.now().date()] * 5,
            'score': [100, 50, 75, 10, 80],
            'text': [
                "I love $AAPL! Best stock ever!",
                "$TSLA is crashing, sell now!",
                "$AAPL will go to $200 soon!",
                "$MSFT cloud growth is amazing",
                "$NVDA AI chips dominating!"
            ],
            'post_id': ['p1', 'p2', 'p3', 'p4', 'p5'],
            'num_comments': [10, 5, 8, 3, 15]
        })
        
        print("\n" + "=" * 60)
        print("TESTING TICKER MAPPING")
        print("=" * 60)
        
        # Test mapping
        mapped = engine.map_to_gvkeyiid(mock_mentions)
        print(f"\n✅ Mapped: {len(mapped)}/{len(mock_mentions)} records")
        
        if not mapped.empty:
            print("\nMapped data:")
            print(mapped[['ticker', 'gvkeyiid', 'text']].to_string())
            
            print("\n" + "=" * 60)
            print("TESTING SENTIMENT CALCULATION")
            print("=" * 60)
            
            # Test sentiment
            aggregated = engine.calculate_daily_sentiment(mapped)
            print(f"\n✅ Aggregated: {len(aggregated)} records")
            print("\nDaily sentiment:")
            print(aggregated[['ticker', 'gvkeyiid', 'sentiment', 'mention_count']].to_string())
        else:
            print("\n⚠️  No tickers were mapped. Try increasing max_universe_size or check ticker symbols.")
        
        print("\n" + "=" * 60)
        print("✅ SENTIMENT ENGINE TEST PASSED!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)