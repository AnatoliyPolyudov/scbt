# exchange.py
import ccxt
from config import SYMBOL, TF, OKX_API_KEY, OKX_SECRET_KEY, OKX_PASSPHRASE

def create_exchange():
    """Создает и возвращает объект биржи"""
    return ccxt.okx({
        "apiKey": OKX_API_KEY,
        "secret": OKX_SECRET_KEY,
        "password": OKX_PASSPHRASE,
        "enableRateLimit": True,
        "options": {"defaultType": "swap"}
    })

def fetch_candles(limit=3):
    """Fetch candles from exchange - returns list instead of DataFrame"""
    try:
        ex = create_exchange()  # создаем объект при каждом вызове
        ohlcv = ex.fetch_ohlcv(SYMBOL, TF, limit=limit)
        return ohlcv  # [[timestamp, open, high, low, close, volume], ...]
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def check_connection():
    """Check exchange connection"""
    try:
        ex = create_exchange()  # создаем объект при каждом вызове
        markets = ex.load_markets()
        print("OKX exchange connected successfully")
        return True
    except Exception as e:
        print(f"Exchange connection error: {e}")
        return False

def place_order(action, price, amount=0.001):
    """
    Реальная постановка ордера.
    action: 'BUY' или 'SELL'
    price: цена ордера
    amount: кол-во (по умолчанию 0.001)
    """
    try:
        ex = create_exchange()  # создаем объект при каждом вызове
        side = "buy" if action.upper() == "BUY" else "sell"
        order = ex.create_limit_order(SYMBOL, side, amount, price)
        print(f"Order placed: {order}")
        return order
    except Exception as e:
        print(f"Order error: {e}")
        return None