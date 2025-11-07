# utils.py
from config import CAPITAL, RISK_PERCENT, SYMBOL

def calculate_position(entry_price, stop_loss_price):
    """Calculate position size based on risk management"""
    risk_amount = CAPITAL * (RISK_PERCENT / 100)
    price_diff = abs(entry_price - stop_loss_price)
    
    if price_diff == 0:
        raise ValueError("Stop-loss cannot be zero")
    
    # Для фьючерсов USDT-margin размер позиции в USDT
    size_usdt = risk_amount
    
    position_info = f"""Amount: {CAPITAL} USDT
Risk: {RISK_PERCENT}% = {risk_amount:.2f} USDT
Position size: {size_usdt:.2f} USDT"""
    
    print(position_info)
    return size_usdt, position_info