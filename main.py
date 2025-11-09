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
from levels import check_smc_levels  # Импорт модуля уровней

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
    
    print("Monitoring 4H/1H levels...")

    send_startup_message()

    if not check_connection():
        return

    polling_thread = threading.Thread(target=process_updates, daemon=True)
    polling_thread.start()
    print("Telegram polling started")

    last_signal_time = 0

    while True:
        try:
            signal = check_smc_levels()  # Проверка уровней

            if signal:
                current_time = int(time.time() * 1000)
                if current_time - last_signal_time > 60000:  # Защита от спама 60 сек
                    # Формируем сообщение о касании уровня
                    message = f"🎯 LEVEL TOUCH\nType: {signal['type']}\nPrice: {signal['price']}"
                    send_telegram_message("level", "", "", "", message)
                    last_signal_time = current_time

            gc.collect()
            time.sleep(6)  # Проверяем каждые 6 секунд

        except KeyboardInterrupt:
            print("Bot stopped manually")
            break
        except Exception as e:
            print(f"Bot error: {e}")
            send_error_message(str(e))
            time.sleep(30)

if __name__ == "__main__":
    main()
