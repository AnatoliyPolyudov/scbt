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
        from exchange import get_exchange
        from levels import find_current_levels
        
        ex = get_exchange()
        balance = ex.fetch_balance()
        usdt_balance = balance['total'].get('USDT', 0)
        rounded_balance = round(usdt_balance, 1)
        
        levels = find_current_levels()
        
        levels_4h = []
        levels_1h = []
        
        for level_type, level_price, _ in levels:
            if level_type.startswith('4H'):
                levels_4h.append((level_type, level_price))
            else:
                levels_1h.append((level_type, level_price))
        
        levels_text = ""
        
        for level_type, level_price in levels_4h:
            tf, l_type = level_type.split('_')
            level_display = f"{tf
