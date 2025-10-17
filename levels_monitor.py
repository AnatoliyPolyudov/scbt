# levels_monitor.py
from exchange import ex
from config import SYMBOL

class LevelMonitor:
    def __init__(self):
        self.last_4h_high = None
        self.last_4h_low = None
        print("Level Monitor initialized")
        
    def fetch_4h_candles(self, limit=10):
        """Fetch 4H candles for level analysis"""
        try:
            ohlcv = ex.fetch_ohlcv(SYMBOL, "4h", limit=limit)
            return ohlcv
        except Exception as e:
            print(f"LevelMonitor error fetching 4h data: {e}")
            return []
        
    def update_levels(self):
        """Update 4H high/low levels from last 10 candles"""
        candles = self.fetch_4h_candles(limit=10)
        if len(candles) >= 2:
            highs = [c[2] for c in candles[:-1]]
            lows = [c[3] for c in candles[:-1]]
            
            self.last_4h_high = max(highs)
            self.last_4h_low = min(lows)
            print(f"4H High={self.last_4h_high:.2f}, Low={self.last_4h_low:.2f}")
