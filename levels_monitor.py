# levels_monitor.py
from exchange import ex, SYMBOL
from telegram import send_telegram_message
import time

class LevelMonitor:
    def __init__(self):
        self.last_4h_high = None
        self.last_4h_low = None
        self.last_closed_ts = None
        print("Level Monitor initialized")

    def fetch_4h_candles(self, limit=10):
        """Fetch recent 4H candles from exchange"""
        try:
            return ex.fetch_ohlcv(SYMBOL, "4h", limit=limit)
        except Exception as e:
            print(f"LevelMonitor error fetching 4h data: {e}")
            return []

    def update_levels(self, send_message=True):
        """Update levels based on last fully closed 4H candle"""
        candles = self.fetch_4h_candles(limit=10)
        if not candles:
            print("LevelMonitor: No candles fetched")
            return

        # Берём последнюю полностью закрытую свечу
        # timestamp каждой свечи возвращается в мс
        current_ts = int(time.time() * 1000)
        last_closed = None
        for candle in reversed(candles):
            ts_open = candle[0]
            ts_close = ts_open + 4 * 60 * 60 * 1000  # 4h в мс
            if ts_close <= current_ts:
                last_closed = candle
                break

        if last_closed is None:
            print("LevelMonitor: No fully closed 4H candle yet")
            return

        high = last_closed[2]
        low = last_closed[3]
        ts_close = last_closed[0] + 4*60*60*1000

        # Проверяем, обновились ли уровни
        if self.last_closed_ts != ts_close or self.last_4h_high != high or self.last_4h_low != low:
            self.last_4h_high = high
            self.last_4h_low = low
            self.last_closed_ts = ts_close
            if send_message:
                message = f"4H Levels Updated:\nHigh: {high:.2f}\nLow: {low:.2f}"
                send_telegram_message("4H_levels", "", "", "", message)
                print(f"LevelMonitor: {message}")
        else:
            print(f"LevelMonitor: Levels unchanged - High={high:.2f}, Low={low:.2f}")
