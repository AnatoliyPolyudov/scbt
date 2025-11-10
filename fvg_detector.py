# fvg_detector.py
from exchange import fetch_candles_tf
from config import SYMBOL

reported_fvg = {}

def detect_fvg():
    """Обнаружить FVG на 1M таймфрейме - ПО ЛОГИКЕ LUXALGO"""
    try:
        candles = fetch_candles_tf(SYMBOL, "1m", 3)  # Нужно только 3 свечи
        if len(candles) < 3:
            return None
        
        # Нумерация как в LuxAlgo:
        current_candle = candles[0]  # Текущая свеча (n)
        prev_candle = candles[1]     # Предыдущая свеча (n-1) 
        candle_2 = candles[2]        # Свеча 2 (n-2)
        
        # БЫЧИЙ FVG: low текущей > high свечи 2 И close предыдущей > high свечи 2
        bull_condition = (current_candle[3] > candle_2[2] and  # low > high[2]
                         prev_candle[4] > candle_2[2])        # close[1] > high[2]
        
        # МЕДВЕЖИЙ FVG: high текущей < low свечи 2 И close предыдущей < low свечи 2  
        bear_condition = (current_candle[2] < candle_2[3] and  # high < low[2]
                         prev_candle[4] < candle_2[3])        # close[1] < low[2]
        
        if bull_condition:
            fvg_type = "BULL_FVG"
            top = current_candle[3]  # low текущей свечи
            bottom = candle_2[2]     # high свечи 2
            print(f"DEBUG: 🐂 BULL FVG DETECTED: {bottom} - {top}")
            print(f"DEBUG: Current Low: {current_candle[3]}, Candle2 High: {candle_2[2]}, Prev Close: {prev_candle[4]}")
        
        elif bear_condition:
            fvg_type = "BEAR_FVG"  
            top = candle_2[3]        # low свечи 2
            bottom = current_candle[2]  # high текущей свечи
            print(f"DEBUG: 🐻 BEAR FVG DETECTED: {bottom} - {top}")
            print(f"DEBUG: Current High: {current_candle[2]}, Candle2 Low: {candle_2[3]}, Prev Close: {prev_candle[4]}")
        
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
                "direction": "BULL" if fvg_type == "BULL_FVG" else "BEAR"
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
        print("🔍 INDEPENDENT FVG MONITORING (LuxAlgo Logic)")
        print("="*50)
        
        candles = fetch_candles_tf(SYMBOL, "1m", 3)
        if len(candles) < 3:
            print("DEBUG: Not enough candles for FVG monitoring")
            return
        
        current = candles[0]
        prev = candles[1]  
        candle2 = candles[2]
        
        print(f"DEBUG: Last 3 candles:")
        print(f"  Current: O:{current[1]} H:{current[2]} L:{current[3]} C:{current[4]}")
        print(f"  Prev:    O:{prev[1]} H:{prev[2]} L:{prev[3]} C:{prev[4]}")
        print(f"  Candle2: O:{candle2[1]} H:{candle2[2]} L:{candle2[3]} C:{candle2[4]}")
        
        bull_cond = current[3] > candle2[2] and prev[4] > candle2[2]
        bear_cond = current[2] < candle2[3] and prev[4] < candle2[3]
        
        print(f"DEBUG: Bull FVG conditions: Low({current[3]}) > High2({candle2[2]}) = {current[3] > candle2[2]} AND Close1({prev[4]}) > High2({candle2[2]}) = {prev[4] > candle2[2]}")
        print(f"DEBUG: Bear FVG conditions: High({current[2]}) < Low2({candle2[3]}) = {current[2] < candle2[3]} AND Close1({prev[4]}) < Low2({candle2[3]}) = {prev[4] < candle2[3]}")
        
        if bull_cond:
            print("🎯 TRUE BULL FVG FOUND!")
            return "BULL_FVG"
        elif bear_cond:
            print("🎯 TRUE BEAR FVG FOUND!") 
            return "BEAR_FVG"
        else:
            print("❌ NO FVG FOUND")
            return None
            
    except Exception as e:
        print(f"FVG monitoring error: {e}")
        return None