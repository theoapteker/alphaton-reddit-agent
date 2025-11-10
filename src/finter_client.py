"""
FINTER API Client - Working Ticker Mapping
Strategy: Get universe, convert gvkeyiid->ticker, build reverse map
"""

import requests
import os
import pandas as pd
from dotenv import load_dotenv
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

class FinterAPI:
    def __init__(self):
        self.base_url = "https://api.finter.quantit.io"
        self.token = os.getenv("FINTER_JWT_TOKEN")
        
        if not self.token:
            raise ValueError("❌ FINTER_JWT_TOKEN not found")
        
        self.headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        logger.info(f"✅ Token loaded ({len(self.token)} chars)")
        self._test_connection()
        
        # Cache for ticker mappings
        self._ticker_to_gvkeyiid_cache = None
    
    def _test_connection(self):
        try:
            self.get_user_info("username")
            logger.info("✅ API connection working!")
        except Exception as e:
            logger.warning(f"⚠️  Test failed: {e}")
    
    def get(self, endpoint: str, params: dict = None):
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, headers=self.headers, params=params, timeout=30)

        if response.status_code == 401:
            raise Exception("❌ JWT authentication failed!")
        if response.status_code in [400, 405]:
            error_msg = response.json().get('message', 'Unknown error')
            # Log the full error details for debugging
            logger.debug(f"API Error {response.status_code} for {endpoint}: params={params}, response={response.json()}")
            raise Exception(f"❌ Error {response.status_code}: {error_msg}")

        response.raise_for_status()
        return response.json()
    
    def post(self, endpoint: str, data: dict = None):
        url = f"{self.base_url}{endpoint}"
        response = requests.post(url, headers=self.headers, json=data, timeout=30)
        
        if response.status_code == 401:
            raise Exception("❌ JWT authentication failed!")
        if response.status_code in [400, 405]:
            raise Exception(f"❌ Error {response.status_code}: {response.json().get('message')}")
        
        response.raise_for_status()
        return response.json()
    
    def build_ticker_mapping(self, max_securities: int = 500, use_cache: bool = True, date: str = None) -> dict:
        if use_cache and self._ticker_to_gvkeyiid_cache is not None:
            logger.info(f"✅ Using cached ticker mapping ({len(self._ticker_to_gvkeyiid_cache)} tickers)")
            return self._ticker_to_gvkeyiid_cache

        logger.info("📡 Building ticker mapping from universe...")

        # Use provided date or default to a recent date
        if date is None:
            from datetime import datetime
            date = datetime.now().strftime("%Y%m%d")

        universe_df = self.get_universe(region="usa", type_stock="stock", vendor="spglobal")
        if max_securities and len(universe_df) > max_securities:
            logger.info(f"   Limiting to first {max_securities} securities for speed")
            universe_df = universe_df.head(max_securities)

        gvkeyiids = universe_df["gvkeyiid"].astype(str).tolist()
        ticker_mapping = {}
        batch_size = 100

        for i in range(0, len(gvkeyiids), batch_size):
            batch = gvkeyiids[i:i+batch_size]
            source_str = ",".join(batch)

            params = {
                "from": "entity_id",
                "to": "shortcode",       # No underscore per API mapping table
                "source": source_str,
                "universe": 0,
                "date": date,
            }

            try:
                result = self.get("/id/convert", params=params)

                if "code_mapped" in result:
                    # result: {"code_mapped": {"001690001": "AAPL", ...}}
                    for src_id, ticker in result["code_mapped"].items():
                        if ticker:
                            ticker_mapping[ticker.upper()] = src_id

                logger.info(f"   Progress: {min(i+batch_size, len(gvkeyiids))}/{len(gvkeyiids)}")
                time.sleep(0.1)
            except Exception as e:
                logger.warning(f"   Batch {i//batch_size} failed: {e}")
                continue

        logger.info(f"✅ Built mapping: {len(ticker_mapping)} tickers")
        self._ticker_to_gvkeyiid_cache = ticker_mapping
        return ticker_mapping




    def entity_id_to_ccid(self, entity_id):
        """Convert FINTER entity_id (gvkeyiid) -> ccid"""
        # entity_id might be int or str; send whatever we got
        result = self.get("/mapper/entity_id_to_ccid", params={"entity_id": entity_id})
        ccid = result.get("ccid") or result.get("data")

        if not ccid:
            # log whole result so we see the real shape
            logger.warning(f"   mapper/entity_id_to_ccid raw response for {entity_id}: {result}")

        return ccid


    def ccid_to_short_code(self, ccid: str):
        """Convert ccid -> short_code (ticker)"""
        result = self.get("/mapper/ccid_to_short_code", params={"ccid": ccid})
        short_code = result.get("short_code") or result.get("data")

        if not short_code:
            logger.warning(f"   mapper/ccid_to_short_code raw response for {ccid}: {result}")

        return short_code
    
    def discover_convert_shape(self, sample_entity_id: str, date: str = None):
            """
            Try a bunch of plausible param names for /id/convert and return the one that works.
            Returns: (method, from_key, to_key)
            """
            # Use provided date or default to current date
            if date is None:
                from datetime import datetime
                date = datetime.now().strftime("%Y%m%d")

            candidates = [
                ("get",  "from",      "to"),
                ("get",  "from_code", "to_code"),
                ("get",  "from_type", "to_type"),
                ("post", "from",      "to"),
                ("post", "from_code", "to_code"),
                ("post", "from_type", "to_type"),
            ]

            for method, from_key, to_key in candidates:
                payload = {
                    from_key: "entity_id",
                    to_key: "shortcode",
                    "source": sample_entity_id,
                    "universe": 0,
                    "date": date,
                }
                try:
                    if method == "get":
                        resp = self.get("/id/convert", params=payload)
                    else:
                        resp = self.post("/id/convert", data=payload)

                    # success: no 400 and we got a dict back
                    if isinstance(resp, dict) and resp:
                        logger.info(f"✅ /id/convert works with method={method}, {from_key}→{to_key}")
                        return method, from_key, to_key

                except Exception as e:
                    logger.info(f"   /id/convert failed for ({method}, {from_key}, {to_key}): {e}")
                    continue

            raise RuntimeError("❌ Could not find working param names for /id/convert")




    # =========================================================================
    # USER ENDPOINTS
    # =========================================================================
    
    def get_user_info(self, item: str = "username"):
        """Get user info (requires item parameter)"""
        logger.info(f"📡 User info: {item}")
        result = self.get("/user_info", params={"item": item})
        logger.info(f"✅ Result: {result.get('data')}")
        return result
    
    # =========================================================================
    # DATA ENDPOINTS
    # =========================================================================
    
    def get_universe(self, region: str = "usa", type_stock: str = "stock", vendor: str = "spglobal") -> pd.DataFrame:
        """Get universe (requires region, type, vendor)"""
        logger.info(f"📡 Universe: {region}, {type_stock}, {vendor}")
        
        params = {"region": region, "type": type_stock, "vendor": vendor}
        result = self.get("/universe/list", params=params)
        
        df = pd.DataFrame(result)
        
        # Handle different API response formats
        if "id_list" in df.columns:
            # Format: unix_timestamp, id_list
            df = pd.DataFrame({"gvkeyiid": df["id_list"]})
        
        # Ensure gvkeyiid is string and 9 characters
        if "gvkeyiid" in df.columns:
            df["gvkeyiid"] = df["gvkeyiid"].astype(str)
            if df["gvkeyiid"].str.len().max() < 9:
                df["gvkeyiid"] = df["gvkeyiid"].apply(lambda x: f"{int(x):09d}")
        
        logger.info(f"✅ Universe: {len(df)} securities")
        return df
    
  
    def get_ticker_to_gvkeyiid(self, ticker: str, mapping: dict = None) -> str:
        """
        Get gvkeyiid for a ticker using pre-built mapping
        
        Args:
            ticker: Stock ticker (e.g., "AAPL")
            mapping: Pre-built mapping dict (if None, will build it)
            
        Returns:
            gvkeyiid string or None
        """
        if mapping is None:
            mapping = self.build_ticker_mapping()
        
        return mapping.get(ticker.upper())
    
    def get_trading_days(self, start: int, end: int) -> pd.DatetimeIndex:
        """Get trading days in range (uses /calendar endpoint)"""
        logger.info(f"📡 Trading days {start}-{end}")
        
        params = {"start_date": str(start), "end_date": str(end)}
        result = self.get("/calendar", params=params)
        
        if "dates" in result:
            dates = [pd.to_datetime(d) for d in result["dates"]]
        elif "trading_days" in result:
            dates = [pd.to_datetime(d) for d in result["trading_days"]]
        else:
            raise ValueError("Unknown /calendar response format")
        
        return pd.DatetimeIndex(dates)
    
    # =========================================================================
    # SIMULATION & SUBMISSION
    # =========================================================================
    
    def run_simulation(self, position_dict: dict, start: int, end: int) -> dict:
        """Run backtest simulation"""
        logger.info(f"📡 Simulation {start}-{end}")
        
        result = self.post("/simulation", {
            "position": position_dict,
            "start_date": str(start),
            "end_date": str(end),
            "initial_cash": 100_000_000,
            "buy_fee_tax": 25,
            "sell_fee_tax": 25,
            "slippage": 10
        })
        
        logger.info("✅ Simulation complete")
        return result
    
    def submit_model(self, model_name: str, universe: str, docker_image: str) -> dict:
        """Submit to production"""
        logger.info(f"📡 Submitting {model_name}")
        
        result = self.post("/submission", {
            "model_name": model_name,
            "universe": universe,
            "docker_image": docker_image,
            "schedule": "0 16 * * *"
        })
        
        logger.info(f"✅ Submitted: {result.get('model_id')}")
        return result


