"""
MCP Server for Reddit Sentiment Agent
Exposes 4 tools:
1. scrape_reddit - Scrape posts for date range
2. analyze_sentiment - Map tickers and calculate sentiment
3. generate_alpha - Create FINTER-compliant positions
4. submit_to_finter - Deploy to production
"""

import sys
sys.path.append('src')

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import logging
import json
import pandas as pd
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Reddit Sentiment MCP Server",
    description="AI Agent for Quantitative Finance Sentiment Analysis",
    version="1.0.0"
)

# Lazy-loaded instances (initialized on first use to avoid requiring credentials at startup)
_scraper = None
_sentiment_engine = None
_finter = None

def get_scraper():
    """Lazy load RedditScraper"""
    global _scraper
    if _scraper is None:
        from scraper import RedditScraper
        _scraper = RedditScraper()
    return _scraper

def get_sentiment_engine():
    """Lazy load SentimentEngine"""
    global _sentiment_engine
    if _sentiment_engine is None:
        from sentiment import SentimentEngine
        _sentiment_engine = SentimentEngine()
    return _sentiment_engine

def get_finter():
    """Lazy load FinterAPI"""
    global _finter
    if _finter is None:
        from finter_client import finter
        _finter = finter
    return _finter

# =========================================================================
# REQUEST/RESPONSE MODELS
# =========================================================================

class ScrapeRequest(BaseModel):
    start_date: str  # YYYYMMDD format
    end_date: str    # YYYYMMDD format
    subreddit: str = "wallstreetbets"

class SentimentRequest(BaseModel):
    mentions_data: List[Dict]  # Raw mentions from scraper

class AlphaRequest(BaseModel):
    sentiment_data: List[Dict]  # Mapped sentiment data
    start_date: str
    end_date: str
    leverage: float = 1.0

class SubmitRequest(BaseModel):
    position_json: str  # JSON string of position DataFrame
    model_name: str
    universe: str = "us_stock"

# =========================================================================
# MCP TOOLS
# =========================================================================

