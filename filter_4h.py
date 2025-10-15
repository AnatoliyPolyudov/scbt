# filter_4h.py
import time
from datetime import datetime
from exchange import fetch_candles
from telegram import send_telegram_message
from config import SYMBOL

class FourHourFilter:
    def __init__(self):
        self.active_direction = None  # None, "LONG", "SHORT"
        self.range_high = 0
        self.range_low = 0
        self.last_status_time = 0
        
    def send_4h_status(self, direction, action):
        """Send 4H filter status to Telegram"""
        message = f"""4H {action}
{direction} | Range: {self.range_high:.2f}-{self.range_low:.2f}
1m monitoring {action}"""
        send_telegram_message("4h_filter", "", "", "", message)
        
    def get_4h_range(self):
        """Get range from previous closed 4H candle"""
        pass
        
    def check_breakout(self):
        """Check for 4H breakout and update activation status"""
        pass
        
    def is_active(self):
        """Check if 1m monitoring should be active"""
        pass
        
    def print_status(self, force=False):
        """Print status every hour or when forced"""
        pass

# Global instance
filter_4h = FourHourFilter()

def get_4h_range(self):
        """Get range from previous closed 4H candle"""
        try:
            # Получаем 2 последние 4H свечи
            df = fetch_candles(symbol=SYMBOL, timeframe="4h", limit=2)
            if len(df) < 2:
                print("[4H FILTER] Not enough 4H candles")
                return False
                
            # Предыдущая закрытая свеча (самая старая из двух)
            prev_candle = df.iloc[0]  # индекс 0 - самая старая
            self.range_high = prev_candle["high"]
            self.range_low = prev_candle["low"]
            
            print(f"[4H FILTER] Range updated: H:{self.range_high:.2f} L:{self.range_low:.2f}")
            return True
            
        except Exception as e:
            print(f"[4H FILTER] Error getting 4H range: {e}")
            return False