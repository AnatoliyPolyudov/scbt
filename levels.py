# levels.py
from exchange import create_exchange
from config import SYMBOL

reported_levels = {}  # Храним: { "4H_HIGH_3850.50": 1740000000000 }

def fetch_candles_tf(timeframe, limit=1):
    """Получить свечи для указанного таймфрейма"""
    ex = create_exchange()
    return ex.fetch_ohlcv(SYMBOL, timeframe, limit=limit)

def find_current_levels():
    """Найти уровни последних закрытых свечей 4H и 1H с их timestamp"""
    levels = []

    # 4H последняя закрытая свеча
    c4 = fetch_candles_tf("4h", 1)
    if c4:
        timestamp = c4[0][0]  # Время открытия свечи
        levels.append(("4H_HIGH", c4[0][2], timestamp))
        levels.append(("4H_LOW",  c4[0][3], timestamp))

    # 1H последняя закрытая свеча
    c1 = fetch_candles_tf("1h", 1)
    if c1:
        timestamp = c1[0][0]  # Время открытия свечи
        levels.append(("1H_HIGH", c1[0][2], timestamp))
        levels.append(("1H_LOW",  c1[0][3], timestamp))

    return levels

def check_level_touch(current_price, levels):
    """Проверить точное касание уровней со сбросом по смене свечи"""
    for level_type, level_price, level_timestamp in levels:
        if current_price == level_price:  # Точное совпадение
            key = f"{level_type}_{level_price}"
            
            # Сброс если сменилась свеча (новый timestamp)
            if key in reported_levels:
                if reported_levels[key] != level_timestamp:
                    del reported_levels[key]  # Сброс - новая свеча
            
            if key not in reported_levels:
                reported_levels[key] = level_timestamp  # Сохраняем timestamp свечи
                return {
                    "type": level_type,
                    "price": level_price
                }
    return None

def check_smc_levels():
    """Основная функция проверки уровней"""
    ex = create_exchange()
    # текущая 1m свеча (close) - для точного мониторинга
    c = ex.fetch_ohlcv(SYMBOL, "1m", limit=1)
    if not c:
        return None

    current_price = c[0][4]
    levels = find_current_levels()
    return check_level_touch(current_price, levels)
