# levels_monitor.py
from exchange import ex
from config import SYMBOL

class LevelMonitor:
    def __init__(self):
        self.last_4h_high = None
        self.last_4h_low = None
        print("Level Monitor initialized")
        
    def fetch_4h_candles(self, limit=5):
        """Fetch recent 4H candles for analysis"""
        try:
            ohlcv = ex.fetch_ohlcv(SYMBOL, "4h", limit=limit)
            return ohlcv
        except Exception as e:
            print(f"LevelMonitor error fetching 4h data: {e}")
            return []
        
    def update_levels(self):
        """Update high/low from the last closed 4H candle"""
        candles = self.fetch_4h_candles(limit=3)
        if len(candles) >= 2:
            last_closed = candles[-2]  # последняя закрытая свеча
            self.last_4h_high = last_closed[2]
            self.last_4h_low = last_closed[3]
            print(f"4H closed candle → High={self.last_4h_high:.2f}, Low={self.last_4h_low:.2f}")
        else:
            print("Not enough candles to determine 4H levels")
