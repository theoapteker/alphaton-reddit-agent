#!/usr/bin/env python3
"""
Full end-to-end pipeline test: Reddit → Sentiment → Alpha → FINTER
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "https://dirk-intrinsic-echoingly.ngrok-free.dev"
HEADERS = {
    "Content-Type": "application/json",
    "ngrok-skip-browser-warning": "true"
}

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_full_pipeline():
    """Test the complete Reddit → FINTER pipeline"""

    print("\n🚀 FULL PIPELINE TEST: Reddit Sentiment → Alpha Generation")
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {datetime.now().isoformat()}\n")

    # Calculate date range (last 7 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    start_str = start_date.strftime("%Y%m%d")
    end_str = end_date.strftime("%Y%m%d")

    print(f"📅 Date Range: {start_str} to {end_str}")

    # =================================================================
    # STEP 1: Scrape Reddit
    # =================================================================
    print_section("STEP 1: Scrape Reddit for Ticker Mentions")

    scrape_payload = {
        "start_date": start_str,
        "end_date": end_str,
        "subreddit": "wallstreetbets"
    }

    response = requests.post(
        f"{BASE_URL}/tools/scrape_reddit",
        json=scrape_payload,
        headers=HEADERS,
        timeout=60
    )

    if response.status_code != 200:
        print(f"❌ Scraping failed: {response.status_code}")
        print(response.text)
        return

    scrape_result = response.json()
    mentions_data = scrape_result["data"]

    print(f"✅ Scraped {scrape_result['records']} mentions")
    print(f"   Sample: {mentions_data[0]['ticker'] if mentions_data else 'None'}")

    if not mentions_data:
        print("⚠️  No mentions found. Trying with wider date range...")
        return

    # =================================================================
    # STEP 2: Analyze Sentiment
    # =================================================================
    print_section("STEP 2: Analyze Sentiment & Map to gvkeyiid")

    sentiment_payload = {
        "mentions_data": mentions_data
    }

    response = requests.post(
        f"{BASE_URL}/tools/analyze_sentiment",
        json=sentiment_payload,
        headers=HEADERS,
        timeout=60
    )

    if response.status_code != 200:
        print(f"❌ Sentiment analysis failed: {response.status_code}")
        print(response.text)
        return

    sentiment_result = response.json()
    sentiment_data = sentiment_result["data"]

    print(f"✅ Analyzed {sentiment_result['records']} records")
    print(f"   Stocks mapped: {sentiment_result['gvkeyiid_mapped']}")

    if sentiment_data:
        print(f"\n   Top 3 by sentiment:")
        sorted_sentiment = sorted(sentiment_data, key=lambda x: x['sentiment'], reverse=True)[:3]
        for s in sorted_sentiment:
            print(f"   - {s.get('ticker', 'N/A')} ({s['gvkeyiid']}): {s['sentiment']:.3f}")

    # =================================================================
    # STEP 3: Generate Alpha
    # =================================================================
    print_section("STEP 3: Generate FINTER-Compliant Alpha Positions")

    alpha_payload = {
        "sentiment_data": sentiment_data,
        "start_date": start_str,
        "end_date": end_str,
        "leverage": 1.0
    }

    response = requests.post(
        f"{BASE_URL}/tools/generate_alpha",
        json=alpha_payload,
        headers=HEADERS,
        timeout=60
    )

    if response.status_code != 200:
        print(f"❌ Alpha generation failed: {response.status_code}")
        print(response.text)
        return

    alpha_result = response.json()

    print(f"✅ Alpha generated successfully!")
    print(f"   Validation passed: {alpha_result['validation_passed']}")
    print(f"   Position shape: {alpha_result['position_shape']}")
    print(f"   Total diff: ${alpha_result['validation_details']['total_diff']:.2f}")

    # Show position preview
    position_preview = alpha_result['position_preview']
    if position_preview:
        print(f"\n   📊 Position Preview (first stock):")
        first_stock = list(position_preview.keys())[0]
        positions = position_preview[first_stock]
        print(f"   Stock: {first_stock}")
        for date, pos in list(positions.items())[:3]:
            print(f"   - {date}: ${pos:,.2f}")

    # =================================================================
    # STEP 4: Summary
    # =================================================================
    print_section("PIPELINE SUMMARY")

    print(f"✅ Total mentions scraped: {len(mentions_data)}")
    print(f"✅ Stocks with sentiment: {sentiment_result['gvkeyiid_mapped']}")
    print(f"✅ Position matrix: {alpha_result['position_shape'][0]} days × {alpha_result['position_shape'][1]} stocks")
    print(f"✅ Validation: {'PASSED ✓' if alpha_result['validation_passed'] else 'FAILED ✗'}")

    print("\n🎉 PIPELINE TEST COMPLETE!")
    print("\nNext step: Submit to FINTER for live trading")
    print(f"Command: POST {BASE_URL}/tools/submit_to_finter")

    return alpha_result

if __name__ == "__main__":
    try:
        test_full_pipeline()
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
