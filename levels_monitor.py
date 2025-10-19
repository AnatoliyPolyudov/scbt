# levels_monitor.py
from exchange import ex, SYMBOL
from telegram import send_telegram_message
import time

class LevelMonitor:
    def __init__(self):
        self.last_4h_high = None
        self.last_4h_low = None
        self.last_update_time = 0
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
        """Update 4H high/low levels from the last closed candle"""
        current_time = time.time()

        # Не чаще чем раз в 4 часа
        if current_time - self.last_update_time < 14400 and self.last_4h_high is not None:
            print(f"LevelMonitor: Levels updated recently, skipping. Next update in {14400 - (current_time - self.last_update_time):.0f} seconds")
            return False

        candles = self.fetch_4h_candles(limit=3)
        if len(candles) >= 2:
            last_closed = candles[-2]
            high = last_closed[2]
            low = last_closed[3]

            if self.last_4h_high is None or high != self.last_4h_high or low != self.last_4h_low:
                self.last_4h_high = high
                self.last_4h_low = low
                self.last_update_time = current_time

                if send_message:
                    message = f"Levels updated High {high:.2f}, Low {low:.2f}"
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


def monitor_levels():
    """Monitor 4H levels for breakouts"""
    monitor = LevelMonitor()
    monitor.update_levels(send_message=True)

    current_high_level = monitor.last_4h_high
    current_low_level = monitor.last_4h_low
    high_breakout_reported = False
    low_breakout_reported = False
    last_high_msg = 0
    last_low_msg = 0
    MIN_MSG_INTERVAL = 300  # 5 минут между сообщениями

    print("Level monitor started - tracking 4H breakouts")

    while True:
        try:
            current_time = time.time()
            # Обновляем уровни каждые 5 минут
            if current_time % 300 < 30:
                old_high = current_high_level
                old_low = current_low_level
                if monitor.update_levels(send_message=False):
                    current_high_level = monitor.last_4h_high
                    current_low_level = monitor.last_4h_low
                    high_breakout_reported = False
                    low_breakout_reported = False
                    print(f"Levels updated: High={current_high_level:.2f}, Low={current_low_level:.2f}")

            ticker = ex.fetch_ticker(SYMBOL)
            current_price = ticker["last"]

            # Проверка пробоя верхнего уровня
            if current_high_level and current_price > current_high_level:
                if not high_breakout_reported or (time.time() - last_high_msg > MIN_MSG_INTERVAL):
                    message = f"High break {current_high_level:.2f}"
                    send_telegram_message("", "", "", "", message)
                    print(f"LevelMonitor: {message}")
                    high_breakout_reported = True
                    last_high_msg = time.time()
                    low_breakout_reported = False

            # Проверка пробоя нижнего уровня
            elif current_low_level and current_price < current_low_level:
                if not low_breakout_reported or (time.time() - last_low_msg > MIN_MSG_INTERVAL):
                    message = f"Low break {current_low_level:.2f}"
                    send_telegram_message("", "", "", "", message)
                    print(f"LevelMonitor: {message}")
                    low_breakout_reported = True
                    last_low_msg = time.time()
                    high_breakout_reported = False

            # Сброс флагов, если цена вернулась в диапазон
            elif current_high_level and current_low_level:
                if current_low_level <= current_price <= current_high_level:
                    if high_breakout_reported or low_breakout_reported:
                        print(f"LevelMonitor: Price returned to range {current_low_level:.2f} - {current_high_level:.2f}, resetting breakout flags")
                        high_breakout_reported = False
                        low_breakout_reported = False

            time.sleep(30)

        except Exception as e:
            print(f"Level monitor error: {e}")
            time.sleep(60)
