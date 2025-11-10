# fvg_detector.py
from exchange import fetch_candles_tf
from config import SYMBOL

reported_fvg = {}

def detect_fvg():
    """Обнаружить FVG по правильному описанию"""
    try:
        candles = fetch_candles_tf(SYMBOL, "1m", 3)
        if not candles or len(candles) < 3:
            return None
        
        # candles[0] - первая (самая старая), candles[1] - вторая, candles[2] - третья (текущая)
        first = candles[0]   # первая свеча
        second = candles[1]  # вторая свеча  
        third = candles[2]   # третья свеча
        
        # БЫЧИЙ FVG: на восходящей второй свече, между максимумом первой и минимумом третьей
        bull_fvg = (
            second[4] > second[1] and  # вторая свеча восходящая (close > open)
            third[3] > first[2] and    # минимум третьей > максимум первой (не перекрываются)
            third[3] > first[2]        # GAP: low третьей > high первой
        )
        
        # МЕДВЕЖИЙ FVG: на падающей второй свече, между минимумом первой и максимумом третьей
        bear_fvg = (
            second[4] < second[1] and  # вторая свеча падающая (close < open)
            third[2] < first[3] and    # максимум третьей < минимум первой (не перекрываются)
            third[2] < first[3]        # GAP: high третьей < low первой
        )

        if bull_fvg:
            fvg_type = "BULL_FVG"
            top = third[3]      # минимум третьей свечи
            bottom = first[2]   # максимум первой свечи
            print(f"🐂 BULL FVG: {bottom} - {top}")

        elif bear_fvg:
            fvg_type = "BEAR_FVG"
            top = first[3]      # минимум первой свечи
            bottom = third[2]   # максимум третьей свечи
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
        candles = fetch_candles_tf(SYMBOL, "1m", 3)
        if not candles or len(candles) < 3:
            print("DEBUG: Not enough candles")
            return None
        
        first = candles[0]
        second = candles[1] 
        third = candles[2]

        bull_fvg = second[4] > second[1] and third[3] > first[2]
        bear_fvg = second[4] < second[1] and third[2] < first[3]

        print("\n🔍 FVG DEBUG CHECK")
        print(f"First candle: O:{first[1]} H:{first[2]} L:{first[3]} C:{first[4]}")
        print(f"Second candle: O:{second[1]} H:{second[2]} L:{second[3]} C:{second[4]}")
        print(f"Third candle: O:{third[1]} H:{third[2]} L:{third[3]} C:{third[4]}")
        print(f"Bull FVG: second_up={second[4] > second[1]}, gap={third[3] > first[2]}")
        print(f"Bear FVG: second_down={second[4] < second[1]}, gap={third[2] < first[3]}")

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