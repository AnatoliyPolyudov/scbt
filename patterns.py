# patterns.py
import time
from datetime import datetime
import numpy as np
import talib
from exchange import fetch_candles, ex, SYMBOL
from config import CANDLES_NEEDED

def wait_for_candle_close():
    """Wait for current candle to close"""
    current_time = int(time.time() * 1000)
    candle_duration = 300000  # 5 минут
    next_candle_time = (current_time // candle_duration + 1) * candle_duration
    wait_time = (next_candle_time - current_time) / 1000
    if wait_time > 0:
        print(f"Waiting for candle close: {wait_time:.1f} sec")
        time.sleep(wait_time)

def check_scob_pattern():
    """Check ScoB pattern on closed candles - returns signal data or None"""
    print("Analyzing candles for ScoB pattern...")
    
    candles = fetch_candles(limit=CANDLES_NEEDED)
    if len(candles) < CANDLES_NEEDED:
        print("Not enough candles for analysis")
        return None

    # === ATR фильтр через TA-Lib ===
    atr_candles = ex.fetch_ohlcv(SYMBOL, "5m", limit=20)
    highs = np.array([c[2] for c in atr_candles], dtype=float)
    lows = np.array([c[3] for c in atr_candles], dtype=float)
    closes = np.array([c[4] for c in atr_candles], dtype=float)
    atr_series = talib.ATR(highs, lows, closes, timeperiod=14)
    atr = atr_series[-1]  # последнее значение ATR

    # Candle 1 (oldest) - индекс -3
    high1 = candles[-3][2]
    low1 = candles[-3][3]

    # Candle 2 (ScoB pattern) - индекс -2  
    high2 = candles[-2][2]
    low2 = candles[-2][3]
    close2 = candles[-2][4]

    # Candle 3 (confirmation) - индекс -1
    high3 = candles[-1][2]
    low3 = candles[-1][3] 
    close3 = candles[-1][4]

    time_str = datetime.fromtimestamp(candles[-1][0] / 1000).strftime('%H:%M')

    print(f"Candles data:")
    print(f"  Candle 1: H:{high1:.2f} L:{low1:.2f}")
    print(f"  Candle 2: H:{high2:.2f} L:{low2:.2f} C:{close2:.2f}")
    print(f"  Candle 3: H:{high3:.2f} L:{low3:.2f} C:{close3:.2f}")

    # ATR фильтр: пропускаем слабые свечи
    candle_range = high2 - low2
    if candle_range < atr * 0.7:
        print(f"ATR filter: range {candle_range:.2f} too small vs ATR {atr:.2f}, skip")
        return None

    # LONG: ScoB down + close above high2
    if (low2 < low1 and close2 > low1 and close3 > high2):
        entry = high2
        stop_loss = entry - 1.5 * atr
        risk = entry - stop_loss
        take_profit = entry + (risk * 2)
        print(f"ScoB LONG pattern detected at {time_str}")
        return {
            "title": "long",
            "time": time_str,
            "entry": round(entry, 2),
            "stop_loss": round(stop_loss, 2),
            "take_profit": round(take_profit, 2),
        }

    # SHORT: ScoB up + close below low2  
    elif (high2 > high1 and close2 < high1 and close3 < low2):
        entry = low2
        stop_loss = entry + 1.5 * atr
        risk = stop_loss - entry
        take_profit = entry - (risk * 2)
        print(f"ScoB SHORT pattern detected at {time_str}")
        return {
            "title": "short",
            "time": time_str,
            "entry": round(entry, 2),
            "stop_loss": round(stop_loss, 2),
            "take_profit": round(take_profit, 2),
        }

    print(f"No ScoB pattern found at {time_str}")
    return None
