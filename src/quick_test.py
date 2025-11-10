#!/usr/bin/env python3
"""
Quick test to verify FINTER /id/convert with correct parameters
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("TESTING CORRECT API PARAMETERS")
print("=" * 60)

token = os.getenv("FINTER_JWT_TOKEN")
if not token:
    print("❌ Token not found")
    exit(1)

print(f"✅ Token loaded ({len(token)} chars)\n")

base_url = "https://api.finter.quantit.io"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Test with correct parameter names
print("Testing: entity_id -> short_code (should work!)")
print("-" * 60)

# Using some common gvkeyiid values
test_ids = "001690001,005764001,006768001"  # AAPL, MSFT, TSLA

params = {
    "from": "entity_id",      # Correct: entity_id (not "id")
    "to": "short_code",       # Correct: short_code (not "shortcode")
    "source": test_ids,
    "universe": 0
}

print(f"Parameters: {json.dumps(params, indent=2)}\n")

try:
    response = requests.get(
        f"{base_url}/id/convert",
        headers=headers,
        params=params,
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}\n")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ SUCCESS!\n")
        print(f"Full Response:\n{json.dumps(result, indent=2)}\n")
        
        if "code_mapped" in result:
            print("Mapped securities:")
            for gvkeyiid, ticker in result["code_mapped"].items():
                print(f"  {gvkeyiid} -> {ticker}")
            print(f"\n✅ Got {len(result['code_mapped'])} ticker mappings!")
        else:
            print("⚠️  No code_mapped in response")
    else:
        print(f"❌ FAILED!")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n" + "=" * 60)