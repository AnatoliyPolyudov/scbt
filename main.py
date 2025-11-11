# main.py
import time
import threading
import gc
import requests
from exchange import check_connection, fetch_candles_tf
from telegram import send_startup_message, send_telegram_message, send_error_message
from callback_handler import handle_callback
from config import TELEGRAM_BOT_TOKEN, check_env_variables, SYMBOL
from levels import check_smc_levels, check_new_candles, find_current_levels
from fvg_detector import detect_fvg


def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    params = {'timeout': 30, 'offset': offset}
    try:
        response = requests.get(url, params=params, timeout=35)
        return response.json()
    except:
        return {'result': []}


def process_updates():
    last_update_id = None
    print("Starting Telegram updates polling...")

    while True:
        try:
            updates = get_updates(last_update_id)
            if updates.get('result'):
                for update in updates['result']:
                    if 'callback_query' in update:
                        callback_data = update['callback_query']['data']
                        print(f"Received callback: {callback_data}")
                        handle_callback(callback_data)
                    last_update_id = update['update_id'] + 1
            time.sleep(1)
        except Exception as e:
            print(f"Updates error: {e}")
            time.sleep(5)


def main():
    print("Starting SMC Levels Bot...")

    if not check_env_variables():
        print("Остановка бота из-за отсутствия переменных окружения")
        return

    print("Monitoring 4H levels + FVG search...")

    send_startup_message()

    if not check_connection():
        return

    polling_thread = threading.Thread(target=process_updates, daemon=True)
    polling_thread.start()
    print("Telegram polling started")

    last_signal_time = 0
    last_candle_check_time = 0
    last_levels_check_time = 0

    # ✅ Контроль FVG (чтобы не искать повторно на той же свече)
    last_fvg_candle = None

    print("🚀 Bot started successfully. Working...")

    while True:
        try:
            current_time = int(time.time() * 1000)

            # ✅ FVG SEARCH — строго после закрытия 1m свечи
            from callback_handler import fvg_search_active
            if fvg_search_active:
                candles = fetch_candles_tf(SYMBOL, "1m", 2)
                if candles and len(candles) >= 2:
                    last_closed_ts = candles[-2][0]

                    if last_fvg_candle != last_closed_ts:
                        last_fvg_candle = last_closed_ts

                        print("🔍 FVG SEARCH: Checking closed candle...")
                        fvg_signal = detect_fvg()

                        if fvg_signal:
                            print(f"🎯 FVG FOUND: {fvg_signal}")
                            message = f"FVG found"
                            send_telegram_message("fvg", "", "", "", message)
                        else:
                            print("❌ No FVG this candle")


            # ✅ Проверка пробоев уровней раз в 60 сек
            if current_time - last_levels_check_time > 60000:
                print(f"\n🕒 [{time.strftime('%H:%M:%S')}] Checking for breakouts...")
                signal = check_smc_levels()

                if signal:
                    if current_time - last_signal_time > 60000:
                        print(f"📨 Level breakout detected: {signal}")
                        # ПРОСТОЕ СООБЩЕНИЕ О ПРОБОЕ
                        message = f"break {signal['price']}"
                        send_telegram_message("breakout", "", "", "", message)
                        last_signal_time = current_time
                    else:
                        print("⏳ Cooldown, skipping duplicate breakout...")
                else:
                    print("📊 No breakouts detected.")

                last_levels_check_time = current_time


            # ✅ Проверка новых свечей 4H
            if current_time - last_candle_check_time > 60000:
                new_candle = check_new_candles()

                if new_candle:
                    print(f"🔄 New candle detected: {new_candle}")
                    levels = find_current_levels()

                    # ПРОСТОЕ СООБЩЕНИЕ ОБ ОБНОВЛЕНИИ УРОВНЕЙ
                    levels_text = ""
                    for level_type, level_price, _ in levels:
                        if level_type.startswith('4H'):
                            tf, l_type = level_type.split('_')
                            levels_text += f"{l_type.lower()} {level_price}\n"

                    timeframe = new_candle.replace('_NEW', '').lower()
                    message = f"update {timeframe}\n{levels_text}"
                    send_telegram_message("update", "", "", "", message)

                last_candle_check_time = current_time


            gc.collect()
            time.sleep(6)

        except KeyboardInterrupt:
            print("\n🛑 Bot stopped manually.")
            break
        except Exception as e:
            print(f"❌ Bot error: {e}")
            send_error_message(str(e))
            time.sleep(30)


if __name__ == "__main__":
    main()