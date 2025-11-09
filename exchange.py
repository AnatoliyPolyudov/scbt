# exchange.py
import ccxt
from config import SYMBOL, TF, OKX_API_KEY, OKX_SECRET_KEY, OKX_PASSPHRASE

# Глобальный экземпляр биржи
_exchange_instance = None

def create_exchange():
    """Создает и возвращает объект биржи"""
    if not all([OKX_API_KEY, OKX_SECRET_KEY, OKX_PASSPHRASE]):
        raise Exception("Отсутствуют учетные данные для OKX. Проверьте файл .env")
    
    return ccxt.okx({
        "apiKey": OKX_API_KEY,
        "secret": OKX_SECRET_KEY,
        "password": OKX_PASSPHRASE,
        "enableRateLimit": True,
        "options": {"defaultType": "swap"}
    })

def get_exchange():
    """Возвращает глобальный экземпляр биржи (один на весь бот)"""
    global _exchange_instance
    if _exchange_instance is None:
        _exchange_instance = create_exchange()
        print("OKX exchange instance created")
    return _exchange_instance

def fetch_candles(limit=3):
    """Fetch candles from exchange - returns list instead of DataFrame"""
    try:
        ex = get_exchange()  # ✅ Используем глобальный экземпляр
        ohlcv = ex.fetch_ohlcv(SYMBOL, TF, limit=limit)
        return ohlcv
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def check_connection():
    """Check exchange connection"""
    try:
        ex = get_exchange()  # ✅ Используем глобальный экземпляр
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
        ex = get_exchange()  # ✅ Используем глобальный экземпляр
        side = "buy" if action.upper() == "BUY" else "sell"
        order = ex.create_limit_order(SYMBOL, side, amount, price)
        print(f"Order placed: {order}")
        return order
    except Exception as e:
        print(f"Order error: {e}")
        return None
