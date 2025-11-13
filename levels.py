# levels.py
from exchange import fetch_candles_tf
from config import SYMBOL, LEVEL_TF

reported_breakouts = {}  # Храним уже пробитые уровни
last_level_timestamp = None


def find_current_levels():
    """Определяет high и low последней закрытой свечи старшего ТФ (например, 4h)."""
    levels = []

    try:
        candles = fetch_candles_tf(SYMBOL, LEVEL_TF, 2)
        if not candles or len(candles) < 2:
            print("ERROR: Недостаточно данных для уровней")
            return []

        prev_candle = candles[-2]  # Последняя закрытая свеча
        timestamp = prev_candle[0]
        high = prev_candle[2]
        low = prev_candle[3]

        levels.append((f"{LEVEL_TF.upper()}_HIGH", high, timestamp))
        levels.append((f"{LEVEL_TF.upper()}_LOW", low, timestamp))

        print(f"DEBUG: {LEVEL_TF.upper()} Levels — HIGH: {high}, LOW: {low}")
        return levels

    except Exception as e:
        print(f"ERROR in find_current_levels: {e}")
        return []


def check_level_breakout(current_price, levels):
    """Проверяет пробитие уровней (вверх/вниз)."""
    print(f"DEBUG: Checking BREAKOUTS — Current price: {current_price}")

    for level_type, level_price, level_timestamp in levels:
        key = f"{level_type}_{level_price}"

        # Если свеча сменилась — сбрасываем старые данные
        if key in reported_breakouts and reported_breakouts[key] != level_timestamp:
            del reported_breakouts[key]

        # Проверка на пробой
        if key not in reported_breakouts:
            if level_type.endswith('HIGH') and current_price > level_price:
                print(f"🟢 BREAKOUT UP — {level_type} {current_price} > {level_price}")
                reported_breakouts[key] = level_timestamp
                return {
                    "type": level_type,
                    "price": level_price,
                    "direction": "UP",
                    "current": current_price
                }

            elif level_type.endswith('LOW') and current_price < level_price:
                print(f"🔴 BREAKOUT DOWN — {level_type} {current_price} < {level_price}")
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
    """Отслеживает появление новой свечи на старшем ТФ."""
    global last_level_timestamp

    try:
        candles = fetch_candles_tf(SYMBOL, LEVEL_TF, 1)
        if not candles:
            return None

        current_timestamp = candles[0][0]

        if last_level_timestamp is None:
            last_level_timestamp = current_timestamp
        elif current_timestamp != last_level_timestamp:
            last_level_timestamp = current_timestamp
            return f"{LEVEL_TF.upper()}_NEW"

        return None

    except Exception as e:
        print(f"ERROR in check_new_candles: {e}")
        return None


def check_smc_levels():
    """Основная функция: проверка пробоев уровней."""
    try:
        print(f"DEBUG: === {LEVEL_TF.upper()} BREAKOUT CHECK STARTED ===")

        # Текущая цена по 1-минутной свече
        current_candle = fetch_candles_tf(SYMBOL, "1m", 1)
        if not current_candle:
            print("DEBUG: No 1m candle data")
            return None

        current_price = current_candle[0][4]
        print(f"DEBUG: Current 1m price: {current_price}")

        levels = find_current_levels()
        result = check_level_breakout(current_price, levels)

        if result:
            print(f"🚨 BREAKOUT DETECTED: {result}")
        else:
            print("DEBUG: No breakout signal")

        print(f"DEBUG: === {LEVEL_TF.upper()} BREAKOUT CHECK FINISHED ===")
        return result

    except Exception as e:
        print(f"ERROR in check_smc_levels: {e}")
        return None
