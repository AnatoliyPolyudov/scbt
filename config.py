# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # загружает переменные из .env

SYMBOL = "BTC/USDT:USDT"
TF = "1m"
CAPITAL = 100
RISK_PERCENT = 1

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Биржа OKX
OKX_API_KEY = os.getenv("OKX_API_KEY")
OKX_SECRET_KEY = os.getenv("OKX_SECRET_KEY")
OKX_PASSPHRASE = os.getenv("OKX_PASSPHRASE")

CANDLES_NEEDED = 3
