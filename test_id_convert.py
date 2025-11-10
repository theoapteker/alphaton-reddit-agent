#!/usr/bin/env python3
"""
Diagnostic test for FINTER /id/convert endpoint
Tests ticker to gvkeyiid conversion
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("FINTER /id/convert DIAGNOSTIC TEST")
print("=" * 60)

# Get token
token = os.getenv("FINTER_JWT_TOKEN")
if not token:
    print("❌ FINTER_JWT_TOKEN not found in .env")
    exit(1)

print(f"\n✅ Token loaded ({len(token)} chars)")

# Test endpoint
base_url = "https://api.finter.quantit.io"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Test 1: Single ticker
print("\n" + "=" * 60)
print("TEST 1: Single ticker conversion (AAPL)")
print("=" * 60)

params = {
    "from": "shortcode",
    "to": "id",
    "source": "AAPL",
    "universe": 0
}

print(f"\nRequest URL: {base_url}/id/convert")
print(f"Parameters: {json.dumps(params, indent=2)}")

try:
    response = requests.get(
        f"{base_url}/id/convert",
        headers=headers,
        params=params,
        timeout=30
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ SUCCESS!")
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if "code_mapped" in result:
            print(f"\nMapped tickers:")
            for ticker, gvkeyiid in result["code_mapped"].items():
                print(f"  {ticker} -> {gvkeyiid}")
    else:
        print(f"\n❌ FAILED!")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"\n❌ Exception: {e}")

# Test 2: Multiple tickers
print("\n" + "=" * 60)
print("TEST 2: Multiple ticker conversion (AAPL,TSLA,MSFT)")
print("=" * 60)

params = {
    "from": "shortcode",
    "to": "id",
    "source": "AAPL,TSLA,MSFT",
    "universe": 0
}

print(f"\nParameters: {json.dumps(params, indent=2)}")

try:
    response = requests.get(
        f"{base_url}/id/convert",
        headers=headers,
        params=params,
        timeout=30
    )
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ SUCCESS!")
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if "code_mapped" in result:
            print(f"\nMapped tickers:")
            for ticker, gvkeyiid in result["code_mapped"].items():
                print(f"  {ticker} -> {gvkeyiid}")
    else:
        print(f"\n❌ FAILED!")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"\n❌ Exception: {e}")

# Test 3: Try different 'from' types
print("\n" + "=" * 60)
print("TEST 3: Testing different 'from' types")
print("=" * 60)

test_cases = [
    {"from": "shortcode", "to": "id", "source": "AAPL", "desc": "shortcode -> id"},
    {"from": "entity_name", "to": "id", "source": "APPLE INC", "desc": "entity_name -> id"},
]

for test in test_cases:
    print(f"\nTesting: {test['desc']}")
    print(f"  Params: {test}")
    
    try:
        response = requests.get(
            f"{base_url}/id/convert",
            headers=headers,
            params={k: v for k, v in test.items() if k != "desc"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if "code_mapped" in result and result["code_mapped"]:
                print(f"  ✅ Success: {result['code_mapped']}")
            else:
                print(f"  ⚠️  Empty result: {result}")
        else:
            print(f"  ❌ Failed ({response.status_code}): {response.text[:100]}")
    except Exception as e:
        print(f"  ❌ Exception: {e}")

print("\n" + "=" * 60)
print("DIAGNOSTIC TEST COMPLETE")
print("=" * 60)