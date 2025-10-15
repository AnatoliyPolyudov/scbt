import ccxt
import pandas as pd
import time
from datetime import datetime
import requests

SYMBOL = "ETH/USDT:USDT"
TF = "1m"
CAPITAL = 1000
RISK_PERCENT = 1

# Настройки Telegram
TELEGRAM_BOT_TOKEN = "8436652130:AAF6On0GJtRHfMZyqD3mpM57eXZfWofJeng"
TELEGRAM_CHAT_ID = "317217451"

ex = ccxt.okx({
    "enableRateLimit": True,
    "options": {
        "defaultType": "swap"
    }
})

last_signal = None
last_check_timestamp = 0
bot_start_time = datetime.now()

def send_telegram_message(message):
    """Отправка сообщения в Telegram"""
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
        print(f"Ошибка отправки в Telegram: {e}")
        return False

def calculate_position(entry_price, stop_loss_price, capital, risk_percent):
    risk_amount = capital * (risk_percent / 100)
    price_diff = abs(entry_price - stop_loss_price)
    if price_diff == 0:
        raise ValueError("Stop-loss cannot be zero")
    size = risk_amount / price_diff
    print(f"Капитал: {capital} USDT")
    print(f"Риск: {risk_percent}% = {risk_amount:.2f} USDT")
    print(f"Сумма: {size:.4f} ETH")
    return size

def fetch_new_data():
    try:
        ohlcv = ex.fetch_ohlcv(SYMBOL, TF, limit=4)  # Берем 4 свечи (все закрытые)
        df = pd.DataFrame(ohlcv, columns=["ts","open","high","low","close","volume"])
        return df
    except Exception as e:
        print(f"Ошибка получения данных: {e}")
        return pd.DataFrame()

def check_pattern(df):
    if len(df) < 4:  # Проверяем что есть минимум 4 свечи
        return None
    
    # Свеча 1 (самая старая)
    high1 = df["high"].iloc[-4]
    low1 = df["low"].iloc[-4]
    
    # Свеча 2 (средняя)
    high2 = df["high"].iloc[-3]
    low2 = df["low"].iloc[-3]
    close2 = df["close"].iloc[-3]
    
    # Свеча 3 (последняя закрытая)
    high3 = df["high"].iloc[-2]
    low3 = df["low"].iloc[-2]
    close3 = df["close"].iloc[-2]
    
    time_str = datetime.fromtimestamp(df['ts'].iloc[-3] / 1000).strftime('%H:%M')
    print(f"Свеча 2 {time_str} H:{high2:.2f} L:{low2:.2f}")
    
    if (low2 < low1 and close2 > low1 and close3 > high2):
        entry = high2
        stop_loss = low2
        risk = entry - stop_loss
        take_profit = entry + (risk * 2)
        print("scob long")
        return {
            "timestamp": df["ts"].iloc[-2],  # Время закрытия свечи 3
            "direction": "LONG",
            "entry": round(entry, 2),
            "stop_loss": round(stop_loss, 2),
            "take_profit": round(take_profit, 2),
        }
    
    elif (high2 > high1 and close2 < high1 and close3 < low2):
        entry = low2
        stop_loss = high2
        risk = stop_loss - entry
        take_profit = entry - (risk * 2)
        print("scob short")
        return {
            "timestamp": df["ts"].iloc[-2],  # Время закрытия свечи 3
            "direction": "SHORT", 
            "entry": round(entry, 2),
            "stop_loss": round(stop_loss, 2),
            "take_profit": round(take_profit, 2),
        }
    
    print("Паттерн не найден")
    return None

def print_signal(signal):
    time_str = datetime.fromtimestamp(signal["timestamp"] / 1000).strftime('%H:%M:%S')
    
    # Формируем общее сообщение для консоли и Telegram
    message = f"""scob {signal['direction'].lower()}
Время: {time_str}
Вход: {signal['entry']}
Стоп: {signal['stop_loss']}
Тейк-профит: {signal['take_profit']}"""
    
    # Выводим в консоль
    print(message)
    
    # Рассчитываем и выводим позицию
    calculate_position(
        entry_price=signal['entry'],
        stop_loss_price=signal['stop_loss'],
        capital=CAPITAL,
        risk_percent=RISK_PERCENT
    )
    
    # Отправляем то же сообщение в Telegram
    send_telegram_message(message)

if __name__ == "__main__":
    print("Мониторинг паттернов...")
    print(f"Параметры: {SYMBOL}, таймфрейм: {TF}")
    print(f"Капитал: {CAPITAL} USDT, Риск: {RISK_PERCENT}%")
    
    # Отправляем сообщение о запуске бота
    start_message = f"SCOB Bot запущен\nПара: {SYMBOL}\nТаймфрейм: {TF}\nКапитал: {CAPITAL} USDT\nРиск: {RISK_PERCENT}%"
    send_telegram_message(start_message)
    
    try:
        markets = ex.load_markets()
        print(f"Биржа OKX подключена успешно")
    except Exception as e:
        error_msg = f"Ошибка подключения к бирже\n{str(e)}"
        send_telegram_message(error_msg)
        print(f"Ошибка подключения к бирже: {e}")
        exit()
    
    while True:
        try:
            current_time = int(time.time() * 1000)
            
            # Проверяем каждую минуту (после закрытия свечи)
            if current_time - last_check_timestamp < 60000:
                time.sleep(5)
                continue
            
            last_check_timestamp = current_time
            df = fetch_new_data()
            
            if df.empty:
                continue
                
            signal = check_pattern(df)
            
            if signal:
                if last_signal is None or signal["timestamp"] != last_signal["timestamp"]:
                    last_signal = signal
                    print_signal(signal)
            
        except KeyboardInterrupt:
            stop_message = "SCOB Bot остановлен вручную"
            send_telegram_message(stop_message)
            print("\n\nМониторинг остановлен")
            break
        except Exception as e:
            error_msg = f"Ошибка в работе бота\n{str(e)}"
            send_telegram_message(error_msg)
            print(f"\nОшибка: {e}")
            time.sleep(30)
