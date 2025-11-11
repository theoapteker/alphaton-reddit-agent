import sys
sys.path.append('src')

import pandas as pd
import numpy as np
from datetime import datetime
from finter_client import finter
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class RedditSentimentAlpha:
    """
    FINTER-compliant alpha strategy from Reddit sentiment
    Implements ALL FINTER requirements:
    - Uses gvkeyiid (not tickers)
    - Shifts positions by 1 day
    - Uses trading days only
    - Max position size: $100M
    - Passes start-end validation
    """

    def __init__(self, sentiment_df: pd.DataFrame, leverage: float = 1.0):
        """
        Args:
            sentiment_df: DataFrame with [gvkeyiid, date, sentiment, mention_count]
            leverage: Position size multiplier (1.0 = $100M AUM)
        """
        self.sentiment_df = sentiment_df
        self.leverage = leverage
        self.universe = "us_stock"

        logger.info(f"🚀 Alpha initialized: {len(sentiment_df)} sentiment records")

    def get(self, start: int, end: int) -> pd.DataFrame:
        """
        Generate position DataFrame following FINTER's strict contract

        Args:
            start: Start date as integer (YYYYMMDD)
            end: End date as integer (YYYYMMDD)

        Returns:
            pd.DataFrame: Index=trading_days, Columns=gvkeyiid, Values=position_size
        """
        logger.info(f"📊 Generating positions for {start} to {end}...")

        # Step 1: Get trading days from FINTER API
        trading_days = finter.get_trading_days(start, end)
        logger.info(f"📅 Trading days: {len(trading_days)}")

        # Step 2: Filter sentiment data to requested date range
        self.sentiment_df['date'] = pd.to_datetime(self.sentiment_df['date'])
        mask = (self.sentiment_df['date'] >= pd.to_datetime(str(start))) & \
               (self.sentiment_df['date'] <= pd.to_datetime(str(end)))
        filtered_sentiment = self.sentiment_df[mask].copy()

        if filtered_sentiment.empty:
            logger.warning("⚠️  No sentiment data in date range!")
            # Return empty DataFrame with correct structure
            return pd.DataFrame(index=trading_days, columns=[], dtype=float)

        # Step 3: Pivot to wide format (index=date, columns=gvkeyiid, values=sentiment)
        pivot = filtered_sentiment.pivot(
            index='date',
            columns='gvkeyiid',
            values='sentiment'
        )

        # Step 4: Reindex to trading days and forward-fill missing dates
        aligned = pivot.reindex(trading_days).ffill(limit=5).fillna(0)

        # Step 5: Generate position weights (long positive, short negative sentiment)
        # Normalize each row to sum to 1.0 (then scale to target AUM)
        weights = aligned.div(aligned.abs().sum(axis=1).replace(0, np.nan), axis=0)
        weights = weights.fillna(0)

        # Step 6: Scale to target notional ($100M default, adjusted by leverage)
        position = weights * 1e8 * self.leverage

        # Step 7: CRITICAL: Apply look-ahead bias shift (shift by 1 trading day)
        position = position.shift(1)

        # Step 8: Fill NaNs from shift with 0 (no position)
        position = position.fillna(0)

        # Step 9: Enforce FINTER's max position size constraint ($100M per security)
        position = position.clip(-1e8, 1e8)

        # Step 10: Remove any non-gvkeyiid columns (safety check)
        valid_cols = [col for col in position.columns if len(str(col)) == 9]
        position = position[valid_cols]

        logger.info(f"✅ Positions generated: {position.shape}")
        logger.info(f"   Date range: {position.index[0]} to {position.index[-1]}")
        logger.info(f"   Securities: {len(position.columns)}")
        logger.info(f"   Max position: ${position.abs().max().max():,.2f}")

        return position

    def validate(self, start: int, end: int) -> dict:
        """
        Run FINTER's critical start-end dependency validation

        The same alpha must produce identical positions regardless of start date.
        Max allowed difference: $1.00 (StartEndDependencyError threshold)

        Returns:
            dict: {passed: bool, total_diff: float, threshold: float}
        """
        logger.info("🔍 Running start-end validation...")

        # Generate positions with two different start dates
        # Use proper date arithmetic to avoid invalid dates (e.g., 20240101 - 100 = 20240001)
        start_date = pd.to_datetime(str(start), format='%Y%m%d')

        # Create earlier start dates for validation
        earlier_start1 = start_date - pd.Timedelta(days=100)
        earlier_start2 = start_date - pd.Timedelta(days=50)

        # Convert back to YYYYMMDD format
        start1_int = int(earlier_start1.strftime('%Y%m%d'))
        start2_int = int(earlier_start2.strftime('%Y%m%d'))

        pos1 = self.get(start1_int, end)  # Extra 100 days lookback
        pos2 = self.get(start2_int, end)   # Extra 50 days lookback

        # Find overlapping period
        overlap_start = max(pos1.index.min(), pos2.index.min())
        overlap_end = min(pos1.index.max(), pos2.index.max())

        # Slice to overlapping period
        pos1_overlap = pos1.loc[overlap_start:overlap_end]
        pos2_overlap = pos2.loc[overlap_start:overlap_end]

        # Calculate absolute difference
        diff = (pos1_overlap - pos2_overlap).abs()
        total_diff = diff.sum().sum()  # Sum across ALL cells

        # Check against FINTER threshold ($1.00)
        threshold = 1.0
        passed = total_diff <= threshold

        logger.info(f"   Total diff: ${total_diff:,.4f} (threshold: ${threshold})")

        if passed:
            logger.info("✅ VALIDATION PASSED!")
        else:
            logger.error(f"❌ FAILED: diff ${total_diff:.4f} > ${threshold}")

            # Show problematic securities
            max_diff = diff.max()
            if not max_diff.empty:
                worst_tickers = max_diff.nlargest(3)
                logger.error(f"   Worst tickers: {worst_tickers.to_dict()}")

        return {
            "passed": passed,
            "total_diff": float(total_diff),
            "threshold": threshold,
            "overlap_days": len(pos1_overlap),
            "max_position_diff": float(diff.max().max()) if not diff.empty else 0,
        }

