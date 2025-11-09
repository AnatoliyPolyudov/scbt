# test_api.py
from exchange import create_exchange
ex = create_exchange()
try:
    candles = ex.fetch_ohlcv("BTC/USDT:USDT", "1m", limit=1)
    print("API работает:", candles[0] if candles else "Нет данных")
except Exception as e:
    print("Ошибка API:", e)
