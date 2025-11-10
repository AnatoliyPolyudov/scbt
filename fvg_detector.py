# fvg_detector.py
from exchange import fetch_candles_tf
from config import SYMBOL

reported_fvg = {}

def detect_fvg():
    """Обнаружить FVG по логике ICT индикатора"""
    try:
        candles = fetch_candles_tf(SYMBOL, "1m", 3)
        if not candles or len(candles) < 3:
            return None
        
        # candles[0] - самая старая (n-2), candles[1] - средняя (n-1), candles[2] - текущая (n)
        first = candles[0]   # n-2
        second = candles[1]  # n-1  
        third = candles[2]   # n (текущая)
        
        # БЫЧИЙ FVG: low(n) > high(n-2) И low(n-1) <= high(n-2) И high(n-1) >= low(n)
        bull_fvg = (
            third[3] > first[2] and      # low(n) > high(n-2)
            second[3] <= first[2] and    # low(n-1) <= high(n-2) 
            second[2] >= third[3]        # high(n-1) >= low(n)
        )
        
        # МЕДВЕЖИЙ FVG: high(n) < low(n-2) И high(n) >= low(n-1) И high(n-1) >= low(n-2)
        bear_fvg = (
            third[2] < first[3] and      # high(n) < low(n-2)
            third[2] >= second[3] and    # high(n) >= low(n-1)
            second[2] >= first[3]        # high(n-1) >= low(n-2)
        )

        if bull_fvg:
            fvg_type = "BULL_FVG"
            top = third[3]      # low текущей свечи
            bottom = first[2]   # high свечи n-2
            print(f"🐂 BULL FVG: {bottom} - {top}")

        elif bear_fvg:
            fvg_type = "BEAR_FVG"
            top = first[3]      # low свечи n-2
            bottom = third[2]   # high текущей свечи
            print(f"🐻 BEAR FVG: {bottom} - {top}")

        else:
            return None

        # Уникальный ключ зоны
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