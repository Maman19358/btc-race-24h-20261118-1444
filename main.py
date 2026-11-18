"""
Deterministic deep-dip cbBTC trading bot strategy:
- Deep-dip Mode A: buy 100% of cash at -2.50% vs the trailing 4h high, sell +1.20% / stop -3.00%.
- Re-arm at recovery within 1.25%.
- Mode B insurance: 25% of cash, only if zero trades by bar 720, dip -1.20% vs the trailing 2h high, sell +0.80% / stop -2.00%.
- Integer math only, deterministic.
"""

import os
import sys

# Add script's directory and its vendor/ subdirectory to sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)
vendor_dir = os.path.join(script_dir, "vendor")
if vendor_dir not in sys.path:
    sys.path.insert(0, vendor_dir)

import makefun_bars

closes = []
armed = True
mode = None
trades = 0

def on_batch(state, batch):
    global armed, mode, trades

    if state.warming_up:
        return []

    for fill in batch.get("fills") or []:
        if fill.get("status") == "filled":
            trades += 1

    c = state.close("CBBTC")
    if c is None:
        return []

    closes.append(c)

    ref_a = max(closes[-240:])
    ref_b = max(closes[-120:])

    holding = state.positions.get("CBBTC")
    if holding is not None and holding.qty > 0:
        entry = holding.cost * 10**7 // holding.qty
        should_sell = False
        if mode == 'A':
            if c * 10000 >= entry * (10000 + 120) or c * 10000 <= entry * (10000 - 300):
                should_sell = True
        elif mode == 'B':
            if c * 10000 >= entry * (10000 + 80) or c * 10000 <= entry * (10000 - 200):
                should_sell = True
        else:
            # Defensive fallback: mode is always set on a buy, so the fallback uses the Mode A thresholds.
            if c * 10000 >= entry * (10000 + 120) or c * 10000 <= entry * (10000 - 300):
                should_sell = True

        if should_sell:
            armed = False
            mode = None
            return [{
                "side": "sell",
                "symbol": "CBBTC",
                "qty": holding.qty,
                "max_slippage_bps": 100
            }]
        else:
            return []
    else:
        if not armed:
            if c * 10000 >= ref_a * (10000 - 125):
                armed = True

        if not armed:
            return []

        if c * 10000 <= ref_a * (10000 - 250) and state.cash >= 1_000_000:
            mode = 'A'
            return [{
                "side": "buy",
                "symbol": "CBBTC",
                "notional_quote_units": state.cash,
                "max_slippage_bps": 100
            }]

        if trades == 0 and state.seq >= 720 and c * 10000 <= ref_b * (10000 - 120):
            notional = state.cash * 25 // 100
            if notional >= 1_000_000:
                mode = 'B'
                return [{
                    "side": "buy",
                    "symbol": "CBBTC",
                    "notional_quote_units": notional,
                    "max_slippage_bps": 100
                }]

        return []

if __name__ == "__main__":
    makefun_bars.run(on_batch)
