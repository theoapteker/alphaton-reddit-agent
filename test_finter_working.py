import sys
sys.path.append('src')

from finter_client import finter

print("=" * 60)
print("TESTING FINTER API (WORKING ENDPOINTS)")
print("=" * 60)

try:
    # Test 1: User info WITH required parameter
    print("\n[TEST 1] /user_info?item=username")
    result = finter.get_user_info("username")
    print(f"✅ Result: {result}")

    # Test 2: Universe
    print("\n[TEST 2] /universe/list")
    universe = finter.get_stock_universe()
    print(f"✅ {len(universe)} securities")

    # Test 3: Trading days
    print("\n[TEST 3] /trading_day")
    days = finter.get_trading_days(20240101, 20240131)
    print(f"✅ {len(days)} trading days")

    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    exit(1)
