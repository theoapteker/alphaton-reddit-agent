#!/usr/bin/env python3
"""
Quick test script for n8n MCP Server endpoints
"""

import requests
import json
from datetime import datetime

# Your ngrok URL
BASE_URL = "https://dirk-intrinsic-echoingly.ngrok-free.dev"

def test_generate_alpha():
    """Test the generate_alpha endpoint with mock data"""

    print("\n" + "=" * 60)
    print("TEST: Generate Alpha Endpoint")
    print("=" * 60)

    # Mock sentiment data (using 2025 dates to match request)
    payload = {
        "sentiment_data": [
            {
                "gvkeyiid": "000169001",
                "date": "2025-11-10",
                "sentiment": 0.625,
                "mention_count": 1
            },
            {
                "gvkeyiid": "001214101",
                "date": "2025-11-09",
                "sentiment": 0.0,
                "mention_count": 1
            },
            {
                "gvkeyiid": "011776801",
                "date": "2025-11-10",
                "sentiment": 0.3,
                "mention_count": 1
            },
            {
                "gvkeyiid": "018499601",
                "date": "2025-11-10",
                "sentiment": -0.2,
                "mention_count": 1
            }
        ],
        "start_date": "20251104",
        "end_date": "20251111",
        "leverage": 1.0
    }

    headers = {
        "Content-Type": "application/json",
        "ngrok-skip-browser-warning": "true"
    }

    print(f"\nSending request to {BASE_URL}/tools/generate_alpha")
    print(f"Sentiment records: {len(payload['sentiment_data'])}")

    try:
        response = requests.post(
            f"{BASE_URL}/tools/generate_alpha",
            json=payload,
            headers=headers,
            timeout=30
        )

        print(f"\nStatus Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("\n✅ SUCCESS! Endpoint returned JSON response")
            print(f"\nResponse:")
            print(json.dumps(result, indent=2))

            print(f"\n📊 Summary:")
            print(f"  - Validation passed: {result.get('validation_passed')}")
            print(f"  - Position shape: {result.get('position_shape')}")
            print(f"  - Total diff: ${result.get('validation_details', {}).get('total_diff', 0):.2f}")

        else:
            print(f"\n❌ FAILED with status {response.status_code}")
            print(f"Response text: {response.text}")

    except requests.exceptions.JSONDecodeError as e:
        print(f"\n❌ JSON Decode Error (the bug we're fixing!): {e}")
        print(f"Response text: {response.text}")
        print(f"Response status: {response.status_code}")

    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    print("\n🚀 Testing n8n MCP Server Endpoints")
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {datetime.now().isoformat()}")

    test_generate_alpha()

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60 + "\n")
