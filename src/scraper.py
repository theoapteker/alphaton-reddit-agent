import praw
import pandas as pd
from datetime import datetime, timedelta
import re
import os
import logging

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class RedditScraper:
    def __init__(self):
        """Initialize Reddit API connection"""
        logger.info("📡 Connecting to Reddit API...")
        
        try:
            self.reddit = praw.Reddit(
                client_id=os.getenv("REDDIT_CLIENT_ID"),
                client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                username=os.getenv("REDDIT_USERNAME"),
                password=os.getenv("REDDIT_PASSWORD"),
                user_agent="AlphatonSentimentAgent/1.0"
            )
            
            # Test connection
            user = self.reddit.user.me()
            logger.info(f"✅ Reddit authentication successful: u/{user.name}")
            
            # Initialize subreddit
            self.subreddit = self.reddit.subreddit("wallstreetbets")
            
        except Exception as e:
            logger.error(f"❌ Reddit auth failed: {str(e)}")
            raise
    
    def scrape_date_range(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Scrape ALL posts from r/wallstreetbets for a date range
        Args:
            start_date: datetime object
            end_date: datetime object
        Returns:
            DataFrame with [post_id, title, text, score, created_utc]
        """
        logger.info(f"📡 Scraping Reddit from {start_date.date()} to {end_date.date()}...")
        
        all_posts = []
        current_date = start_date
        
        while current_date <= end_date:
            logger.info(f"   Processing {current_date.date()}...")
            
            # Calculate timestamps for this day
            start_ts = int(current_date.replace(hour=0, minute=0, second=0).timestamp())
            end_ts = int(current_date.replace(hour=23, minute=59, second=59).timestamp())
            
            # Scrape posts
            day_posts = []
            try:
                for post in self.subreddit.new(limit=500):
                    if start_ts <= post.created_utc <= end_ts:
                        day_posts.append({
                            'post_id': post.id,
                            'title': post.title,
                            'text': post.selftext or "",
                            'score': post.score,
                            'num_comments': post.num_comments,
                            'created_utc': datetime.fromtimestamp(post.created_utc)
                        })
                
                all_posts.extend(day_posts)
                logger.info(f"      Found {len(day_posts)} posts")
                
            except Exception as e:
                logger.warning(f"⚠️  Failed to scrape {current_date.date()}: {e}")
            
            current_date += timedelta(days=1)
        
        df = pd.DataFrame(all_posts)
        logger.info(f"✅ Total posts scraped: {len(df)}")
        
        return df
    
    def extract_ticker_mentions(self, posts_df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract stock tickers from post titles and text
        Pattern: $TICKER (e.g., $AAPL, $TSLA, $NVDA)
        Returns DataFrame with [ticker, date, score, text, post_id]
        """
        logger.info("🔍 Extracting ticker mentions...")
        
        if posts_df.empty:
            logger.warning("⚠️  No posts to extract from!")
            return pd.DataFrame(columns=['ticker', 'date', 'score', 'text', 'post_id'])
        
        # Regex pattern to match $TICKER format (2-5 uppercase letters)
        ticker_pattern = r'\$([A-Z]{2,5})\b'
        
        mentions = []
        
        for _, row in posts_df.iterrows():
            # Combine title and text
            combined_text = f"{row['title']} {row['text']}"
            
            # Find all ticker mentions in the text
            found_tickers = set(re.findall(ticker_pattern, combined_text))
            
            # Create a record for each unique ticker in this post
            for ticker in found_tickers:
                mentions.append({
                    'ticker': ticker,
                    'date': row['created_utc'].date(),
                    'score': row['score'],
                    'text': combined_text[:500],  # First 500 chars for sentiment analysis
                    'post_id': row['post_id'],
                    'num_comments': row['num_comments']
                })
        
        mentions_df = pd.DataFrame(mentions)
        
        if not mentions_df.empty:
            logger.info(f"✅ Extracted {len(mentions_df)} ticker mentions")
            
            # Show top 5 most mentioned tickers
            top_tickers = mentions_df['ticker'].value_counts().head()
            logger.info(f"📈 Top tickers:\n{top_tickers}")
        else:
            logger.warning("⚠️  No ticker mentions found!")
        
        return mentions_df

# Test the scraper
# Test the scraper
if __name__ == "__main__":
    import sys
    
    # CRITICAL: Load environment variables BEFORE creating scraper
    from dotenv import load_dotenv
    load_dotenv()
    
    print("=" * 60)
    print("TESTING REDDIT SCRAPER")
    print("=" * 60)
    
    # Debug: Print if variables are loaded
    print(f"REDDIT_CLIENT_ID loaded: {'YES' if os.getenv('REDDIT_CLIENT_ID') else 'NO'}")
    print(f"REDDIT_USERNAME loaded: {'YES' if os.getenv('REDDIT_USERNAME') else 'NO'}")
    print()
    
    try:
        scraper = RedditScraper()
        
        # Test: Scrape last 3 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=3)
        
        posts = scraper.scrape_date_range(start_date, end_date)
        mentions = scraper.extract_ticker_mentions(posts)
        
        print("\n" + "=" * 60)
        print(f"✅ SCRAPER TEST PASSED!")
        print(f"   Posts scraped: {len(posts)}")
        print(f"   Ticker mentions: {len(mentions)}")
        
    except Exception as e:
        print(f"\n❌ SCRAPER TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)