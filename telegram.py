# telegram.py
import json
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, SYMBOL

def send_telegram_message(title, time_str, entry, stop_loss, take_profit, keyboard=None):
    """
    Send a message to Telegram.
    """
    message = take_profit  # Используем только текст сообщения
    
    # Если клавиатура не передана, используем стандартную
    if keyboard is None:
        # Импортируем здесь чтобы избежать циклического импорта
        from callback_handler import fvg_search_active
        
        # Динамический текст кнопки FVG SEARCH
        button_text = "FVG SEARCH" if not fvg_search_active else "FVG SEARCH"
        
        keyboard = {
            'inline_keyboard': [
                [
                    {'text': button_text, 'callback_data': 'TOGGLE_FVG_SEARCH'}
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
        
        # ИЗМЕНИЛ ФОРМАТ СООБЩЕНИЯ
        levels_text = ""
        for level_type, level_price, _ in levels:
            if level_type.startswith('4H'):
                tf, l_type = level_type.split('_')
                levels_text += f"{l_type.lower()} {level_price}\n"
        
        message = f"""{SYMBOL}
{levels_text}"""
        
        send_telegram_message("startup", "", "", "", message)
    except Exception as e:
        message = f"""{SYMBOL}
error - {e}"""
        send_telegram_message("startup", "", "", "", message)

def send_error_message(error):
    message = f"Bot error: {error}"
    send_telegram_message("error", "", "", "", message)