# exchange.py
import ccxt
import pandas as pd
from config import SYMBOL, TF

# Exchange connection
ex = ccxt.okx({
    "enableRateLimit": True,
    "options": {"defaultType": "swap"}
})

def fetch_candles(limit=3):
    """Fetch candles from exchange"""
    try:
        ohlcv = ex.fetch_ohlcv(SYMBOL, TF, limit=limit)
        df = pd.DataFrame(ohlcv, columns=["ts","open","high","low","close","volume"])
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()

def check_connection():
    """Check exchange connection"""
    try:
        markets = ex.load_markets()
        print("OKX exchange connected successfully")
        return True
    except Exception as e:
        print(f"Exchange connection error: {e}")
        return False
