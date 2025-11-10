import praw
import os
from dotenv import load_dotenv

load_dotenv()

print("Testing Reddit authentication...")

try:
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD"),
        user_agent="test"
    )
    
    user = reddit.user.me()
    print(f"✅ SUCCESS: Logged in as u/{user.name}")
    
    # Test subreddit access
    sub = reddit.subreddit("wallstreetbets")
    post = next(sub.new(limit=1))
    print(f"✅ Can access r/wallstreetbets: {post.title[:50]}...")
    
except Exception as e:
    print(f"❌ FAILED: {e}")
    print("\nTROUBLESHOOTING:")
    print("1. Did you select 'script' app type?")
    print("2. Is client ID exactly 14 chars?")
    print("3. Is client secret exactly 27 chars?")
    print("4. Does username match exactly?")
    print("5. Try disabling 2FA on Reddit account")
