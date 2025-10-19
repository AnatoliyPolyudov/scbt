# levels_monitor.py
from exchange import ex
from config import SYMBOL
from telegram import send_telegram_message
import time

class LevelMonitor:
    def __init__(self):
        self.last_4h_high = None
        self.last_4h_low = None
        self.last_update_time = 0
        print("Level Monitor initialized")
        
    def fetch_4h_candles(self, limit=3):
        """Fetch recent 4H candles for analysis"""
        try:
            return ex.fetch_ohlcv(SYMBOL, "4h", limit=limit)
        except Exception as e:
            print(f"LevelMonitor error fetching 4h data: {e}")
            return []
        
    def update_levels(self, send_message=True):
        """Update 4H high/low levels from the last closed candle"""
        current_time = time.time()
        
        # 🔥 Обновляем уровни не чаще чем раз в 4 часа
        if current_time - self.last_update_time < 14400 and self.last_4h_high is not None:
            print(f"LevelMonitor: Levels updated recently, skipping. Next update in {14400 - (current_time - self.last_update_time):.0f} seconds")
            return False
            
        candles = self.fetch_4h_candles(limit=3)
        if len(candles) >= 2:
            last_closed = candles[-2]  # последняя закрытая свеча
            high = last_closed[2]
            low = last_closed[3]
            
            # 🔥 Отправляем сообщение ТОЛЬКО если уровни изменились И send_message=True
            if self.last_4h_high is None or high != self.last_4h_high or low != self.last_4h_low:
                self.last_4h_high = high
                self.last_4h_low = low
                self.last_update_time = current_time
                
                if send_message:
                    message = f"📊 4H Levels Updated:\n🏔️ High: {high:.2f}\n📉 Low: {low:.2f}"
                    send_telegram_message("4H_levels", "", "", "", message)
                    print(f"LevelMonitor: {message}")
                else:
                    print(f"LevelMonitor: Levels updated silently - High={high:.2f}, Low={low:.2f}")
                return True
            else:
                print(f"LevelMonitor: 4H levels unchanged - High={high:.2f}, Low={low:.2f}")
                self.last_update_time = current_time
                return False
        else:
            print("LevelMonitor: Not enough candles to determine 4H levels")
            return False
