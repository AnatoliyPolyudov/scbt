# main.py
import time
from threading import Thread
from web_server import app
import order_manager  # подписки подключаются здесь
from patterns import check_scob_pattern, wait_for_candle_close
from telegram import send_startup_message, send_telegram_message, send_error_message
from exchange import check_connection

def run_web_server():
    """Запуск Flask в отдельном потоке"""
    app.run(host='0.0.0.0', port=5000, threaded=True)

def main_loop():
    print("Starting ScoB Bot...")
    print("Monitoring patterns...")
    
    # Отправка стартап-сообщения
    send_startup_message()
    
    if not check_connection():
        return
    
    last_signal_time = 0
    
    while True:
        try:
            wait_for_candle_close()
            
            signal = check_scob_pattern()
            
            if signal:
                current_time = int(time.time() * 1000)
                if current_time - last_signal_time > 60000:
                    send_telegram_message(
                        signal["title"],
                        signal["time"], 
                        signal["entry"],
                        signal["stop_loss"],
                        signal["take_profit"]
                    )
                    last_signal_time = current_time
            
            time.sleep(5)
        
        except KeyboardInterrupt:
            print("Bot stopped manually")
            break
        except Exception as e:
            print(f"Bot error: {e}")
            send_error_message(str(e))
            time.sleep(30)

if __name__ == "__main__":
    # Flask запускаем в отдельном потоке
    web_thread = Thread(target=run_web_server, daemon=True)
    web_thread.start()
    
    # основной цикл бота
    main_loop()
