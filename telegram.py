# telegram.py
import json
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, SYMBOL, TF, CAPITAL, RISK_PERCENT
from utils import calculate_position

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
        button_text = "🔍 FVG SEARCH" if not fvg_search_active else "⏹️ FVG SEARCH"
        
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

# Остальные функции без изменений...
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
            level_display = f"{tf.lower()} {l_type.lower()}: {level_price}"
            levels_text += f"{level_display}\n"
        
        levels_text += "\n"
        
        for level_type, level_price in levels_1h:
            tf, l_type = level_type.split('_')
            level_display = f"{tf.lower()} {l_type.lower()}: {level_price}"
            levels_text += f"{level_display}\n"
        
        message = f"""🚀 Started
{SYMBOL}

📊 Current Levels
{levels_text}"""
        
        send_telegram_message("startup", "", "", "", message)
    except Exception as e:
        message = f"""🚀 Started
{SYMBOL}

Levels: error - {e}"""
        send_telegram_message("startup", "", "", "", message)

def send_error_message(error):
    message = f"Bot error: {error}"
    send_telegram_message("error", "", "", "", message)

# Функцию send_balance можно удалить, так как кнопка убрана