"""Module 7 - 20-year backtest of Top-N SPDR momentum vs SPY buy-and-hold.

Pulls weekly adjusted closes for the 11 SPDR sector ETFs + SPY, then runs
a simple monthly top-N momentum strategy. Parameters are interactive so the
student can build intuition for how K, lookback, and costs change results.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.page import bootstrap
from utils.style import page_header
from utils.quiz import render_quiz
from utils.market import SECTORS, SECTOR_TICKERS, BENCHMARK, get_prices
from utils.backtest import (
    top_n_momentum_backtest,
    equity_curve_figure,
    drawdown_figure,
    holdings_heatmap,
)


bootstrap("מודול 7 – Backtest")
page_header(
    "🧪 מודול 7 – Backtest ל-20 שנה",
    "אסטרטגיית Top-N מומנטום על סקטורי SPDR מול S&P 500 buy-and-hold",
)


# ---------------------------- OPENING ----------------------------

st.markdown(
    """
למדת את התיאוריה. **עובד?** לפניך Backtest של 20 שנה של הכלל הפשוט ביותר ב-Sector Rotation:
בכל סוף חודש מחזיקים את **N הסקטורים** עם המומנטום הגבוה ביותר ב-X חודשים אחרונים, במשקלים שווים.
משווים ל-S&P 500 (SPY) buy-and-hold.

> **ספוילר:** זה עובד. אבל לא תמיד, לא בהרבה, ולא בלי כאב. ה-Backtest מציג את זה כן.
"""
)


# ---------------------------- SECTION 1: THE STRATEGY ----------------------------

st.markdown("### 1. האסטרטגיה במשפט אחד")
st.markdown(
    """
