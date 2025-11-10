# fvg_detector.py
from exchange import fetch_candles_tf
from config import SYMBOL

reported_fvg = {}

def detect_fvg():
    """Обнаружить FVG по логике ICT индикатора (на закрытых свечах)"""
    try:
        # Берем 4 свечи, но используем 1,2,3 (все закрытые)
        candles = fetch_candles_tf(SYMBOL, "1m", 4)
        if not candles or len(candles) < 4:
            return None
        
        # Используем уже закрытые свечи:
        # candles[0] - n-3 (самая старая)
        # candles[1] - n-2 (первая свеча FVG)  
        # candles[2] - n-1 (средняя свеча)
        # candles[3] - n (последняя закрытая свеча)
        
        first = candles[1]   # n-2
        second = candles[2]  # n-1  
        third = candles[3]   # n (последняя закрытая свеча)
        
        # БЫЧИЙ FVG
        bull_fvg = (
            third[3] > first[2] and      # low(n) > high(n-2)
            second[3] <= first[2] and    # low(n-1) <= high(n-2)
            second[2] >= third[3]        # high(n-1) >= low(n)
        )
        
        # МЕДВЕЖИЙ FVG
        bear_fvg = (
            third[2] < first[3] and      # high(n) < low(n-2)
            third[2] >= second[3] and    # high(n) >= low(n-1)
            second[2] >= first[3]        # high(n-1) >= low(n-2)
        )

        if bull_fvg:
            fvg_type = "BULL_FVG"
            top = third[3]      # low последней закрытой свечи
            bottom = first[2]   # high свечи n-2
            print(f"🐂 BULL FVG: {bottom} - {top}")

        elif bear_fvg:
            fvg_type = "BEAR_FVG"
            top = first[3]      # low свечи n-2
            bottom = third[2]   # high последней закрытой свечи
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


def monitor_fvg_independent():
    """НЕЗАВИСИМЫЙ мониторинг FVG — для ручной проверки"""
    try:
        candles = fetch_candles_tf(SYMBOL, "1m", 4)
        if not candles or len(candles) < 4:
            print("DEBUG: Not enough candles")
            return None
        
        first = candles[1]
        second = candles[2] 
        third = candles[3]

        bull_fvg = (
            third[3] > first[2] and
            second[3] <= first[2] and
            second[2] >= third[3]
        )
        
        bear_fvg = (
            third[2] < first[3] and
            third[2] >= second[3] and
            second[2] >= first[3]
        )

        print("\n🔍 FVG DEBUG CHECK (Closed Candles)")
        print(f"First (n-2): O:{first[1]} H:{first[2]} L:{first[3]} C:{first[4]}")
        print(f"Second (n-1): O:{second[1]} H:{second[2]} L:{second[3]} C:{second[4]}")
        print(f"Third (n): O:{third[1]} H:{third[2]} L:{third[3]} C:{third[4]}")
        print(f"Bull FVG: low(n){third[3]} > high(n-2){first[2]} = {third[3] > first[2]}")
        print(f"Bear FVG: high(n){third[2]} < low(n-2){first[3]} = {third[2] < first[3]}")

        if bull_fvg:
            print("🎯 TRUE BULL FVG FOUND")
            return "BULL_FVG"
        if bear_fvg:
            print("🎯 TRUE BEAR FVG FOUND")
            return "BEAR_FVG"
        
        print("❌ NO FVG")
        return None

    except Exception as e:
        print(f"FVG monitor error: {e}")
        return None