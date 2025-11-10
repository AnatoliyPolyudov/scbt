# fvg_detector.py
from exchange import fetch_candles_tf
from config import SYMBOL

reported_fvg = {}

def detect_fvg():
    """Обнаружить FVG на 1M таймфрейме - ОСНОВНАЯ ФУНКЦИЯ"""
    try:
        candles = fetch_candles_tf(SYMBOL, "1m", 4)
        if len(candles) < 4:
            return None
        
        candle1 = candles[1]  # Свеча после разрыва
        candle2 = candles[2]  # Свеча разрыва
        candle3 = candles[3]  # Свеча до разрыва
        
        # МЕДВЕЖИЙ FVG: low свечи 1 > high свечи 3
        if candle1[3] > candle3[2]:
            fvg_type = "BEAR_FVG"
            top = candle1[3]
            bottom = candle3[2]
            print(f"DEBUG: 🐻 TRUE BEAR FVG DETECTED: {bottom} - {top}")
            print(f"DEBUG: Candle1 Low: {candle1[3]}, Candle3 High: {candle3[2]}")
        
        # БЫЧИЙ FVG: high свечи 1 < low свечи 3  
        elif candle1[2] < candle3[3]:
            fvg_type = "BULL_FVG"
            top = candle3[3]
            bottom = candle1[2]
            print(f"DEBUG: 🐂 TRUE BULL FVG DETECTED: {bottom} - {top}")
            print(f"DEBUG: Candle1 High: {candle1[2]}, Candle3 Low: {candle3[3]}")
        
        else:
            print("DEBUG: No FVG pattern found")
            return None
        
        # Проверяем не сообщали ли уже об этом FVG
        fvg_key = f"{fvg_type}_{top}_{bottom}"
        if fvg_key not in reported_fvg:
            reported_fvg[fvg_key] = True
            return {
                "type": fvg_type,
                "top": top,
                "bottom": bottom,
                "direction": "BEAR" if fvg_type == "BEAR_FVG" else "BULL"
            }
        
        print(f"DEBUG: FVG already reported: {fvg_key}")
        return None
        
    except Exception as e:
        print(f"FVG detection error: {e}")
        return None

def monitor_fvg_independent():
    """НЕЗАВИСИМЫЙ мониторинг FVG - для дебага"""
    try:
        print("\n" + "="*50)
        print("🔍 INDEPENDENT FVG MONITORING")
        print("="*50)
        
        candles = fetch_candles_tf(SYMBOL, "1m", 4)
        if len(candles) < 4:
            print("DEBUG: Not enough candles for FVG monitoring")
            return
        
        print(f"DEBUG: Last 4 candles:")
        for i, candle in enumerate(candles):
            timestamp = candle[0]
            open_price = candle[1]
            high = candle[2]
            low = candle[3]
            close = candle[4]
            print(f"  Candle {i}: O:{open_price} H:{high} L:{low} C:{close}")
        
        candle1 = candles[1]  # Свеча после разрыва
        candle2 = candles[2]  # Свеча разрыва
        candle3 = candles[3]  # Свеча до разрыва
        
        print(f"DEBUG: Checking FVG conditions:")
        print(f"  Bear FVG: Candle1 Low ({candle1[3]}) > Candle3 High ({candle3[2]}) = {candle1[3] > candle3[2]}")
        print(f"  Bull FVG: Candle1 High ({candle1[2]}) < Candle3 Low ({candle3[3]}) = {candle1[2] < candle3[3]}")
        
        # Проверяем условия
        if candle1[3] > candle3[2]:
            print("🎯 TRUE BEAR FVG FOUND!")
            return "BEAR_FVG"
        elif candle1[2] < candle3[3]:
            print("🎯 TRUE BULL FVG FOUND!")
            return "BULL_FVG"
        else:
            print("❌ NO FVG FOUND")
            return None
            
    except Exception as e:
        print(f"FVG monitoring error: {e}")
        return None