# main.py
import order_manager
import time
import threading
import gc
import requests
import json
from exchange import check_connection, ex
from patterns import check_scob_pattern, wait_for_candle_close
from telegram import send_startup_message, send_telegram_message, send_error_message
from callback_handler import handle_callback
from config import TELEGRAM_BOT_TOKEN, SYMBOL
from levels_monitor import LevelMonitor

def get_updates(offset=None):
    """Get updates from Telegram via polling"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    params = {'timeout': 30, 'offset': offset}
    try:
        response = requests.get(url, params=params, timeout=35)
        return response.json()
    except:
        return {'result': []}

def process_updates():
    """Process Telegram updates in background"""
    last_update_id = None
    print("Starting Telegram updates polling...")
    
    while True:
        try:
            updates = get_updates(last_update_id)
            if updates.get('result'):
                for update in updates['result']:
                    if 'callback_query' in update:
                        callback_data = update['callback_query']['data']
                        print(f"Received callback: {callback_data}")
                        handle_callback(callback_data)
                    
                    last_update_id = update['update_id'] + 1
            
            time.sleep(1)
        except Exception as e:
            print(f"Updates error: {e}")
            time.sleep(5)

def monitor_levels():
    """Monitor 4H levels for breakouts"""
    monitor = LevelMonitor()
    monitor.update_levels(send_message=True)
    
    # 🔥 Улучшенная логика отслеживания пробоев
    current_high_level = monitor.last_4h_high
    current_low_level = monitor.last_4h_low
    high_breakout_reported = False
    low_breakout_reported = False
    
    print("Level monitor started - tracking 4H breakouts")
    
    while True:
        try:
            # Обновляем уровни каждые 5 минут для актуальности
            current_time = time.time()
            if current_time % 300 < 30:  # Каждые 5 минут
                old_high = current_high_level
                old_low = current_low_level
                monitor.update_levels(send_message=False)
                current_high_level = monitor.last_4h_high
                current_low_level = monitor.last_4h_low
                
                # 🔥 Если уровни изменились - сбрасываем флаги пробоев
                if current_high_level != old_high or current_low_level != old_low:
                    print(f"Levels updated - resetting breakout flags. New levels: H={current_high_level:.2f}, L={current_low_level:.2f}")
                    high_breakout_reported = False
                    low_breakout_reported = False
            
            # Проверяем пробои каждые 30 секунд
            ticker = ex.fetch_ticker(SYMBOL)
            current_price = ticker["last"]
            
            # 🔥 Логика пробоя верхнего уровня
            if current_high_level and current_price > current_high_level:
                if not high_breakout_reported:
                    message = f"🚀 BREAKOUT UP: Price {current_price:.2f} > 4H High {current_high_level:.2f}"
                    send_telegram_message("", "", "", "", message)
                    print(f"LevelMonitor: {message}")
                    high_breakout_reported = True
                    # При пробое вверх сбрасываем флаг пробоя вниз
                    low_breakout_reported = False
            
            # 🔥 Логика пробоя нижнего уровня
            elif current_low_level and current_price < current_low_level:
                if not low_breakout_reported:
                    message = f"📉 BREAKOUT DOWN: Price {current_price:.2f} < 4H Low {current_low_level:.2f}"
                    send_telegram_message("", "", "", "", message)
                    print(f"LevelMonitor: {message}")
                    low_breakout_reported = True
                    # При пробое вниз сбрасываем флаг пробоя вверх
                    high_breakout_reported = False
            
            # 🔥 Логика возврата в диапазон (сброс флагов при возврате между уровнями)
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

def main():
    print("Starting ScoB Bot...")
    print("Monitoring patterns...")
    
    # Send startup message
    send_startup_message()
    
    # Check exchange connection
    if not check_connection():
        return
    
    # Start Telegram polling in background thread
    polling_thread = threading.Thread(target=process_updates, daemon=True)
    polling_thread.start()
    print("Telegram polling started")
    
    # Start Level Monitor in background thread
    level_thread = threading.Thread(target=monitor_levels, daemon=True)
    level_thread.start()
    print("Level monitor started")
    
    last_signal_time = 0
    
    while True:
        try:
            # Wait for candle close
            wait_for_candle_close()
            
            # Check for patterns
            signal = check_scob_pattern()
            
            # Send signal if found
            if signal:
                current_time = int(time.time() * 1000)
                # Prevent duplicate signals
                if current_time - last_signal_time > 60000:
                    send_telegram_message(
                        signal["title"],
                        signal["time"], 
                        signal["entry"],
                        signal["stop_loss"],
                        signal["take_profit"]
                    )
                    last_signal_time = current_time
                    
            gc.collect()
            time.sleep(1)
            
            # Wait before next check
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("Bot stopped manually")
            break
        except Exception as e:
            print(f"Bot error: {e}")
            send_error_message(str(e))
            time.sleep(30)

if __name__ == "__main__":
    main()
