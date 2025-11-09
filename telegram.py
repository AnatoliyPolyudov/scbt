# telegram.py
import json
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, SYMBOL, TF, CAPITAL, RISK_PERCENT
from utils import calculate_position

def send_telegram_message(title, time_str, entry, stop_loss, take_profit):
    """
    Send a message to Telegram.
    """
    if entry and stop_loss:
        # Логика для ордеров (если понадобится в будущем)
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
                    {'text': 'BALANCE', 'callback_data': 'BALANCE'}
                ]
            ]
        }
    else:
        # Логика для уведомлений об уровнях и стартапа
        message = take_profit
        keyboard = {
            'inline_keyboard': [
                [
                    {'text': 'BALANCE', 'callback_data': 'BALANCE'}
                ]
            ]
        }
    
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
    try:
        from exchange import create_exchange
        from levels import find_current_levels
        
        ex = create_exchange()
        balance = ex.fetch_balance()
        usdt_balance = balance['total'].get('USDT', 0)
        rounded_balance = round(usdt_balance, 1)
        
        # Получаем текущие уровни
        levels = find_current_levels()
        
        # Формируем текст уровней в нужном формате
        levels_text = ""
        for level_type, level_price, _ in levels:
            # Преобразуем тип в нужный формат: "4h high", "1h low" и т.д.
            tf, l_type = level_type.split('_')
            level_display = f"{tf.lower()} {l_type.lower()}: {level_price}"
            levels_text += f"{level_display}\n"
        
        message = f"""🚀 Started
symbol: {SYMBOL}
tf: {TF}
capital: {CAPITAL} USDT
risk: {RISK_PERCENT}%
balance: {rounded_balance} USDT

📊 Current Levels
{levels_text}"""
        
        send_telegram_message("startup", "", "", "", message)
    except Exception as e:
        message = f"""🚀 Started
symbol: {SYMBOL}
tf: {TF}
capital: {CAPITAL} USDT  
risk: {RISK_PERCENT}%
balance: error
Levels: error - {e}"""
        send_telegram_message("startup", "", "", "", message)

def send_error_message(error):
    """Send error message to Telegram"""
    message = f"Bot error: {error}"
    send_telegram_message("error", "", "", "", message)

def send_balance():
    """Send current account balance to Telegram"""
    try:
        from exchange import create_exchange
        ex = create_exchange()
        balance = ex.fetch_balance()
        usdt_balance = balance['total'].get('USDT', 0)
        message = f"Balance: {round(usdt_balance, 1)} USDT"
        send_telegram_message("BALANCE", "", "", "", message)
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
