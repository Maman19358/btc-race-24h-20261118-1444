# Deep-Dip cbBTC Bot — btc-race-24h-20261118-1444

A deterministic, causal trading bot for the make.fun "Race a BTC trading bot
live for 24 hours" bounty. It trades Coinbase Wrapped BTC (CBBTC) against
USDC, one 1-minute bar at a time, with $1,000 of paper money. No network, no
clock, no files, no randomness — integer math only.

## Strategy

- **Mode A (deep dip, full size):** buy 100% of cash when the latest close
  is at least 2.50% below the trailing 240-bar (4-hour) high. Sell all when
  the close is +1.20% above the blended entry price, or stop out at -3.00%.
  After a sell, re-arm only once the close has recovered to within 1.25% of
  the trailing 4-hour high — no re-buying into a falling market.
- **Mode B (insurance):** if no trade has filled by bar 720 and the close is
  at least 1.20% below the trailing 120-bar (2-hour) high, buy 25% of cash;
  sell at +0.80% or stop at -2.00%. This only keeps the entry in the
  >= 1-trade tier if the race window never dips deeply.

## Dev-window result (frozen 24h window in the kit)

Net PnL **+$22.73**, **4 trades**, max drawdown **-0.65%**, fees $1.62.
The dev window falls -2.80% overall, so buy-and-hold loses -$31.63 on it.
Verified locally with the kit's own replay math and the protocol driver
(`proto/verify_main.py` in the grade dir); two runs are byte-identical.

## Files

- `main.py` — the bot (stdlib only + the vendored shim)
- `vendor/makefun_bars.py` — the kit's SDK shim, byte-identical copy

## Grade locally

Run the kit's `grade-local` (Node 22 baseline bots) or the Python protocol
driver against the frozen dev window in the kit; the bot must reproduce
+$22.73 / 4 trades / -0.65% and be deterministic across two runs.
