# config.py
import os
from dotenv import load_dotenv

load_dotenv()

SYMBOL = "BTC/USDT:USDT"
TF = "5m"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

OKX_API_KEY = os.getenv("OKX_API_KEY")
OKX_SECRET_KEY = os.getenv("OKX_SECRET_KEY")
OKX_PASSPHRASE = os.getenv("OKX_PASSPHRASE")

CANDLES_NEEDED = 3

def check_env_variables():
    required_vars = {
        "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
        "TELEGRAM_CHAT_ID": TELEGRAM_CHAT_ID,
        "OKX_API_KEY": OKX_API_KEY,
        "OKX_SECRET_KEY": OKX_SECRET_KEY,
        "OKX_PASSPHRASE": OKX_PASSPHRASE
    }
    
    missing_vars = []
    for name, value in required_vars.items():
        if not value:
            missing_vars.append(name)
    
    if missing_vars:
        print(f"Ошибка: Отсутствуют переменные окружения: {', '.join(missing_vars)}")
        return False
    
    print("Все переменные окружения загружены успешно")
    return True
