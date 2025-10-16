# main.py
import order_manager
import time
import threading
from exchange import check_connection
from patterns import check_scob_pattern, wait_for_candle_close
from telegram import send_startup_message, send_telegram_message, send_error_message
from flask import Flask, request
from callback_handler import handle_callback

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    data = request.json
    callback_data = data['callback_query']['data']
    handle_callback(callback_data)
    return 'OK'

def run_flask():
    app.run(host='0.0.0.0', port=5000)

def main():
    print("Starting ScoB Bot...")
    print("Monitoring patterns...")
    
    # Send startup message
    send_startup_message()
    
    # Check exchange connection
    if not check_connection():
        return
    
    # Start Flask in background thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("Web server started on port 5000")
    
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