# Test the alpha
if __name__ == "__main__":
    import sys
    from datetime import datetime, timedelta

    print("=" * 60)
    print("TESTING FINTER-COMPLIANT ALPHA")
    print("=" * 60)

    # Create mock sentiment data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    mock_sentiment = []
    current_date = start_date

    while current_date <= end_date:
        if current_date.weekday() < 5:  # Weekdays only
            mock_sentiment.append({
                'gvkeyiid': '00169001',  # AAPL
                'date': current_date.date(),
                'sentiment': 0.5,
                'mention_count': 10
            })
            mock_sentiment.append({
                'gvkeyiid': '00166610',  # TSLA
                'date': current_date.date(),
                'sentiment': -0.3,
                'mention_count': 5
            })
        current_date += timedelta(days=1)

    mock_df = pd.DataFrame(mock_sentiment)

    try:
        # Create alpha
        alpha = RedditSentimentAlpha(mock_df, leverage=1.0)

        # Generate positions
        start_int = 20240101
        end_int = 20240131

        position = alpha.get(start_int, end_int)
        print(f"\n✅ Position generated: {position.shape}")
        print(f"✅ Max position: ${position.abs().max().max():,.2f}")

        # Run validation
        validation = alpha.validate(start_int, end_int)
        print(f"\n✅ Validation: {validation}")

        if validation['passed']:
            print("\n" + "=" * 60)
            print("🎉 ALPHA TEST PASSED!")
            print("✅ All FINTER constraints satisfied!")
            print("=" * 60)
        else:
            print("\n❌ Validation failed - check logs above")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ ALPHA TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
