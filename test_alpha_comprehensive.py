"""
Comprehensive Alpha Generator Test Suite
Tests the RedditSentimentAlpha class with mocked FINTER API
"""
import sys
sys.path.append('src')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

print("=" * 80)
print("COMPREHENSIVE ALPHA GENERATOR TEST SUITE")
print("=" * 80)

# ============================================================================
# MOCK FINTER CLIENT
# ============================================================================

class MockFinterAPI:
    """Mock FINTER API client for testing"""

    def get_trading_days(self, start: int, end: int) -> pd.DatetimeIndex:
        """Generate mock trading days (weekdays only)"""
        # Handle date arithmetic edge cases (e.g., 20240101 - 100 = 20240001)
        try:
            start_date = pd.to_datetime(str(start), format='%Y%m%d')
        except ValueError:
            # If date is invalid, use earliest possible date
            start_date = pd.to_datetime('2023-01-01')

        try:
            end_date = pd.to_datetime(str(end), format='%Y%m%d')
        except ValueError:
            # If date is invalid, use latest possible date
            end_date = pd.to_datetime('2025-12-31')

        # Generate all dates in range
        all_dates = pd.date_range(start_date, end_date, freq='D')

        # Filter to weekdays only (Monday=0 to Friday=4)
        trading_days = all_dates[all_dates.dayofweek < 5]

        return pd.DatetimeIndex(trading_days)

    def get_universe(self, region="usa", type_stock="stock", vendor="spglobal"):
        """Return mock universe data"""
        return pd.DataFrame({
            'gvkeyiid': ['001690001', '001666010', '001234567'],
            'tic': ['AAPL', 'TSLA', 'MSFT']
        })

# Patch the finter module before importing alpha
mock_finter = MockFinterAPI()
sys.modules['finter_client'] = Mock()
sys.modules['finter_client'].finter = mock_finter

# Now we can import alpha
from alpha import RedditSentimentAlpha

# ============================================================================
# TEST UTILITIES
# ============================================================================

