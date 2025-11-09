# levels.py
from exchange import fetch_candles_tf
from config import SYMBOL

reported_breakouts = {}

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
            print(f"DEBUG: 4H Levels - HIGH: {prev_candle[2]}, LOW: {prev_candle[3]}")

        # 1H предыдущая закрытая свеча
        c1 = fetch_candles_tf(SYMBOL, "1h", 2)
        if c1 and len(c1) >= 2:
            prev_candle = c1[-2]
            timestamp = prev_candle[0]
            levels.append(("1H_HIGH", prev_candle[2], timestamp))
            levels.append(("1H_LOW", prev_candle[3], timestamp))
            print(f"DEBUG: 1H Levels - HIGH: {prev_candle[2]}, LOW: {prev_candle[3]}")

        print(f"DEBUG: Total levels to monitor: {len(levels)}")
        return levels
        
    except Exception as e:
        print(f"ERROR in find_current_levels: {e}")
        return []

def check_level_breakout(current_price, levels):
    """Проверить пробой уровней"""
    print(f"DEBUG: Checking breakouts - Current price: {current_price}")
    
    for level_type, level_price, level_timestamp in levels:
        key = f"{level_type}_{level_price}"
        
        # Проверяем был ли уже пробой этого уровня
        if key in reported_breakouts:
            if reported_breakouts[key] != level_timestamp:
                print(f"DEBUG: Level reset - {key} (new candle)")
                del reported_breakouts[key]  # Сброс при смене свечи
            else:
                print(f"DEBUG: Level already reported - {key}")
                continue
        
        # Проверяем пробой ВВЕРХ (для HIGH уровней)
        if level_type.endswith('HIGH') and current_price > level_price:
            print(f"DEBUG: 🟢 BREAKOUT UP - {level_type} {current_price} > {level_price}")
            reported_breakouts[key] = level_timestamp
            return {
                "type": level_type,
                "price": level_price,
                "direction": "UP",
                "current": current_price
            }
        
        # Проверяем пробой ВНИЗ (для LOW уровней)  
        elif level_type.endswith('LOW') and current_price < level_price:
            print(f"DEBUG: 🔴 BREAKOUT DOWN - {level_type} {current_price} < {level_price}")
            reported_breakouts[key] = level_timestamp
            return {
                "type": level_type,
                "price": level_price, 
                "direction": "DOWN",
                "current": current_price
            }
        else:
            print(f"DEBUG: No breakout - {level_type} {current_price} vs {level_price}")
    
    print("DEBUG: No breakouts detected")
    return None

def check_smc_levels():
    """Основная функция проверки уровней"""
    try:
        print("DEBUG: === LEVELS CHECK STARTED ===")
        current_candle = fetch_candles_tf(SYMBOL, "1m", 1)
        if not current_candle:
            print("DEBUG: No 1m candle data")
            return None

        current_price = current_candle[0][4]
        print(f"DEBUG: Current 1m price: {current_price}")
        
        levels = find_current_levels()
        result = check_level_breakout(current_price, levels)
        
        if result:
            print(f"DEBUG: 🚨 BREAKOUT SIGNAL: {result}")
        else:
            print("DEBUG: No breakout signal")
            
        print("DEBUG: === LEVELS CHECK FINISHED ===")
        return result
        
    except Exception as e:
        print(f"ERROR in check_smc_levels: {e}")
        return None
