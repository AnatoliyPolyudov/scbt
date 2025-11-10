from exchange import fetch_candles_tf
from config import SYMBOL

reported_fvg = {}

def detect_fvg():
    """Обнаружить FVG на 1M таймфрейме - по логике LuxAlgo"""
    try:
        candles = fetch_candles_tf(SYMBOL, "1m", 3)
        if not candles or len(candles) < 3:
            return None
        
        # Правильная нумерация: ccxt → последние свечи в конце списка
        current_candle = candles[-1]   # n
        prev_candle = candles[-2]      # n-1
        candle_2 = candles[-3]         # n-2
        
        # Бычий FVG
        bull_condition = (
            current_candle[3] > candle_2[2] and   # low(n) > high(n-2)
            prev_candle[4] > candle_2[2]          # close(n-1) > high(n-2)
        )

        # Медвежий FVG
        bear_condition = (
            current_candle[2] < candle_2[3] and   # high(n) < low(n-2)
            prev_candle[4] < candle_2[3]          # close(n-1) < low(n-2)
        )

        if bull_condition:
            fvg_type = "BULL_FVG"
            top = current_candle[3]
            bottom = candle_2[2]
        elif bear_condition:
            fvg_type = "BEAR_FVG"
            top = candle_2[3]
            bottom = current_candle[2]
        else:
            return None

        # Создаём уникальный ключ GAP'а
        fvg_key = f"{fvg_type}_{top}_{bottom}"

        # Проверяем, сообщали ли раньше
        if fvg_key not in reported_fvg:
            reported_fvg[fvg_key] = True
            return {
                "type": fvg_type,
                "top": top,
                "bottom": bottom,
                "direction": "BULL" if fvg_type == "BULL_FVG" else "BEAR"
            }

        return None

    except Exception as e:
        print(f"FVG detection error: {e}")
        return None
