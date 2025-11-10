# fvg_detector.py
from exchange import fetch_candles_tf
from config import SYMBOL

reported_fvg = {}

def detect_fvg():
    """Обнаружить FVG на 1M таймфрейме - по логике LuxAlgo"""
    try:
        candles = fetch_candles_tf(SYMBOL, "1m", 3)
        if not candles or len(candles) < 3:
            return None
        
        # ✅ Правильная нумерация — ccxt возвращает свечи от старых к новым
        current = candles[-1]   # n
        prev = candles[-2]      # n-1
        candle2 = candles[-3]   # n-2
        
        # БЫЧИЙ FVG
        bull = (
            current[3] > candle2[2] and   # low(n) > high(n-2)
            prev[4] > candle2[2]          # close(n-1) > high(n-2)
        )

        # МЕДВЕЖИЙ FVG
        bear = (
            current[2] < candle2[3] and   # high(n) < low(n-2)
            prev[4] < candle2[3]          # close(n-1) < low(n-2)
        )

        if bull:
            fvg_type = "BULL_FVG"
            top = current[3]      # low текущей
            bottom = candle2[2]   # high свечи 2

        elif bear:
            fvg_type = "BEAR_FVG"
            top = candle2[3]      # low свечи 2
            bottom = current[2]   # high текущей

        else:
            return None

        # Уникальный ключ зоны, чтобы не слать повторно
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
        
        current = candles[-1]
        prev = candles[-2]
        candle2 = candles[-3]

        bull = current[3] > candle2[2] and prev[4] > candle2[2]
        bear = current[2] < candle2[3] and prev[4] < candle2[3]

        print("\n🔍 FVG DEBUG CHECK")
        print(f"Low(n): {current[3]}, High(n-2): {candle2[2]}")
        print(f"High(n): {current[2]}, Low(n-2): {candle2[3]}")
        print(f"Close(n-1): {prev[4]}")
        print(f"bull={bull}, bear={bear}")

        if bull:
            print("🎯 BULL FVG FOUND")
            return "BULL_FVG"
        if bear:
            print("🎯 BEAR FVG FOUND")
            return "BEAR_FVG"
        
        print("❌ NO FVG")
        return None

    except Exception as e:
        print(f"FVG monitor error: {e}")
        return None
