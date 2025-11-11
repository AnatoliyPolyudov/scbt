# callback_handler.py
from event_bus import publish
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

# Глобальный флаг ручного управления
fvg_search_active = False

def send_telegram_simple_message(text):
    """Простая отправка сообщения в Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': text,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, data=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"TELEGRAM_ERROR: {e}")
        return False

def handle_callback(query_data):
    global fvg_search_active
    
    print("CALLBACK_HANDLER: Received callback:", query_data)
    
    if query_data == "TOGGLE_FVG_SEARCH":
        # Переключаем состояние
        fvg_search_active = not fvg_search_active
        
        if fvg_search_active:
            print("🎯 FVG SEARCH ACTIVATED")
            send_telegram_simple_message("FVG search activated")
        else:
            print("⏹️ FVG SEARCH DEACTIVATED")  
            send_telegram_simple_message("FVG search deactivated")
        
    else:
        # Остальные кнопки
        publish("BUTTON_CLICK", {"action": query_data})