@app.get("/health")
def health_check():
    """Health check endpoint for n8n"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "reddit_connected": True,
        "finter_connected": True
    }

@app.post("/tools/scrape_reddit", tags=["MCP Tools"])
def scrape_reddit_endpoint(request: ScrapeRequest):
    """
    TOOL 1: Scrape Reddit for ticker mentions

    Input:
    - start_date: "20240101"
    - end_date: "20240131"

    Output:
    - List of posts with ticker mentions
    """
    logger.info(f"🔧 TOOL: scrape_reddit ({request.start_date} to {request.end_date})")

    try:
        scraper = get_scraper()

        # Parse dates
        start = datetime.strptime(request.start_date, "%Y%m%d")
        end = datetime.strptime(request.end_date, "%Y%m%d")

        # Scrape posts
        posts = scraper.scrape_date_range(start, end)

        # Extract mentions
        mentions = scraper.extract_ticker_mentions(posts)

        # Convert to dict format
        result = {
            "status": "success",
            "records": len(mentions),
            "date_range": f"{request.start_date} to {request.end_date}",
            "subreddit": request.subreddit,
            "data": mentions.to_dict("records") if not mentions.empty else []
        }

        logger.info(f"✅ Scraped {result['records']} mentions")
        return result

    except Exception as e:
        logger.error(f"❌ Scraper failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/analyze_sentiment", tags=["MCP Tools"])
def analyze_sentiment_endpoint(request: SentimentRequest):
    """
    TOOL 2: Analyze sentiment and map to gvkeyiid

    Input:
    - mentions_data: List of {ticker, date, score, text}

    Output:
    - Mapped sentiment data with gvkeyiid
    """
    logger.info(f"🔧 TOOL: analyze_sentiment ({len(request.mentions_data)} records)")

    try:
        if not request.mentions_data:
            return {"status": "success", "records": 0, "data": []}

        sentiment_engine = get_sentiment_engine()

        # Convert to DataFrame
        mentions_df = pd.DataFrame(request.mentions_data)

        # Map to gvkeyiid
        mapped = sentiment_engine.map_to_gvkeyiid(mentions_df)

        # Calculate sentiment
        sentiment = sentiment_engine.calculate_daily_sentiment(mapped)

        result = {
            "status": "success",
            "records": len(sentiment),
            "gvkeyiid_mapped": len(sentiment['gvkeyiid'].unique()),
            "data": sentiment.to_dict("records")
        }

        logger.info(f"✅ Sentiment calculated for {result['records']} records")
        return result

    except Exception as e:
        logger.error(f"❌ Sentiment analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/generate_alpha", tags=["MCP Tools"])
def generate_alpha_endpoint(request: AlphaRequest):
    """
    TOOL 3: Generate FINTER-compliant alpha positions

    Input:
    - sentiment_data: List of {gvkeyiid, date, sentiment, mention_count}
    - start_date, end_date: "20240101"
    - leverage: float (default 1.0)

    Output:
    - Position DataFrame (JSON format)
    - Validation results
    """
    logger.info(f"🔧 TOOL: generate_alpha ({request.start_date} to {request.end_date})")

    try:
        if not request.sentiment_data:
            raise HTTPException(status_code=400, detail="No sentiment data provided")

        from alpha import RedditSentimentAlpha

        # Convert to DataFrame
        sentiment_df = pd.DataFrame(request.sentiment_data)

        # Create alpha
        alpha = RedditSentimentAlpha(sentiment_df, request.leverage)

        # Generate positions
        position = alpha.get(
            int(request.start_date),
            int(request.end_date)
        )

        # Run validation
        validation = alpha.validate(
            int(request.start_date),
            int(request.end_date)
        )

        # Convert position to JSON for MCP transport
        position_json = position.to_json(orient="split", date_format="iso")

        result = {
            "status": "success",
            "validation_passed": validation["passed"],
            "validation_details": validation,
            "position_shape": list(position.shape),  # Convert tuple to list for JSON
            "position_preview": position.head().to_dict(),
            "position_json": position_json
        }

        logger.info(f"✅ Alpha generated: {position.shape}, validation: {validation['passed']}")
        return result

    except Exception as e:
        logger.error(f"❌ Alpha generation failed: {e}")
        import traceback
        traceback.print_exc()  # Print full traceback for debugging
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/submit_to_finter", tags=["MCP Tools"])
def submit_to_finter_endpoint(request: SubmitRequest):
    """
    TOOL 4: Submit alpha to FINTER production

    Input:
    - position_json: JSON string of position DataFrame
    - model_name: "reddit_sentiment_v1"
    - universe: "us_stock"

    Output:
    - Submission confirmation
    """
    logger.info(f"🔧 TOOL: submit_to_finter ({request.model_name})")

    try:
        finter = get_finter()

        # Parse position from JSON
        position = pd.read_json(request.position_json, orient='split')

        # Submit to FINTER
        result = finter.submit_model(
            model_name=request.model_name,
            universe=request.universe,
            docker_image="public.ecr.aws/d2s6t0y4/reddit-agent:v1"
        )

        submission_result = {
            "status": "submitted",
            "model_id": result.get("model_id"),
            "model_name": request.model_name,
            "validation_url": result.get("validation_url"),
            "position_preview": position.head().to_dict()
        }

        logger.info(f"✅ Submitted: {result.get('model_id')}")
        return submission_result

    except Exception as e:
        logger.error(f"❌ Submission failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =========================================================================
# MCP DISCOVERY ENDPOINT
# =========================================================================

@app.get("/mcp/tools", tags=["MCP Discovery"])
def list_tools():
    """List all available MCP tools for n8n"""
    return {
        "tools": [
            {
                "name": "scrape_reddit",
                "description": "Scrape Reddit r/wallstreetbets for ticker mentions",
                "input_schema": {
                    "start_date": "YYYYMMDD",
                    "end_date": "YYYYMMDD"
                }
            },
            {
                "name": "analyze_sentiment",
                "description": "Analyze sentiment and map to FINTER gvkeyiid",
                "input_schema": {
                    "mentions_data": "list of mentions"
                }
            },
            {
                "name": "generate_alpha",
                "description": "Generate FINTER-compliant alpha positions",
                "input_schema": {
                    "sentiment_data": "list of sentiment records",
                    "start_date": "YYYYMMDD",
                    "end_date": "YYYYMMDD"
                }
            },
            {
                "name": "submit_to_finter",
                "description": "Submit alpha to FINTER production",
                "input_schema": {
                    "position_json": "JSON string of position DataFrame",
                    "model_name": "string"
                }
            }
        ]
    }

# =========================================================================
# MAIN
# =========================================================================

if __name__ == "__main__":
    import uvicorn

    print("\n" + "=" * 60)
    print("STARTING MCP SERVER")
    print("=" * 60)
    print("📡 Server: http://localhost:8000")
    print("📡 Docs:   http://localhost:8000/docs")
    print("📡 Health: http://localhost:8000/health")
    print("=" * 60 + "\n")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
