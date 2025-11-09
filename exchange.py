# levels.py
from exchange import get_exchange  # ✅ Импортируем get_exchange вместо create_exchange
from config import SYMBOL

reported_levels = {}  # Храним: { "4H_HIGH_3850.50": 1740000000000 }

def fetch_candles_tf(timeframe, limit=2):
    """Получить свечи для указанного таймфрейма"""
    ex = get_exchange()  # ✅ Используем глобальный экземпляр
    return ex.fetch_ohlcv(SYMBOL, timeframe, limit=limit)

def find_current_levels():
    """Найти уровни ПРЕДЫДУЩИХ закрытых свечей 4H и 1H"""
    levels = []

    # 4H ПРЕДЫДУЩАЯ закрытая свеча (индекс -2)
    c4 = fetch_candles_tf("4h", 2)
    if c4 and len(c4) >= 2:
        prev_candle = c4[-2]  # ПРЕДЫДУЩАЯ закрытая свеча
        timestamp = prev_candle[0]  # Время открытия свечи
        levels.append(("4H_HIGH", prev_candle[2], timestamp))
        levels.append(("4H_LOW",  prev_candle[3], timestamp))

    # 1H ПРЕДЫДУЩАЯ закрытая свеча (индекс -2)
    c1 = fetch_candles_tf("1h", 2)
    if c1 and len(c1) >= 2:
        prev_candle = c1[-2]  # ПРЕДЫДУЩАЯ закрытая свеча
        timestamp = prev_candle[0]  # Время открытия свечи
        levels.append(("1H_HIGH", prev_candle[2], timestamp))
        levels.append(("1H_LOW",  prev_candle[3], timestamp))

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
    ex = get_exchange()  # ✅ Используем глобальный экземпляр
    # текущая 1m свеча (close) - для точного мониторинга
    c = ex.fetch_ohlcv(SYMBOL, "1m", limit=1)
    if not c:
        return None

    current_price = c[0][4]
    levels = find_current_levels()
    return check_level_touch(current_price, levels)
