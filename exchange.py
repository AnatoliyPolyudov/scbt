# exchange.py
import ccxt
from config import SYMBOL, TF

# Exchange connection
ex = ccxt.okx({
    "enableRateLimit": True,
    "options": {"defaultType": "swap"}
})

def fetch_candles(limit=3):
    """Fetch candles from exchange - returns list instead of DataFrame"""
    try:
        ohlcv = ex.fetch_ohlcv(SYMBOL, TF, limit=limit)
        return ohlcv  # [[timestamp, open, high, low, close, volume], ...]
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def check_connection():
    """Check exchange connection"""
    try:
        markets = ex.load_markets()
        print("OKX exchange connected successfully")
        return True
    except Exception as e:
        print(f"Exchange connection error: {e}")
        return False