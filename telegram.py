# telegram.py
import json
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, SYMBOL, TF, CAPITAL, RISK_PERCENT
from utils import calculate_position
from exchange import ex  # подключаем объект биржи для запроса баланса

def send_telegram_message(title, time_str, entry, stop_loss, take_profit):
    """
    Send a message to Telegram.
    If entry and stop_loss are set, include position info.
    """
    if entry and stop_loss:
        size, position_info = calculate_position(float(entry), float(stop_loss))
        message = f"""scob {title}
{time_str}
entry: {entry}
stop: {stop_loss}
tp: {take_profit}

{position_info}"""
        
        keyboard = {
            'inline_keyboard': [
                [
                    {'text': 'BUY LIMIT', 'callback_data': f'BUY_LIMIT:{entry}'},
                    {'text': 'SELL LIMIT', 'callback_data': f'SELL_LIMIT:{entry}'},
                    {'text': 'Баланс', 'callback_data': 'BALANCE'}
                ]
            ]
        }
    else:
        message = take_profit
        keyboard = None
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML',
            'reply_markup': json.dumps(keyboard) if keyboard else None
        }
        response = requests.post(url, data=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"TELEGRAM_ERROR: {e}")
        return False

def send_startup_message():
    message = f"started\n{SYMBOL}\n{TF}\n{CAPITAL} USDT\n{RISK_PERCENT}%"
    send_telegram_message("startup", "", "", "", message)

def send_error_message(error):
    message = f"Bot error: {error}"
    send_telegram_message("error", "", "", "", message)

def send_balance():
    """Send current account balance to Telegram"""
    try:
        balance = ex.fetch_balance()
        usdt_balance = balance['total'].get('USDT', 0)
        message = f"Ваш баланс: {usdt_balance} USDT"
        send_telegram_message("Баланс", "", "", "", message)
    except Exception as e:
        send_error_message(f"Ошибка получения баланса: {e}")

def set_webhook():
    url = "http://194.87.238.84:5000/webhook"
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook",
            data={"url": url}
        )
        print(f"Webhook set: {response.status_code}")
    except Exception as e:
        print(f"Error setting webhook: {e}")
