# levels.py
from exchange import fetch_candles_tf
from config import SYMBOL

reported_levels = {}
last_4h_timestamp = None
last_1h_timestamp = None

def find_current_levels():
    """Найти уровни предыдущих закрытых свечей 4H и 1H"""
    levels = []

    try:
        # 4H предыдущая закрытая свеча
        c4 = fetch_candles_tf(SYMBOL, "4h", 2)
        if c4 and len(c4) >= 2:
            prev_candle = c4[-2]
            timestamp = prev_candle[0]
            levels.append(("4H_HIGH", prev_candle[2], timestamp))
            levels.append(("4H_LOW", prev_candle[3], timestamp))

        # 1H предыдущая закрытая свеча
        c1 = fetch_candles_tf(SYMBOL, "1h", 2)
        if c1 and len(c1) >= 2:
            prev_candle = c1[-2]
            timestamp = prev_candle[0]
            levels.append(("1H_HIGH", prev_candle[2], timestamp))
            levels.append(("1H_LOW", prev_candle[3], timestamp))

        return levels
        
    except Exception as e:
        print(f"Error in find_current_levels: {e}")
        return []

def check_level_touch(current_price, levels):
    """Проверить точное касание уровней"""
    for level_type, level_price, level_timestamp in levels:
        if current_price == level_price:
            key = f"{level_type}_{level_price}"
            
            if key in reported_levels:
                if reported_levels[key] != level_timestamp:
                    del reported_levels[key]
            
            if key not in reported_levels:
                reported_levels[key] = level_timestamp
                return {
                    "type": level_type,
                    "price": level_price
                }
    return None

def check_new_candles():
    """Проверить смену свечей 4H и 1H"""
    global last_4h_timestamp, last_1h_timestamp
    
    try:
        # Проверяем 4H свечу
        c4 = fetch_candles_tf(SYMBOL, "4h", 1)
        if c4:
            current_4h_timestamp = c4[0][0]
            if last_4h_timestamp is None:
                last_4h_timestamp = current_4h_timestamp
            elif current_4h_timestamp != last_4h_timestamp:
                last_4h_timestamp = current_4h_timestamp
                return "4H_NEW"
        
        # Проверяем 1H свечу
        c1 = fetch_candles_tf(SYMBOL, "1h", 1)
        if c1:
            current_1h_timestamp = c1[0][0]
            if last_1h_timestamp is None:
                last_1h_timestamp = current_1h_timestamp
            elif current_1h_timestamp != last_1h_timestamp:
                last_1h_timestamp = current_1h_timestamp
                return "1H_NEW"
                
        return None
        
    except Exception as e:
        print(f"Error checking new candles: {e}")
        return None

def check_smc_levels():
    """Основная функция проверки уровней"""
    try:
        current_candle = fetch_candles_tf(SYMBOL, "1m", 1)
        if not current_candle:
            return None

        current_price = current_candle[0][4]
        levels = find_current_levels()
        return check_level_touch(current_price, levels)
        
    except Exception as e:
        print(f"Levels check error: {e}")
        return None
