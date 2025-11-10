# fvg_detector.py
from exchange import fetch_candles_tf
from config import SYMBOL

reported_fvg = {}

def detect_fvg():
    """Обнаружить FVG на 1M таймфрейме"""
    try:
        # Берем последние 3 свечи 1M
        candles = fetch_candles_tf(SYMBOL, "1m", 3)
        if len(candles) < 3:
            return None
        
        current = candles[0]  # Текущая свеча [timestamp, o, h, l, c, volume]
        prev1 = candles[1]    # Предыдущая свеча  
        prev2 = candles[2]    # Свеча 2 назад
        
        current_low = current[3]
        current_high = current[2]
        prev2_high = prev2[2]
        prev2_low = prev2[3]
        
        # МЕДВЕЖИЙ FVG (разрыв вниз): high текущей < low двух свечей назад
        if current_high < prev2_low:
            fvg_type = "BEAR_FVG"
            top = prev2_low
            bottom = current_high
            print(f"DEBUG: 🐻 BEAR FVG detected - Price gap down: {current_high} < {prev2_low}")
        
        # БЫЧИЙ FVG (разрыв вверх): low текущей > high двух свечей назад
        elif current_low > prev2_high:
            fvg_type = "BULL_FVG" 
            top = current_low
            bottom = prev2_high
            print(f"DEBUG: 🐂 BULL FVG detected - Price gap up: {current_low} > {prev2_high}")
        
        else:
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
        
        return None
        
    except Exception as e:
        print(f"FVG detection error: {e}")
        return None