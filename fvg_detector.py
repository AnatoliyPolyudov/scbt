# fvg_detector.py
from exchange import fetch_candles_tf
from config import SYMBOL, FVG_TF

reported_fvg = {}

def detect_fvg():
    """
    Обнаружение FVG строго по ЗАКРЫТЫМ свечам.
    Берём 4 свечи, чтобы гарантированно исключить текущую (незакрытую).
    Используем последние три закрытые:
        first  = n-3
        second = n-2
        third  = n-1 (та, которая только что закрылась)
    """
    try:
        candles = fetch_candles_tf(SYMBOL, FVG_TF, 4)  # Используем timeframe из config
        if not candles or len(candles) < 4:
            return None

        # Все три свечи — полностью закрытые
        first  = candles[-4]   # n-3
        second = candles[-3]   # n-2
        third  = candles[-2]   # n-1

        # Данные по свечам
        first_high, first_low = first[2], first[3]
        second_high, second_low = second[2], second[3]
        third_high, third_low = third[2], third[3]

        # БЫЧИЙ FVG (Fair Value Gap вверх)
        bull_fvg = third_low > first_high

        # МЕДВЕЖИЙ FVG (Fair Value Gap вниз)
        bear_fvg = third_high < first_low

        if not bull_fvg and not bear_fvg:
            return None

        if bull_fvg:
            fvg_type = "BULL_FVG"
            top = third_low      # нижняя граница гэпа
            bottom = first_high  # верхняя граница гэпа
        else:
            fvg_type = "BEAR_FVG"
            top = first_low      # нижняя граница гэпа
            bottom = third_high  # верхняя граница гэпа

        key = f"{fvg_type}_{top}_{bottom}"

        if key not in reported_fvg:
            reported_fvg[key] = True
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