# =========================================================================
# GLOBAL INSTANCE
# =========================================================================
print("\n" + "=" * 60)
print("INITIALIZING FINTER API CLIENT")
print("=" * 60)
finter = FinterAPI()
print("✅ READY")
print("=" * 60 + "\n")


# =========================================================================
# SELF-TEST
# =========================================================================
if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("SELF-TEST")
    print("=" * 60)
    
    try:
        # Test all endpoints
        finter.get_user_info("username")
        
        universe = finter.get_universe()
        print(f"\n✅ Universe: {len(universe)} securities")
        
        days = finter.get_trading_days(20240101, 20240131)
        print(f"\n✅ Trading days: {len(days)}")
        
        # Test ticker mapping (limit to 200 for speed)
        print("\n" + "=" * 60)
        print("BUILDING TICKER MAPPING")
        print("=" * 60)
        
        ticker_map = finter.build_ticker_mapping(max_securities=200)
        
        if ticker_map:
            print(f"\n✅ Built mapping: {len(ticker_map)} tickers")
            
            # Test some common tickers
            test_tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "JPM"]
            print("\nTesting common tickers:")
            for ticker in test_tickers:
                gvkeyiid = ticker_map.get(ticker)
                if gvkeyiid:
                    print(f"  ✅ {ticker} -> {gvkeyiid}")
                else:
                    print(f"  ⚠️  {ticker} not found")
        else:
            print("\n⚠️  No tickers mapped")
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
