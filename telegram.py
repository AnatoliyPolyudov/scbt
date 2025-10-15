# telegram.py
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, SYMBOL, TF, CAPITAL, RISK_PERCENT
from utils import calculate_position

def send_telegram_message(title, time_str, entry, stop_loss, take_profit):
    """Send signal to Telegram with position calculation"""
    # Calculate position only for trade signals (not for startup/error messages)
    if entry and stop_loss:  # Only calculate for actual trades
        size, position_info = calculate_position(float(entry), float(stop_loss))
        message = f"""scob {title}
{time_str}
entry: {entry}
stop: {stop_loss}
tp: {take_profit}

{position_info}"""
    else:
        # For startup/error messages, use the take_profit field as message
        message = take_profit
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, data=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram error: {e}")
        return False

def send_startup_message():
    """Send bot startup message"""
    message = f"Bot started\n{SYMBOL}\n{TF}\nAmount : {CAPITAL} USDT\nRisk: {RISK_PERCENT}%"
    send_telegram_message("start", "", "", "", message)

def send_error_message(error):
    """Send error message"""
    send_telegram_message("error", "", "", "", f"Bot error: {error}")
