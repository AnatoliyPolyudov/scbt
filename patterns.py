# patterns.py
import time
from datetime import datetime
from exchange import fetch_candles, SYMBOL
from config import CANDLES_NEEDED
import numpy as np
import talib

def wait_for_candle_close():
    current_time = int(time.time() * 1000)
    candle_duration = 300000  # 5 minutes
    next_candle_time = (current_time // candle_duration + 1) * candle_duration
    wait_time = (next_candle_time - current_time) / 1000
    if wait_time > 0:
        print(f"Waiting for candle close: {wait_time:.1f} sec")
        time.sleep(wait_time)

def check_scob_pattern():
    """Detect ScoB pattern with ATR and without ATR"""
    print("Analyzing candles for ScoB pattern...")

    candles = fetch_candles(limit=CANDLES_NEEDED + 20)
    if len(candles) < CANDLES_NEEDED + 20:
        print("Not enough candles for analysis")
        return []

    highs = np.array([c[2] for c in candles], dtype=float)
    lows = np.array([c[3] for c in candles], dtype=float)
    closes = np.array([c[4] for c in candles], dtype=float)

    # ATR
    atr = talib.ATR(highs, lows, closes, timeperiod=14)[-1]
    if np.isnan(atr):
        atr = None

    c1, c2, c3 = candles[-3], candles[-2], candles[-1]
    high1, low1 = c1[2], c1[3]
    high2, low2, close2 = c2[2], c2[3], c2[4]
    high3, low3, close3 = c3[2], c3[3], c3[4]

    time_str = datetime.fromtimestamp(c3[0] / 1000).strftime('%H:%M')
    signals = []

    # LONG pattern
    if low2 < low1 and close2 > low1 and close3 > high2:
        entry = high2
        stop_loss_default = low2  # обычный стоп
        take_profit_default = entry + (entry - stop_loss_default) * 2

        # без ATR
        signals.append({
            "title": "long (no ATR)",
            "time": time_str,
            "entry": round(entry, 2),
            "stop_loss": round(stop_loss_default, 2),
            "take_profit": round(take_profit_default, 2)
        })

        # с ATR
        if atr:
            stop_loss_atr = entry - 1.5 * atr
            take_profit_atr = entry + (entry - stop_loss_atr) * 2
            signals.append({
                "title": "long (ATR)",
                "time": time_str,
                "entry": round(entry, 2),
                "stop_loss": round(stop_loss_atr, 2),
                "take_profit": round(take_profit_atr, 2)
            })

    # SHORT pattern
    elif high2 > high1 and close2 < high1 and close3 < low2:
        entry = low2
        stop_loss_default = high2
        take_profit_default = entry - (stop_loss_default - entry) * 2

        # без ATR
        signals.append({
            "title": "short (no ATR)",
            "time": time_str,
            "entry": round(entry, 2),
            "stop_loss": round(stop_loss_default, 2),
            "take_profit": round(take_profit_default, 2)
        })

        # с ATR
        if atr:
            stop_loss_atr = entry + 1.5 * atr
            take_profit_atr = entry - (stop_loss_atr - entry) * 2
            signals.append({
                "title": "short (ATR)",
                "time": time_str,
                "entry": round(entry, 2),
                "stop_loss": round(stop_loss_atr, 2),
                "take_profit": round(take_profit_atr, 2)
            })

    if signals:
        print(f"Signals detected at {time_str}: {[s['title'] for s in signals]}")
    else:
        print(f"No ScoB pattern found at {time_str}")

    return signals
