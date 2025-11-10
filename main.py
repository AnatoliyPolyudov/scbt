# main.py
import order_manager
import time
import threading
import gc
import requests
from exchange import check_connection
from telegram import send_startup_message, send_telegram_message, send_error_message
from callback_handler import handle_callback
from config import TELEGRAM_BOT_TOKEN, check_env_variables
from levels import check_smc_levels, check_new_candles, find_current_levels
from fvg_detector import detect_fvg, monitor_fvg_independent

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

def main():
    print("Starting SMC Levels Bot...")
    
    # Проверяем переменные окружения перед запуском
    if not check_env_variables():
        print("Остановка бота из-за отсутствия переменных окружения")
        return
    
    print("Monitoring 4H/1H levels + FVG...")

    send_startup_message()

    if not check_connection():
        return

    polling_thread = threading.Thread(target=process_updates, daemon=True)
    polling_thread.start()
    print("Telegram polling started")

    last_signal_time = 0
    last_candle_check_time = 0
    last_levels_check_time = 0
    last_fvg_check_time = 0  # ✅ Добавляем таймер для независимого мониторинга FVG

    print("🚀 Bot started successfully. Monitoring levels every 60 seconds...")

    while True:
        try:
            current_time = int(time.time() * 1000)
            
            # ✅ НЕЗАВИСИМЫЙ МОНИТОРИНГ FVG КАЖДЫЕ 30 СЕКУНД (ДЛЯ ДЕБАГА)
            if current_time - last_fvg_check_time > 30000:
                print(f"\n🔍 [{time.strftime('%H:%M:%S')}] Independent FVG Monitoring...")
                fvg_debug = monitor_fvg_independent()
                last_fvg_check_time = current_time
            
            # ПРОВЕРЯЕМ ПРОБОЙ УРОВНЕЙ КАЖДУЮ МИНУТУ (60 секунд)
            if current_time - last_levels_check_time > 60000:
                print(f"\n🕒 [{time.strftime('%H:%M:%S')}] Checking for breakouts...")
                signal = check_smc_levels()

                if signal:
                    if current_time - last_signal_time > 60000:  # Защита от спама
                        print(f"📨 Level breakout detected: {signal}")
                        
                        # ✅ ПОИСК КОНТРАСТНОГО FVG ПОСЛЕ ПРОБОЯ
                        fvg_signal = detect_fvg()
                        print(f"DEBUG: FVG check result: {fvg_signal}")
                        
                        level_type = signal['type']
                        tf, l_type = level_type.split('_')
                        direction = signal['direction']
                        
                        if signal['direction'] == "UP":
                            # После пробоя ВВЕРХ ищем МЕДВЕЖИЙ FVG
                            if fvg_signal and fvg_signal['direction'] == "BEAR":
                                message = f"🎯 Breakout + FVG Setup\n{level_type.replace('_', ' ')} {direction}\nLevel: {signal['price']}\nCurrent: {signal['current']}\n🐻 Bear FVG: {fvg_signal['bottom']} - {fvg_signal['top']}"
                                print("🚨 BULL BREAKOUT + BEAR FVG - SELL SETUP")
                            else:
                                message = f"🎯 Level Breakout\n{level_type.replace('_', ' ')} {direction}\nLevel: {signal['price']}\nCurrent: {signal['current']}"
                                print("📈 BULL BREAKOUT ONLY")
                        
                        elif signal['direction'] == "DOWN":
                            # После пробоя ВНИЗ ищем БЫЧИЙ FVG
                            if fvg_signal and fvg_signal['direction'] == "BULL":
                                message = f"🎯 Breakout + FVG Setup\n{level_type.replace('_', ' ')} {direction}\nLevel: {signal['price']}\nCurrent: {signal['current']}\n🐂 Bull FVG: {fvg_signal['bottom']} - {fvg_signal['top']}"
                                print("🚨 BEAR BREAKOUT + BULL FVG - BUY SETUP")
                            else:
                                message = f"🎯 Level Breakout\n{level_type.replace('_', ' ')} {direction}\nLevel: {signal['price']}\nCurrent: {signal['current']}"
                                print("📉 BEAR BREAKOUT ONLY")
                        
                        send_telegram_message("breakout", "", "", "", message)
                        last_signal_time = current_time
                    else:
                        print("⏳ Signal skipped (spam protection - 60s cooldown)")
                else:
                    print("📊 No breakout signals detected")
                
                last_levels_check_time = current_time

            # Проверяем смену свечей каждые 30 секунд
            if current_time - last_candle_check_time > 30000:
                new_candle = check_new_candles()
                if new_candle:
                    print(f"🔄 New candle detected: {new_candle}")
                    
                    # Получаем актуальные уровни
                    levels = find_current_levels()
                    
                    # Формируем текст уровней
                    levels_text = ""
                    levels_4h = []
                    levels_1h = []
                    
                    for level_type, level_price, _ in levels:
                        if level_type.startswith('4H'):
                            levels_4h.append((level_type, level_price))
                        else:
                            levels_1h.append((level_type, level_price))
                    
                    # Уровни 4H
                    for level_type, level_price in levels_4h:
                        tf, l_type = level_type.split('_')
                        level_display = f"{tf.lower()} {l_type.lower()}: {level_price}"
                        levels_text += f"{level_display}\n"
                    
                    # Пустая строка между уровнями
                    levels_text += "\n"
                    
                    # Уровни 1H
                    for level_type, level_price in levels_1h:
                        tf, l_type = level_type.split('_')
                        level_display = f"{tf.lower()} {l_type.lower()}: {level_price}"
                        levels_text += f"{level_display}\n"
                    
                    # Отправляем уведомление о новых уровнях
                    timeframe = new_candle.replace('_NEW', '').lower()
                    message = f"🔄 New {timeframe} Candle\n\n📊 Updated Levels:\n{levels_text}"
                    send_telegram_message("update", "", "", "", message)
                    print(f"📨 Sent levels update for {timeframe}")
                
                last_candle_check_time = current_time

            gc.collect()
            time.sleep(6)  # Основная задержка цикла

        except KeyboardInterrupt:
            print("\n🛑 Bot stopped manually")
            break
        except Exception as e:
            print(f"❌ Bot error: {e}")
            send_error_message(str(e))
            time.sleep(30)

if __name__ == "__main__":
    main()