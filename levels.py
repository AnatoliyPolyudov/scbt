# levels.py
from exchange import fetch_candles_tf
from config import SYMBOL

reported_breakouts = {}  # Храним ПРОБИТЫЕ уровни
last_4h_timestamp = None

def find_current_levels():
    """Найти уровни предыдущих закрытых свечей 4H"""
    levels = []

    try:
        # 4H предыдущая закрытая свеча
        c4 = fetch_candles_tf(SYMBOL, "4h", 2)
        if c4 and len(c4) >= 2:
            prev_candle = c4[-2]
            timestamp = prev_candle[0]
            levels.append(("4H_HIGH", prev_candle[2], timestamp))
            levels.append(("4H_LOW", prev_candle[3], timestamp))
            print(f"DEBUG: 4H Levels - HIGH: {prev_candle[2]}, LOW: {prev_candle[3]}")

        print(f"DEBUG: Total levels to monitor: {len(levels)}")
        return levels
        
    except Exception as e:
        print(f"ERROR in find_current_levels: {e}")
        return []

def check_level_breakout(current_price, levels):
    """Проверить ПРОБОЙ уровней"""
    print(f"DEBUG: Checking BREAKOUTS - Current price: {current_price}")
    
    for level_type, level_price, level_timestamp in levels:
        key = f"{level_type}_{level_price}"
        
        # Проверяем был ли уже пробой этого уровня
        if key in reported_breakouts:
            if reported_breakouts[key] != level_timestamp:
                del reported_breakouts[key]  # Сброс при смене свечи
            else:
                continue  # Уже сообщали о пробое
        
        # ПРОБОЙ ВВЕРХ: цена > HIGH уровня
        if level_type.endswith('HIGH') and current_price > level_price:
            print(f"DEBUG: 🟢 BREAKOUT UP - {level_type} {current_price} > {level_price}")
            reported_breakouts[key] = level_timestamp
            return {
                "type": level_type,
                "price": level_price,
                "direction": "UP",
                "current": current_price
            }
        
        # ПРОБОЙ ВНИЗ: цена < LOW уровня  
        elif level_type.endswith('LOW') and current_price < level_price:
            print(f"DEBUG: 🔴 BREAKOUT DOWN - {level_type} {current_price} < {level_price}")
            reported_breakouts[key] = level_timestamp
            return {
                "type": level_type,
                "price": level_price, 
                "direction": "DOWN", 
                "current": current_price
            }
    
    print("DEBUG: No breakouts detected")
    return None

def check_new_candles():
    """Проверить смену свечей 4H"""
    global last_4h_timestamp
    
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
                
        return None
        
    except Exception as e:
        print(f"Error checking new candles: {e}")
        return None

def check_smc_levels():
    """Основная функция проверки уровней - ИСПОЛЬЗУЕМ ПРОБОЙ"""
    try:
        print("DEBUG: === BREAKOUT CHECK STARTED ===")
        current_candle = fetch_candles_tf(SYMBOL, "1m", 1)
        if not current_candle:
            print("DEBUG: No 1m candle data")
            return None

        current_price = current_candle[0][4]
        print(f"DEBUG: Current 1m price: {current_price}")
        
        levels = find_current_levels()
        result = check_level_breakout(current_price, levels)  # ✅ ИСПОЛЬЗУЕМ ПРОБОЙ
        
        if result:
            print(f"DEBUG: 🚨 BREAKOUT SIGNAL: {result}")
        else:
            print("DEBUG: No breakout signal")
            
        print("DEBUG: === BREAKOUT CHECK FINISHED ===")
        return result
        
    except Exception as e:
        print(f"ERROR in check_smc_levels: {e}")
        return None