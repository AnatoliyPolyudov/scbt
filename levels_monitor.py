# levels_monitor.py
import ccxt
import asyncio
import time
from datetime import datetime
from exchange import ex, SYMBOL
from telegram import send_telegram_message

class LevelMonitor:
    def __init__(self):
        self.last_4h_high = None
        self.last_4h_low = None
        self.last_candle_timestamp = None
        self.levels_sent = False
        self.last_update_time = 0
        print("Level Monitor initialized - 4H levels will be sent on new candle close")

    def update_levels(self, send_message=True):
        """Совместимость со старым кодом - отправляет уровни при первом вызове"""
        current_time = time.time()
        
        # Если уровни еще не отправлялись, отправляем их
        if not self.levels_sent:
            candles = ex.fetch_ohlcv(SYMBOL, "4h", limit=3)
            if len(candles) >= 2:
                previous_closed_candle = candles[-2]
                self.calculate_and_send_levels_sync(previous_closed_candle)
                return True
        return False

    def calculate_and_send_levels_sync(self, closed_candle):
        """Синхронная версия для совместимости"""
        try:
            # closed_candle = [timestamp, open, high, low, close, volume]
            timestamp, open_price, high, low, close, volume = closed_candle
            
            # Сохраняем High/Low для мониторинга пробоев
            self.last_4h_high = high
            self.last_4h_low = low
            
            # Расчет дополнительных уровней поддержки/сопротивления
            levels = self.calculate_support_resistance(high, low, close)
            
            # Форматируем и отправляем сообщение
            message = self.format_levels_message(levels, timestamp)
            send_telegram_message("4H_levels", "", "", "", message)
            
            self.levels_sent = True
            self.last_update_time = time.time()
            print(f"✅ 4H уровни отправлены по закрытой свече")
            
        except Exception as e:
            print(f"❌ Ошибка расчета уровней: {e}")

    def calculate_support_resistance(self, high, low, close):
        """Расчет уровней поддержки и сопротивления"""
        # Pivot Points классические
        pivot = (high + low + close) / 3
        r1 = (2 * pivot) - low
        s1 = (2 * pivot) - high
        r2 = pivot + (high - low)
        s2 = pivot - (high - low)
        
        # Дополнительные уровни
        resistance_levels = [
            round(r1, 2),
            round(r2, 2),
            round(high, 2)  # предыдущий максимум
        ]
        
        support_levels = [
            round(s1, 2),
            round(s2, 2), 
            round(low, 2)   # предыдущий минимум
        ]
        
        # Убираем дубликаты и сортируем
        resistance_levels = sorted(list(set(resistance_levels)))
        support_levels = sorted(list(set(support_levels)))
        
        return {
            'support': support_levels,
            'resistance': resistance_levels,
            'pivot': round(pivot, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'timestamp': datetime.now()
        }

    def format_levels_message(self, levels, candle_timestamp):
        """Форматирует сообщение с уровнями"""
        candle_time = datetime.fromtimestamp(candle_timestamp/1000).strftime('%H:%M %d.%m')
        
        supports = ", ".join([f"`{s}`" for s in levels['support']])
        resistances = ", ".join([f"`{r}`" for r in levels['resistance']])
        
        return f"""
📊 **4H Уровни {SYMBOL}** ({candle_time})

🛟 **Поддержка:** {supports}
🎯 **Сопротивление:** {resistances}  
⚖️ **Pivot:** `{levels['pivot']}`
📈 **High:** `{levels['high']}`
📉 **Low:** `{levels['low']}`

_Обновлено: {datetime.now().strftime('%H:%M:%S')}_
"""

def monitor_levels():
    """Мониторинг 4H уровней для пробоев (совместимость с текущим кодом)"""
    monitor = LevelMonitor()
    
    # Первоначальная отправка уровней
    monitor.update_levels(send_message=True)

    current_high_level = monitor.last_4h_high
    current_low_level = monitor.last_4h_low
    high_breakout_reported = False
    low_breakout_reported = False
    last_high_msg = 0
    last_low_msg = 0
    MIN_MSG_INTERVAL = 300  # 5 минут

    print("Level monitor started - tracking 4H breakouts")

    while True:
        try:
            current_time = time.time()
            
            # Проверяем новую свечу каждую минуту
            candles = ex.fetch_ohlcv(SYMBOL, "4h", limit=3)
            if len(candles) >= 2:
                latest_candle = candles[-1]
                previous_closed_candle = candles[-2]
                
                candle_timestamp = latest_candle[0]
                
                # Если появилась новая свеча
                if candle_timestamp != monitor.last_candle_timestamp:
                    print(f"🕯️ Новая 4H свеча: {datetime.fromtimestamp(candle_timestamp/1000)}")
                    monitor.last_candle_timestamp = candle_timestamp
                    
                    # Обновляем уровни по новой свече
                    monitor.calculate_and_send_levels_sync(previous_closed_candle)
                    current_high_level = monitor.last_4h_high
                    current_low_level = monitor.last_4h_low
                    high_breakout_reported = False
                    low_breakout_reported = False

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
                    message = f"Low break: {current_low_level:.2f}"
                    send_telegram_message("", "", "", "", message)
                    print(f"LevelMonitor: {message}")
                    low_breakout_reported = True
                    last_low_msg = time.time()
                    high_breakout_reported = False

            # Сброс флагов при возврате цены в диапазон
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
