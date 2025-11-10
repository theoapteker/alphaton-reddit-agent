import sys
sys.path.append('src')

from finter_client import finter

print("=" * 50)
print("TESTING FINTER API CONNECTION")
print("=" * 50)

try:
    # Test 1: User info
    print("\n1. Testing /user_info endpoint...")
    user_info = finter.get("/user_info")
    print(f"✅ SUCCESS: Hello, {user_info['name']}! ({user_info['email']})")
    
    # Test 2: Trading days
    print("\n2. Testing /trading_day endpoint...")
    trading_days = finter.get_trading_days(20240101, 20240131)
    print(f"✅ SUCCESS: Found {len(trading_days)} trading days")
    print(f"   Dates: {trading_days[0].strftime('%Y-%m-%d')} to {trading_days[-1].strftime('%Y-%m-%d')}")
    
    # Test 3: Universe
    print("\n3. Testing /universe/list endpoint...")
    universe = finter.get_stock_universe()
    print(f"✅ SUCCESS: Loaded {len(universe)} securities")
    print(f"   Sample: {universe[['tic', 'gvkeyiid']].head(3).to_string()}")
    
    print("\n" + "=" * 50)
    print("ALL TESTS PASSED! ✅")
    print("Your JWT token is working correctly.")
    print("=" * 50)
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    print("\nTROUBLESHOOTING:")
    print("1. Check your .env file contains the full JWT token")
    print("2. Ensure token is on one line after FINTER_JWT_TOKEN=")
    print("3. Verify token hasn't expired (Expires 2025-12-09)")
    print("4. Check you're connected to internet")
    sys.exit(1)
