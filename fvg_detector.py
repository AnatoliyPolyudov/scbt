# fvg_detector.py
from exchange import fetch_candles_tf
from config import SYMBOL

reported_fvg = {}

def detect_fvg():
    """
    Обнаружение FVG строго ПО ЗАКРЫТЫМ свечам.
    Берём 4 свечи, чтобы гарантированно исключить текущую (незакрытую).
    Используем последние три закрытые:
        first  = n-3
        second = n-2
        third  = n-1 (та, которая только что закрылась)
    """
    try:
        candles = fetch_candles_tf(SYMBOL, "1m", 4)  # Берём 4 свечи
        if not candles or len(candles) < 4:
            return None

        # Все три свечи — полностью закрытые
        first  = candles[-4]   # n-3
        second = candles[-3]   # n-2
        third  = candles[-2]   # n-1

        # БЫЧИЙ FVG (Fair Value Gap вверх)
        bull_fvg = (
            third[3] > first[2] and      # low(n-1) > high(n-3)
            second[3] <= first[2] and    # low(n-2) <= high(n-3)
            second[2] >= third[3]        # high(n-2) >= low(n-1)
        )

        # МЕДВЕЖИЙ FVG (Fair Value Gap вниз)
        bear_fvg = (
            third[2] < first[3] and      # high(n-1) < low(n-3)
            third[2] >= second[3] and    # high(n-1) >= low(n-2)
            second[2] >= first[3]        # high(n-2) >= low(n-3)
        )

        if not bull_fvg and not bear_fvg:
            return None

        if bull_fvg:
            fvg_type = "BULL_FVG"
            top = third[3]      # low(n-1)
            bottom = first[2]   # high(n-3)
        else:
            fvg_type = "BEAR_FVG"
            top = first[3]      # low(n-3)
            bottom = third[2]   # high(n-1)

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
