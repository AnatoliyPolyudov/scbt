# В функции send_startup_message() ИСПРАВЛЕН формат:

def send_startup_message():
    try:
        from exchange import create_exchange
        from levels import find_current_levels
        
        ex = create_exchange()
        balance = ex.fetch_balance()
        usdt_balance = balance['total'].get('USDT', 0)
        rounded_balance = round(usdt_balance, 1)
        
        # Получаем текущие уровни
        levels = find_current_levels()
        
        # Разделяем уровни по таймфреймам
        levels_4h = []
        levels_1h = []
        
        for level_type, level_price, _ in levels:
            if level_type.startswith('4H'):
                levels_4h.append((level_type, level_price))
            else:
                levels_1h.append((level_type, level_price))
        
        # Формируем текст уровней с отступом
        levels_text = ""
        
        # Уровни 4H
        for level_type, level_price in levels_4h:
            tf, l_type = level_type.split('_')
            level_display = f"{tf.lower()} {l_type.lower()}: {level_price}"
            levels_text += f"{level_display}\n"
        
        # Добавляем пустую строку между 4H и 1H
        levels_text += "\n"
        
        # Уровни 1H
        for level_type, level_price in levels_1h:
            tf, l_type = level_type.split('_')
            level_display = f"{tf.lower()} {l_type.lower()}: {level_price}"
            levels_text += f"{level_display}\n"
        
        message = f"""🚀 Started
symbol: {SYMBOL}
tf: {TF}
capital: {CAPITAL} USDT
risk: {RISK_PERCENT}%
balance: {rounded_balance} USDT

📊 Current Levels
{levels_text}"""
        
        send_telegram_message("startup", "", "", "", message)
    except Exception as e:
        message = f"""🚀 Started
symbol: {SYMBOL}
tf: {TF}
capital: {CAPITAL} USDT  
risk: {RISK_PERCENT}%
balance: error
Levels: error - {e}"""
        send_telegram_message("startup", "", "", "", message)
