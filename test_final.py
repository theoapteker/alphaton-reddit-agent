import sys
sys.path.append('src')

from finter_client import finter

print("=" * 60)
print("FINTER API FINAL TEST")
print("=" * 60)

try:
    # Test 1: User info (requires item parameter)
    print("\n✅ Test 1: /user_info?item=username")
    result = finter.get_user_info("username")
    print(f"   Result: {result}")

    # Test 2: Universe (requires region, type, vendor)
    print("\n✅ Test 2: /universe/list?region=usa&type=stock&vendor=spglobal")
    universe = finter.get_universe(region="usa", type_stock="stock", vendor="spglobal")
    print(f"   Securities: {len(universe)}")
    print(f"   Columns: {universe.columns.tolist()}")
    print(f"   Sample:\n{universe.head()}")

    # Test 3: Trading days
    print("\n✅ Test 3: /trading_day")
    days = finter.get_trading_days(20240101, 20240131)
    print(f"   Trading days count: {len(days)}")
    print(f"   Date range: {days[0].strftime('%Y-%m-%d')} to {days[-1].strftime('%Y-%m-%d')}")

    print("\n" + "=" * 60)
    print("🎉 SUCCESS! All endpoints working!")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
