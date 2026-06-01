# Confluence Engine Pro — Pine Script v6 Strategy

A weighted, multi-indicator **confluence** strategy for TradingView. It scores
TREND + MOMENTUM + VOLATILITY + VOLUME indicators into a single net score, gates
entries on ADX/ATR regime + higher-timeframe trend, sizes positions from risk,
manages partial take-profits + a chandelier trail, and reports **In-Sample (IS)
vs Out-of-Sample (OOS)** performance for walk-forward validation.

> ⚠️ **Honest warning.** This design stacks many indicators *and* an adaptive
> heuristic weighting layer. That is a **high overfitting-risk** combination.
> **Only OOS results matter.** Any test window with fewer than ~20–30 trades is
> statistically meaningless. The adaptive layer is a **heuristic, not machine
> learning and not AI**, and nothing here implies or guarantees profit.

---

## 1. How to load it in TradingView (step by step)

1. Open [tradingview.com](https://www.tradingview.com) → open any chart.
2. Bottom panel → **Pine Editor** tab.
3. Click **Open → New blank strategy** (or just clear the editor).
4. Open `ConfluenceEnginePro.pine` from this folder, **copy the entire file**,
   and paste it into the Pine Editor (replacing everything).
5. Click **Save** (name it, e.g. "Confluence Engine Pro").
6. Click **Add to chart**. The strategy plots markers + three tables and writes
   results to the **Strategy Tester** panel.
7. Open **Settings (gear icon)** to tune every input — all are grouped and have
   tooltips. Open the **Properties** tab to confirm commission/slippage/initial
   capital match what you intend (they are also exposed as script inputs).
8. Use the **Strategy Tester → Overview / Performance Summary / List of Trades**
   for the full TradingView report. The on-chart **IS / OOS table** is the one
   you should trust for validation.

**Verifying no-repaint:** add it to a chart, let bars close, then reload — the
historical entry markers must not move. HTF data uses
`lookahead=barmerge.lookahead_off` and entries are gated on
`barstate.isconfirmed`, so signals are evaluated on confirmed bars only.

---

## 2. Strategy character

This is **primarily a trend-following / momentum-continuation system** with
volatility and volume *confirmation* filters — **not** a mean-reversion system:

- **Trend-following core:** EMA cross, Ichimoku cloud, Supertrend, ADX gate, and
  an HTF EMA trend filter all push it to trade **with** an established trend.
- **Momentum confirmation:** RSI (midline, de-weighted at extremes), MACD,
  Stochastic — it wants momentum *aligned* with the trend, and explicitly
  *avoids* buying into overbought / selling into oversold extremes.
- **Volatility/volume gating:** Bollinger expansion + an ATR% ceiling + a volume
  spike requirement mean it prefers **breakouts/continuations on real
  participation**, and stands aside in chop (ADX gate) and during news-spike
  volatility (ATR% filter).

Net effect: fewer, higher-quality trades that try to ride trends with a defined
1R/2R partial-exit structure and a trailing runner — a **high risk:reward,
lower win-rate** profile typical of trend systems.

**Recommended timeframe:** **1H–4H for swing trades**, or **Daily** for
position trades. These reduce noise/whipsaw, make the ADX and HTF filters
meaningful, and keep commission/slippage drag low relative to move size. The
intraday session filter exists for 5–15m use, but lower timeframes hurt this
style (more chop, costs eat the edge).

---

## 3. Assets it is BUILT for (and why)

Liquid, **trend-prone** US equities and ETFs with tight spreads and clean,
sustained directional moves:

**Broad-index / sector ETFs (best fit — smooth trends, tight spreads, deep liquidity):**
- **SPY, QQQ, IWM, DIA** — deep liquidity, strong drift, low spread; the ADX/HTF
  filters work cleanly.
- **XLK, XLF, XLE, XLV, SMH** — sector trends persist; good for the trend core.

**Large-cap trending leaders (strong momentum, high liquidity):**
- **AAPL, MSFT, NVDA, AMZN, GOOGL, META, AVGO, NFLX** — they trend hard in
  regimes and have the liquidity to absorb the 2-tick slippage assumption.

**Liquid trend-following commodity/leveraged ETFs (for the volatility-tuned profile):**
- **TQQQ / SOXL** (leveraged — only with reduced risk%), **GLD, USO** when in
  clear trends.

**Why these:** high average daily volume (low slippage), penny-tight spreads
(realistic 2-tick fills), and a documented tendency to **trend** rather than
oscillate, which is exactly what the ADX gate + HTF filter + Supertrend/Ichimoku
core are built to exploit.

---

## 4. Assets it is NOT suitable for

- **Low-liquidity / small-cap / micro-cap stocks** — wide spreads and gaps make
  the 0.03% commission + 2-tick slippage assumption optimistic; fills are bad.
- **Penny stocks & illiquid OTC names** — un-backtestable, manipulation-prone.
- **Choppy, range-bound, low-ADX tickers** — the engine is designed to *skip*
  these; forcing it on them produces whipsaw losses.
- **Mean-reverting pairs / range ETFs** (e.g. many bond ETFs in calm regimes,
  some low-beta utilities) — wrong character; use a reversion system instead.
- **Hyper-volatile event-driven names** (biotech binary events, meme spikes) —
  the ATR% filter will (correctly) block most entries; results are noise.
- **Illiquid futures/forex sessions or thin crypto pairs** — spread + 24h
  session quirks break the session/volume assumptions.

If a symbol spends most of its time with **ADX < 20** or **ATR% > the ceiling**,
it is the wrong instrument for this strategy.

---

## 5. Per-asset-class tuning guide

Start from defaults, then adjust per class. (All are inputs with tooltips.)

### A) High-volatility tech / leveraged ETFs (NVDA, TSLA, SMH, TQQQ, SOXL)
- **Risk per Trade:** lower to **0.5%** (leveraged ETFs: 0.25–0.5%).
- **Max ATR% (vol filter):** raise to **10–14%** (these are *normally* volatile).
- **ATR Stop Mult:** widen to **2.5–3.0** so normal noise doesn't stop you out.
- **ADX Min:** keep **20–22**.
- **Chandelier Mult:** **3.5–4.0** to give the runner room.
- **Long Threshold:** keep strict (**3.0–4.0**) — you want strong confluence.
- Timeframe: **1H** swing.

### B) Broad-index ETFs (SPY, QQQ, IWM, DIA)
- **Risk per Trade:** **1%** (default).
- **Max ATR%:** lower to **3–5%** (these are smooth; high ATR% = real stress).
- **ATR Stop Mult:** **1.5–2.0** (tighter, trends are smoother).
- **ADX Min:** **18–20** (index trends register lower ADX than single stocks).
- **HTF Filter:** keep ON; **Market Filter** can stay OFF (SPY *is* the market).
- **Long Threshold:** **2.5–3.0** (slightly looser is fine; trends are reliable).
- Timeframe: **1H–Daily**.

### C) Lower-volatility large caps / defensives (AAPL, MSFT, JNJ, PG, XLV, XLP)
- **Risk per Trade:** **1%**.
- **Max ATR%:** **3–4%**.
- **ATR Stop Mult:** **1.5–2.0**.
- **ADX Min:** **22–25** (demand a clearer trend before committing).
- **Volume Spike x:** **1.3–1.5** (moves are quieter; don't over-demand spikes).
- **Take-Profit:** consider **TP1 1R / TP2 2.5–3R** — these grind, so let
  winners run a bit further with the trail.
- Timeframe: **Daily** position trades or **4H** swing.

### General rules
- **Enable the Market Filter (SPY)** for single stocks to avoid longs in
  risk-off tape; leave it OFF for SPY/QQQ themselves.
- **Adaptive weighting:** leave OFF until you have **30+ closed trades** in your
  IS window; then enable and re-check **OOS** — if OOS degrades, the adaptation
  overfit; turn it back off.
- Always re-validate on the **OOS** window after any tuning.

---

## 6. Module map (where each requirement lives in the code)

| Module | What it does | Key inputs group |
|---|---|---|
| 1 | Weighted confluence engine (10 scored indicators, ADX/ATR gates) | `10/11/12/13/14` |
| 2 | HTF trend filter + regime detection + optional SPY market filter | `20` |
| 3 | ATR/structure stop, 1R/2R partial TPs, chandelier trail, time exit | `30` |
| 4 | Risk-based sizing, daily cap, cooldown, pyramiding, DD circuit breaker, session/weekday filter | `40/41` |
| 5 | Walk-forward IS/OOS date windows + active-window restriction + reporting | `50` |
| 6 | Adaptive heuristic weighting (bounded, warm-up, master toggle) | `60` |
| 7 | Compact per-trade export log table (entry/exit/dir/prices/stop/bitmask/PnL/R/regime) | `80` |
| 8 | Markers, SL/TP lines, confluence breakdown table, performance table | `80` |
| 9 | `alert()` (dynamic, webhook-ready) on entries + `alertcondition()` entry/exit | n/a |

### Trade-log "Mask" column (Module 7)
The `Mask` value is a **bitmask of which indicators agreed with the trade
direction at entry** (bit `i` set ⇒ indicator `i` fired):

```
bit0 EMA  bit1 Ichimoku  bit2 Supertrend  bit3 RSI  bit4 MACD
bit5 Stoch  bit6 Bollinger  bit7 VWAP  bit8 OBV  bit9 VolSpike
```

Decode in Python with `for i in range(10): fired = bool(mask >> i & 1)`. Copy
the log table rows (entry/exit time, direction, prices, stop, mask, PnL, R,
regime) into your external pipeline to train a real model **out-of-sample**.

---

## 7. Compliance checklist (HARD CONSTRAINTS)

- [x] Pine v6, `strategy()`, `ta./request./array.` namespaces, no v4/v5 syntax.
- [x] No repaint / no lookahead: `barstate.isconfirmed` + `lookahead_off`.
- [x] Realistic costs: `commission_type=strategy.commission.percent`,
      `commission_value` (0.03% default), `slippage` (2 ticks default) — all inputs.
- [x] `calc_on_every_tick=false`, `max_bars_back=5000`.
- [x] Every parameter is an `input()` with `group=` and `tooltip=`.
- [x] Long-only / short-only / both toggle (default Long Only).
- [x] No deprecated functions; adaptive layer is **not** called ML/AI; no profit promises.