- **יקום:** 11 סקטורי SPDR (SPY **לא** ביקום – הוא רק הבנצ'מארק).
- **סיגנל:** תשואה כוללת ב-N חודשים אחרונים, נמדדת בסוף כל חודש.
- **אחזקה:** Top-K סקטורים, משקלים שווים, רי-בלאנס חודשי.
- **עלויות:** bps לכל רי-בלאנס, מוכפלים ב-turnover (מרחק L1 בין משקלים).
- **בנצ'מארק:** SPY buy-and-hold.
- **שים לב:** זוהי גרסה פשוטה. אסטרטגיות פרודקשן מוסיפות סינון תנודתיות, regime overlays, risk parity ועוד.
"""
)


# ---------------------------- SECTION 2: PARAMETERS ----------------------------

st.markdown("### 2. פרמטרים")
st.caption("שנה את הסליידרים – הכל מתחשב מחדש בזמן אמת.")

p1, p2 = st.columns(2)
with p1:
    K = st.slider("מספר סקטורים להחזיק (Top-N)", 1, 6, 3)
    cost_bps = st.slider("עלויות עסקה (bps לרי-בלאנס)", 0, 50, 5)
with p2:
    lookback = st.slider("חלון מומנטום (חודשים)", 1, 12, 6)
    years = st.slider("שנים אחורה", 5, 25, 20)


# ---------------------------- SECTION 3: RUN BACKTEST ----------------------------

period_str = f"{years}y"
tickers = SECTOR_TICKERS + [BENCHMARK]

try:
    with st.spinner("שולף נתוני שערים מ-Yahoo Finance..."):
        prices = get_prices(tickers, period=period_str, interval="1wk")
except Exception as exc:  # noqa: BLE001
    st.error(f"שגיאה בשליפת נתוני שערים מ-Yahoo: {exc}. נסה לרענן.")
    st.stop()

if prices is None or prices.empty:
    st.error("שגיאה בשליפת נתוני שערים מ-Yahoo. נסה לרענן.")
    st.stop()

result = top_n_momentum_backtest(
    prices,
    benchmark=BENCHMARK,
    n=K,
    lookback_months=lookback,
    cost_bps=float(cost_bps),
)

if result["equity"].empty:
    st.warning("אין מספיק נתונים לתקופה הנבחרת — נסה תקופה ארוכה יותר.")
    st.stop()


# ---------------------------- SECTION 4: HEADLINE STATS ----------------------------

st.markdown("### 3. סטטיסטיקות מרכזיות")

stats = result["stats"]
s = stats["strategy"]
b = stats["benchmark"]
excess_cagr = s["cagr"] - b["cagr"]


def _fmt_pct(v: float, signed: bool = False) -> str:
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    return f"{v * 100:+.1f}%" if signed else f"{v * 100:.1f}%"


def _fmt_num(v: float) -> str:
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    return f"{v:.2f}"


stats_table = pd.DataFrame(
    {
        "מדד": [
            "תשואה כוללת",
            "תשואה שנתית (CAGR)",
            "תנודתיות שנתית",
            "Sharpe (rf=0)",
            "Max Drawdown",
            "Hit Rate (חודשים חיוביים)",
        ],
        "אסטרטגיה": [
            _fmt_pct(s["total_return"]),
            _fmt_pct(s["cagr"]),
            _fmt_pct(s["vol_ann"]),
            _fmt_num(s["sharpe"]),
            _fmt_pct(s["max_drawdown"]),
            _fmt_pct(s["hit_rate"]),
        ],
        "SPY (בנצ'מארק)": [
            _fmt_pct(b["total_return"]),
            _fmt_pct(b["cagr"]),
            _fmt_pct(b["vol_ann"]),
            _fmt_num(b["sharpe"]),
            _fmt_pct(b["max_drawdown"]),
            _fmt_pct(b["hit_rate"]),
        ],
    }
)

st.dataframe(stats_table, hide_index=True, use_container_width=True)

m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Excess CAGR vs SPY", _fmt_pct(excess_cagr, signed=True))
with m2:
    delta_sharpe = s["sharpe"] - b["sharpe"]
    st.metric("Δ Sharpe", f"{delta_sharpe:+.2f}")
with m3:
    delta_dd = s["max_drawdown"] - b["max_drawdown"]
    st.metric("Δ Max Drawdown", _fmt_pct(delta_dd, signed=True))


# ---------------------------- SECTION 5: EQUITY CURVE ----------------------------

st.markdown("### 4. עקומת הון")
st.plotly_chart(equity_curve_figure(result["equity"]), use_container_width=True)

if excess_cagr > 0.005:
    verdict = "ניצחה את הבנצ'מארק"
elif excess_cagr < -0.005:
    verdict = "פיגרה אחרי הבנצ'מארק"
else:
    verdict = "הדביקה את הבנצ'מארק בערך"

st.markdown(
    f"בתקופה שנבחרה האסטרטגיה **{verdict}**: "
    f"{_fmt_pct(s['cagr'])} שנתי לעומת {_fmt_pct(b['cagr'])} ל-SPY "
    f"(הפרש של {_fmt_pct(excess_cagr, signed=True)} בשנה)."
)


# ---------------------------- SECTION 6: DRAWDOWNS ----------------------------

st.markdown("### 5. Drawdowns")
st.plotly_chart(drawdown_figure(result["equity"]), use_container_width=True)

equity_df = result["equity"]
strat_dd = equity_df["strategy"] / equity_df["strategy"].cummax() - 1.0
worst_dd_date = strat_dd.idxmin()
worst_dd_str = (
    worst_dd_date.strftime("%Y-%m") if isinstance(worst_dd_date, pd.Timestamp) else "—"
)

st.markdown(
    f"ה-Drawdown החריף ביותר של האסטרטגיה היה **{_fmt_pct(s['max_drawdown'])}** סביב **{worst_dd_str}**, "
    f"לעומת **{_fmt_pct(b['max_drawdown'])}** ל-SPY. "
    "כשהשוק נופל בחדות, רוטציה לא תציל אותך — היא **מקטינה את הסיכון אבל לא מבטלת אותו**."
)


# ---------------------------- SECTION 7: HOLDINGS HEATMAP ----------------------------

st.markdown("### 6. מי הוחזק, מתי")
sector_names_he = {t: SECTORS[t]["name_he"] for t in SECTOR_TICKERS}
st.plotly_chart(
    holdings_heatmap(result["holdings"], sector_names_he),
    use_container_width=True,
)

holdings = result["holdings"]
if not holdings.empty:
    held_pct = (holdings > 0).mean().sort_values(ascending=True) * 100
    most_held = held_pct.idxmax()
    most_held_pct = held_pct.max()
    label_map = {t: f"{t} · {SECTORS[t]['name_he']}" for t in held_pct.index}
    held_df = pd.DataFrame(
        {
            "מגזר": [label_map[t] for t in held_pct.index],
            "% מהחודשים שבהם הוחזק": held_pct.values,
        }
    )
    bar = go.Figure(
        go.Bar(
            x=held_df["% מהחודשים שבהם הוחזק"],
            y=held_df["מגזר"],
            orientation="h",
            marker_color="#2563eb",
            text=[f"{v:.0f}%" for v in held_df["% מהחודשים שבהם הוחזק"]],
            textposition="outside",
        )
    )
    bar.update_layout(
        height=max(320, 26 * len(held_df) + 80),
        margin=dict(l=10, r=30, t=20, b=10),
        xaxis=dict(range=[0, 100], ticksuffix="%", showgrid=True, gridcolor="rgba(0,0,0,0.05)"),
        yaxis=dict(autorange="reversed"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False,
    )
    st.plotly_chart(bar, use_container_width=True, config={"displayModeBar": False})

    st.markdown(
        f"הסקטור שהוחזק הכי הרבה: **{label_map[most_held]}** ({most_held_pct:.0f}% מהחודשים). "
        "ריכוזיות גבוהה בסקטור אחד אומרת שהאסטרטגיה למעשה רכבה על trend ארוך-טווח, "
        "לא 'הסתובבה' בין סקטורים בכל חודש."
    )


# ---------------------------- SECTION 8: WHAT THIS DOES NOT TELL YOU ----------------------------

st.markdown("### 7. מה ה-Backtest הזה **לא** אומר לך")
st.markdown(
    """
- **Survivorship & coverage:** XLC (תקשורת) נוצר רק ב-2018. לפני זה, מניות תקשורת היו בתוך XLK ו-XLY. ה-Backtest מתייחס ליקום של היום כאל יקום היסטורי — וזה לא מדויק.
- **Look-ahead bias:** מינימלי כאן (משתמשים במחירי סוף-חודש לרי-בלאנס שמתבסס על מידע שזמין במועד), אבל מימוש אמיתי דורש זהירות בתזמון EOD/SOD.
- **מסים:** אפס. חשבון רגיל (לא קרן השתלמות / IRA) יאבד 0.5%–2.0% בשנה ל-short-term capital gains.
- **Slippage / impact:** אפס. עבור חשבון קטן ה-slippage נמוך אבל לא אפס.
- **שבריריות regime:** תוצאות 2004–2024 לאו דווקא משתחזרות ב-regime עתידי שונה (ריבית גבוהה, אינפלציה מתמשכת, geopolitical fragmentation).
- **בלי ריבית חסרת סיכון:** Sharpe מחושב עם rf=0 — מוטה כלפי מעלה בתקופות של תשואה גבוהה ל-T-Bills.
- **מזל סטטיסטי:** 20 שנה = ~240 תצפיות חודשיות. עם בחירת 3 מתוך 11, גודל המדגם צנוע. **המובהקות הסטטיסטית חלשה.**
"""
)


# ---------------------------- SECTION 9: SENSITIVITY ----------------------------

st.markdown("### 8. ניתוח רגישות (אופציונלי)")
st.caption("בודק 9 קומבינציות של K ו-lookback. ייקח 10–30 שניות בכניסה הראשונה.")

if st.button("הרץ ניתוח רגישות"):
    k_grid = [2, 3, 4]
    lb_grid = [3, 6, 12]
    rows = []
    progress = st.progress(0.0)
    total = len(k_grid) * len(lb_grid)
    idx = 0
    for k_val in k_grid:
        for lb_val in lb_grid:
            res = top_n_momentum_backtest(
                prices,
                benchmark=BENCHMARK,
                n=k_val,
                lookback_months=lb_val,
                cost_bps=float(cost_bps),
            )
            st_s = res["stats"]["strategy"]
            bn_s = res["stats"]["benchmark"]
            rows.append(
                {
                    "K (Top-N)": k_val,
                    "Lookback (חודשים)": lb_val,
                    "CAGR": _fmt_pct(st_s["cagr"]),
                    "Vol שנתי": _fmt_pct(st_s["vol_ann"]),
                    "Sharpe": _fmt_num(st_s["sharpe"]),
                    "Max DD": _fmt_pct(st_s["max_drawdown"]),
                    "Excess vs SPY": _fmt_pct(st_s["cagr"] - bn_s["cagr"], signed=True),
                }
            )
            idx += 1
            progress.progress(idx / total)
    progress.empty()
    sens_df = pd.DataFrame(rows)
    st.dataframe(sens_df, hide_index=True, use_container_width=True)
    st.caption(
        "טבלה זו מדגימה ש-Sharpe ו-CAGR יכולים להשתנות בעשרות נקודות בסיס בין קומבינציות סבירות. "
        "אם תוצאה רגישה מאוד לפרמטר, זה דגל אדום ל-overfitting."
    )


# ---------------------------- QUIZ ----------------------------

st.divider()
render_quiz(
    "module_7_backtest",
    [
        {
            "q": "למה ה-Sharpe ב-Backtest מוצג כאן 'גבוה מדי' בתיאוריה?",
            "options": [
                "כי משתמשים בנתונים חודשיים במקום יומיים",
                "כי הריבית חסרת הסיכון (rf) הוגדרה ל-0 — הפרמיה האמיתית נמוכה יותר",
                "כי לא מנכים מסים",
                "כי משתמשים ב-SPY במקום ב-VTI",
            ],
            "answer": 1,
            "explain": "Sharpe = (CAGR − rf) / vol. כאן rf=0. בתקופות של T-Bills סביב 4–5%, ה-Sharpe האמיתי נמוך משמעותית.",
        },
        {
            "q": "למה תוצאות 2004–2024 לאו דווקא ינבאו את 2024 ואילך?",
            "options": [
                "כי yfinance לא אמין",
                "כי משטר השוק (regime) משתנה: ריבית, אינפלציה, מבנה השוק, התנהגות משקיעים",
                "כי SPDR כבר לא קיים",
                "כי המודל מסתכל רק על מומנטום",
            ],
            "answer": 1,
            "explain": "Regime change: 2004–2021 = ריבית יורדת/אפס. 2022+ = ריבית גבוהה, אינפלציה מתמשכת. אסטרטגיה שעבדה ב-regime אחד לא מובטחת ב-regime אחר.",
        },
        {
            "q": "ה-cost_bps מוכפל ב-turnover (מרחק L1 בין משקלים). למה?",
            "options": [
                "כדי לחשב מסים",
                "כדי להעריך את חיכוך הרי-בלאנס — אתה משלם רק על מה שמשתנה בתיק",
                "כדי לעקוב אחרי volatility",
                "כדי להגדיל את ה-Sharpe באופן מלאכותי",
            ],
            "answer": 1,
            "explain": "אם המשקלים זהים בין חודש לחודש — turnover=0 — לא משלמים כלום. רק שינוי בפועל עולה כסף (עמלות, ספרד, slippage).",
        },
        {
            "q": "להגדיל את K (להחזיק יותר סקטורים) — מה הצפי?",
            "options": [
                "מעלה את התנודתיות בגלל ריכוזיות",
                "מוריד תנודתיות בגלל פיזור — והאסטרטגיה מתקרבת ל-SPY",
                "לא משפיע על כלום",
                "תמיד מעלה את ה-CAGR",
            ],
            "answer": 1,
            "explain": "ככל ש-K גדל, התיק מפוזר יותר. בגבול K=11 הוא בעצם משוקלל שווה את כל הסקטורים — קרוב מאוד ל-SPY. פחות תנודתיות, פחות edge.",
        },
        {
            "q": "XLC נוצר רק ב-2018. למה זו בעיה ב-Backtest של 20 שנה?",
            "options": [
                "אין בעיה — yfinance מספיק חכם",
                "Survivorship/coverage bias: לפני 2018 מניות תקשורת היו ב-XLK ו-XLY — היקום הסקטוריאלי ההיסטורי שונה מהיום",
                "XLC זול מדי",
                "כי XLC הוא לא ETF אמיתי",
            ],
            "answer": 1,
            "explain": "Reclassifications של S&P משנות את התוכן של ה-ETFs. Backtest שמניח את היקום של היום זהה ליקום של 2005 — מציג עבר שמעולם לא היה זמין למשקיע אמיתי.",
        },
    ],
)