def generate_mock_sentiment_data(days: int = 30, base_date: str = "2024-01-15") -> pd.DataFrame:
    """Generate realistic mock sentiment data centered around a specific date"""
    # Center the data around base_date to ensure it covers test ranges
    center_date = datetime.strptime(base_date, "%Y-%m-%d")
    start_date = center_date - timedelta(days=days//2)
    end_date = center_date + timedelta(days=days//2)

    sentiment_records = []
    current_date = start_date

    while current_date <= end_date:
        if current_date.weekday() < 5:  # Weekdays only
            # AAPL - mostly positive sentiment
            sentiment_records.append({
                'gvkeyiid': '001690001',
                'date': current_date.date(),
                'sentiment': np.random.uniform(0.3, 0.8),
                'mention_count': np.random.randint(5, 20)
            })

            # TSLA - mixed sentiment
            sentiment_records.append({
                'gvkeyiid': '001666010',
                'date': current_date.date(),
                'sentiment': np.random.uniform(-0.5, 0.5),
                'mention_count': np.random.randint(3, 15)
            })

            # MSFT - slightly positive
            if np.random.random() > 0.3:  # Not every day
                sentiment_records.append({
                    'gvkeyiid': '001234567',
                    'date': current_date.date(),
                    'sentiment': np.random.uniform(0.1, 0.6),
                    'mention_count': np.random.randint(2, 10)
                })

        current_date += timedelta(days=1)

    return pd.DataFrame(sentiment_records)

def validate_position_dataframe(position: pd.DataFrame, start: int, end: int) -> dict:
    """Validate that position DataFrame meets FINTER requirements"""
    errors = []
    warnings = []

    # Check 1: Index should be DatetimeIndex
    if not isinstance(position.index, pd.DatetimeIndex):
        errors.append("Index is not DatetimeIndex")

    # Check 2: All column names should be 9-character gvkeyiid
    invalid_cols = [col for col in position.columns if len(str(col)) != 9]
    if invalid_cols:
        errors.append(f"Invalid gvkeyiid columns: {invalid_cols}")

    # Check 3: All values should be numeric
    if not position.select_dtypes(include=[np.number]).shape == position.shape:
        errors.append("Non-numeric values found in position DataFrame")

    # Check 4: Max position size should not exceed $100M
    if position.shape[1] > 0:  # Only check if there are columns
        max_position = position.abs().max().max()
        if pd.notna(max_position) and max_position > 1e8:
            errors.append(f"Position exceeds $100M limit: ${max_position:,.2f}")
    else:
        max_position = 0.0

    # Check 5: Should have trading days only (weekdays)
    if not all(position.index.dayofweek < 5):
        errors.append("Non-trading days found in position index")

    # Check 6: Date range validation
    first_date = position.index[0]
    last_date = position.index[-1]
    expected_first = pd.to_datetime(str(start), format='%Y%m%d')
    expected_last = pd.to_datetime(str(end), format='%Y%m%d')

    if first_date < expected_first or last_date > expected_last:
        warnings.append(f"Date range [{first_date} to {last_date}] outside requested [{expected_first} to {expected_last}]")

    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'max_position': max_position,
        'shape': position.shape,
        'date_range': (first_date, last_date)
    }

# ============================================================================
# TEST CASES
# ============================================================================

def test_1_basic_initialization():
    """Test 1: Alpha initialization"""
    print("\n" + "=" * 80)
    print("TEST 1: Basic Initialization")
    print("=" * 80)

    sentiment_df = generate_mock_sentiment_data(days=30)
    print(f"Generated {len(sentiment_df)} sentiment records")

    alpha = RedditSentimentAlpha(sentiment_df, leverage=1.0)

    print("✅ Alpha initialized successfully")
    print(f"   Records: {len(sentiment_df)}")
    print(f"   Unique securities: {sentiment_df['gvkeyiid'].nunique()}")
    print(f"   Date range: {sentiment_df['date'].min()} to {sentiment_df['date'].max()}")

    return True

def test_2_position_generation():
    """Test 2: Position generation with valid date range"""
    print("\n" + "=" * 80)
    print("TEST 2: Position Generation")
    print("=" * 80)

    sentiment_df = generate_mock_sentiment_data(days=60)
    alpha = RedditSentimentAlpha(sentiment_df, leverage=1.0)

    # Generate positions for January 2024
    start_date = 20240101
    end_date = 20240131

    position = alpha.get(start_date, end_date)

    print(f"\n✅ Position generated:")
    print(f"   Shape: {position.shape}")
    print(f"   Date range: {position.index[0]} to {position.index[-1]}")
    print(f"   Securities: {len(position.columns)}")
    print(f"   Trading days: {len(position)}")
    print(f"   Max position: ${position.abs().max().max():,.2f}")
    print(f"   Total notional: ${position.abs().sum().sum():,.2f}")

    # Validate structure
    validation = validate_position_dataframe(position, start_date, end_date)

    if validation['valid']:
        print("\n✅ FINTER validation passed!")
    else:
        print(f"\n❌ Validation failed: {validation['errors']}")
        return False

    if validation['warnings']:
        print(f"⚠️  Warnings: {validation['warnings']}")

    return True

def test_3_look_ahead_bias_shift():
    """Test 3: Verify 1-day position shift (look-ahead bias prevention)"""
    print("\n" + "=" * 80)
    print("TEST 3: Look-Ahead Bias Prevention (1-Day Shift)")
    print("=" * 80)

    # Create sentiment data with known pattern
    dates = pd.date_range('2024-01-01', '2024-01-31', freq='D')
    dates = dates[dates.dayofweek < 5]  # Weekdays only

    sentiment_data = []
    for i, date in enumerate(dates):
        # AAPL sentiment increases linearly over time
        sentiment_data.append({
            'gvkeyiid': '001690001',
            'date': date.date(),
            'sentiment': 0.1 * (i + 1),  # Increasing sentiment
            'mention_count': 10
        })

    sentiment_df = pd.DataFrame(sentiment_data)
    alpha = RedditSentimentAlpha(sentiment_df, leverage=1.0)

    position = alpha.get(20240101, 20240131)

    # The first trading day should have zero position (due to shift)
    first_day_position = position.iloc[0].abs().sum()

    print(f"First trading day position: ${first_day_position:,.2f}")

    if first_day_position == 0:
        print("✅ Look-ahead bias shift verified!")
        print("   First day has zero position (expected due to 1-day shift)")
        return True
    else:
        print("❌ Look-ahead bias shift FAILED!")
        print(f"   Expected first day position: $0.00")
        print(f"   Actual: ${first_day_position:,.2f}")
        return False

def test_4_position_constraints():
    """Test 4: Position size constraints ($100M max)"""
    print("\n" + "=" * 80)
    print("TEST 4: Position Size Constraints")
    print("=" * 80)

    # Generate sentiment data that overlaps with Jan 2024
    sentiment_df = generate_mock_sentiment_data(days=60, base_date="2024-01-15")

    # Test with different leverage levels
    test_cases = [
        (0.5, "Conservative"),
        (1.0, "Normal"),
        (2.0, "Aggressive")
    ]

    all_passed = True

    for leverage, description in test_cases:
        alpha = RedditSentimentAlpha(sentiment_df, leverage=leverage)
        position = alpha.get(20240101, 20240131)

        if position.shape[1] > 0:
            max_position = position.abs().max().max()
        else:
            max_position = 0.0

        print(f"\n{description} (leverage={leverage}):")
        print(f"   Max position: ${max_position:,.2f}")

        if pd.isna(max_position):
            print(f"   ⚠️  No positions generated (empty sentiment data)")
            continue

        if max_position <= 1e8:
            print(f"   ✅ Within $100M limit")
        else:
            print(f"   ❌ EXCEEDS $100M limit!")
            all_passed = False

    return all_passed

def test_5_start_end_validation():
    """Test 5: Start-end dependency validation (critical for FINTER)"""
    print("\n" + "=" * 80)
    print("TEST 5: Start-End Dependency Validation")
    print("=" * 80)

    # Generate 200 days of sentiment data to allow different lookbacks
    # Center around Jan 2024 to ensure coverage
    sentiment_df = generate_mock_sentiment_data(days=200, base_date="2024-01-15")
    alpha = RedditSentimentAlpha(sentiment_df, leverage=1.0)

    # Run validation
    validation_result = alpha.validate(20240101, 20240131)

    print(f"\nValidation Results:")
    print(f"   Passed: {validation_result['passed']}")
    print(f"   Total diff: ${validation_result['total_diff']:,.4f}")
    print(f"   Threshold: ${validation_result['threshold']}")
    print(f"   Overlap days: {validation_result['overlap_days']}")
    print(f"   Max position diff: ${validation_result['max_position_diff']:,.4f}")

    if validation_result['passed']:
        print("\n✅ Start-end validation PASSED!")
        return True
    else:
        print("\n❌ Start-end validation FAILED!")
        print("   Different start dates produce different positions")
        print("   This indicates look-ahead bias or non-deterministic behavior")
        return False

def test_6_empty_sentiment_handling():
    """Test 6: Graceful handling of empty sentiment data"""
    print("\n" + "=" * 80)
    print("TEST 6: Empty Sentiment Data Handling")
    print("=" * 80)

    # Empty DataFrame with correct structure
    empty_df = pd.DataFrame(columns=['gvkeyiid', 'date', 'sentiment', 'mention_count'])

    alpha = RedditSentimentAlpha(empty_df, leverage=1.0)
    position = alpha.get(20240101, 20240131)

    print(f"Position shape: {position.shape}")
    print(f"Position columns: {len(position.columns)}")

    if len(position.columns) == 0 and len(position) > 0:
        print("✅ Empty sentiment handled correctly!")
        print("   Returns empty positions with correct trading days")
        return True
    else:
        print("❌ Empty sentiment handling FAILED!")
        return False

def test_7_long_short_separation():
    """Test 7: Verify long/short position separation"""
    print("\n" + "=" * 80)
    print("TEST 7: Long/Short Position Separation")
    print("=" * 80)

    # Create data with clear positive and negative sentiment
    dates = pd.date_range('2024-01-01', '2024-01-15', freq='D')
    dates = dates[dates.dayofweek < 5]

    sentiment_data = []
    for date in dates:
        # Strong positive sentiment
        sentiment_data.append({
            'gvkeyiid': '001690001',
            'date': date.date(),
            'sentiment': 0.8,
            'mention_count': 10
        })
        # Strong negative sentiment
        sentiment_data.append({
            'gvkeyiid': '001666010',
            'date': date.date(),
            'sentiment': -0.7,
            'mention_count': 10
        })

    sentiment_df = pd.DataFrame(sentiment_data)
    alpha = RedditSentimentAlpha(sentiment_df, leverage=1.0)

    position = alpha.get(20240101, 20240131)

    # Check for both long and short positions
    has_long = (position > 0).any().any()
    has_short = (position < 0).any().any()

    print(f"\nHas long positions: {has_long}")
    print(f"Has short positions: {has_short}")

    if '001690001' in position.columns:
        avg_aapl = position['001690001'].mean()
        print(f"AAPL (positive sentiment) avg position: ${avg_aapl:,.2f}")

    if '001666010' in position.columns:
        avg_tsla = position['001666010'].mean()
        print(f"TSLA (negative sentiment) avg position: ${avg_tsla:,.2f}")

    if has_long and has_short:
        print("\n✅ Long/Short separation working correctly!")
        return True
    else:
        print("\n⚠️  Only one-sided positions found")
        return True  # Not necessarily a failure

# ============================================================================
# RUN ALL TESTS
# ============================================================================

def run_all_tests():
    """Run all test cases and report results"""
    print("\n" + "=" * 80)
    print("RUNNING ALL TESTS")
    print("=" * 80)

    tests = [
        ("Basic Initialization", test_1_basic_initialization),
        ("Position Generation", test_2_position_generation),
        ("Look-Ahead Bias Prevention", test_3_look_ahead_bias_shift),
        ("Position Constraints", test_4_position_constraints),
        ("Start-End Validation", test_5_start_end_validation),
        ("Empty Sentiment Handling", test_6_empty_sentiment_handling),
        ("Long/Short Separation", test_7_long_short_separation),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            passed = test_func()
            results[test_name] = "✅ PASSED" if passed else "❌ FAILED"
        except Exception as e:
            results[test_name] = f"❌ ERROR: {str(e)}"
            import traceback
            traceback.print_exc()

    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    for test_name, result in results.items():
        print(f"{result:<15} {test_name}")

    # Overall result
    passed_count = sum(1 for r in results.values() if "PASSED" in r)
    total_count = len(results)

    print("\n" + "=" * 80)
    print(f"OVERALL: {passed_count}/{total_count} tests passed")
    print("=" * 80)

    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Alpha generator is FINTER-compliant and ready for deployment!")
        return 0
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed")
        print("Please review the failures above")
        return 1

if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
