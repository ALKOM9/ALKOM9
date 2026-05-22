"""Module 6 - Implementation: three ways to express a sector view.

Walks the student through overweight tilt, long-short, and pure momentum
implementations, and includes an interactive position-sizing calculator
so a mobile learner can see what a $X portfolio would look like.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.page import bootstrap
from utils.style import page_header
from utils.quiz import render_quiz
from utils.market import SECTORS, SECTOR_TICKERS
from utils.cycle import phase_to_sectors, PHASE_LABELS_HE


bootstrap("מודול 6 – יישום")
page_header(
    "🛠️ מודול 6 – איך מבטאים תזה סקטוריאלית",
    "שלוש גישות, ממסורתית לאגרסיבית, + מחשבון פוזיציות אינטראקטיבי",
)

# ---------------------------- OPENING ----------------------------
st.markdown(
    """
אתה כבר מבין את המחזור (מודול 1), את הסקטורים (מודול 2), את הרוטציה הקלאסית (מודול 3),
ויודע לקרוא את המאקרו וה-RRG (מודולים 4–5). עכשיו השאלה הקריטית:

> **איך מתרגמים תזה לפוזיציות אמיתיות?**

המודול הזה מציג שלוש גישות, מהשמרנית לאגרסיבית – ומאפשר לך לראות איך תיק של $X יראה
תחת כל אחת מהן. המטרה היא לא לסחור עכשיו, אלא להבין את הטרייד-אוף בין פשטות, סיכון ועלות.
"""
)

# ---------------------------- SECTION 1: THREE STYLES ----------------------------
st.markdown("### 1. שלוש גישות יישום – מבט-על")
approaches_df = pd.DataFrame(
    [
        {"גישה": "Overweight tilt", "תיאור": "תיק core+satellite, הטיית משקל קלה לפי השלב",
         "סיכון": "נמוך", "יתרון": "פשוט, יציב, חוסך מס", "חיסרון": "מומנט קטן, תלות בליבה"},
        {"גישה": "Long-Short", "תיאור": "לונג בסקטור המוביל / שורט בסקטור פיגר",
         "סיכון": "בינוני-גבוה", "יתרון": "dollar-neutral, מקטין סיכון שוק",
         "חיסרון": "עלויות שורט, מס, מורכבות"},
        {"גישה": "Pure Momentum", "תיאור": "החזק רק את 3–5 הסקטורים המובילים, מחזר חודשית",
         "סיכון": "גבוה", "יתרון": "תפיסת מומנטום מלאה",
         "חיסרון": "תנודתי, drawdowns חדים, מס"},
    ]
)
st.dataframe(approaches_df, hide_index=True, use_container_width=True)
st.caption(
    "אין גישה אחת 'נכונה'. הבחירה תלויה בגודל התיק, סוג החשבון (חייב-מס מול פטור), "
    "הזמן שאתה מוכן להקדיש לניהול, ובסיבולת ל-drawdown."
)

# ---------------------------- SECTION 2: OVERWEIGHT ----------------------------
st.divider()
st.markdown("### 2. גישה 1 – Overweight Tilt (השמרנית)")
st.markdown(
    """
הגישה הכי ידידותית למשקיע ביתי. רעיון: לבנות **תיק core + satellite**:

- **Core (60–80%)** – SPY (או VTI), חשיפה רחבה לשוק האמריקאי.
- **Satellite (20–40%)** – ETF סקטוריאליים, מוטים לפי שלב המחזור.

**דוגמה: תיק $10K, שלב 'סוף מחזור':** Core $7,000 SPY. Satellite $3,000: $1,500 XLE,
$1,000 XLV, $500 XLP. מוכר/נמנע מ-XLY ו-XLRE (Underweight בשלב הזה).

**יתרונות:** נשאר מפוזר, turnover נמוך → פחות עמלות ומס, סטייה צנועה מהמדד → tracking
error נמוך → פחות פגיעה רגשית כשהמדד עולה והטיה לא עובדת.

**חסרונות:** תופס רק חלק קטן מאלפא הרוטציה; מוסיף מורכבות לתיק שיכול היה להיות פשוט SPY;
אם ההטיה קטנה מדי – הרעש בולע אותה.
"""
)

# ---------------------------- INTERACTIVE CALCULATOR ----------------------------
st.markdown("#### 🧮 מחשבון פוזיציות אינטראקטיבי")
st.caption(
    "הכנס סך תיק, אחוז ליבה, ושלב המחזור הנוכחי – המחשבון יציג את הפוזיציות המומלצות. "
    "כלי לימודי בלבד, לא ייעוץ השקעות."
)

col_a, col_b = st.columns(2)
with col_a:
    total_usd = st.number_input(
        "סך תיק (USD)", min_value=500, max_value=10_000_000,
        value=10_000, step=500, key="calc_total",
    )
with col_b:
    phase_options = ["early", "mid", "late", "recession"]
    phase_choice = st.selectbox(
        "שלב מחזור נוכחי", options=phase_options,
        format_func=lambda p: PHASE_LABELS_HE[p], index=2, key="calc_phase",
    )

core_pct = st.slider(
    "אחוז ליבה (SPY) מתוך התיק",
    min_value=50, max_value=90, value=70, step=5, key="calc_core",
)

tilts = phase_to_sectors(phase_choice)
ow_list = tilts["overweight"]
uw_list = tilts["underweight"]

core_usd = total_usd * core_pct / 100.0
satellite_usd = total_usd - core_usd
# 70% of satellite → equal across OW; 30% → cash buffer.
ow_basket_usd = satellite_usd * 0.70
cash_usd = satellite_usd * 0.30

rows: list[dict] = [
    {"טיקר": "SPY", "תפקיד": "Core",
     "סכום ($)": round(core_usd, 2), "אחוז": f"{core_pct:.1f}%"}
]
if ow_list:
    per_ow = ow_basket_usd / len(ow_list)
    for t in ow_list:
        meta = SECTORS.get(t, {"name_he": t, "emoji": ""})
        rows.append({
            "טיקר": f"{meta['emoji']} {t}",
            "תפקיד": f"OW – {meta['name_he']}",
            "סכום ($)": round(per_ow, 2),
            "אחוז": f"{per_ow / total_usd * 100:.1f}%",
        })
else:
    cash_usd += ow_basket_usd  # nothing to overweight → all to cash
for t in uw_list:
    meta = SECTORS.get(t, {"name_he": t, "emoji": ""})
    rows.append({
        "טיקר": f"{meta['emoji']} {t}",
        "תפקיד": f"UW – {meta['name_he']} (נמנע)",
        "סכום ($)": 0.0, "אחוז": "0.0%",
    })
rows.append({
    "טיקר": "Cash", "תפקיד": "כרית נזילות",
    "סכום ($)": round(cash_usd, 2),
    "אחוז": f"{cash_usd / total_usd * 100:.1f}%",
})

positions_df = pd.DataFrame(rows)
st.dataframe(positions_df, hide_index=True, use_container_width=True)
if not ow_list and not uw_list:
    st.info("בשלב לא ודאי – שב במדד רחב, חכה לסיגנל חזק יותר.")
st.caption(
    "כלל ההקצאה: ליבה לפי הסליידר ב-SPY. מהיתרה – 70% מפוזר שווה בין סקטורי OW, "
    "30% מזומן. סקטורי UW מקבלים 0% (נמנע/מוכר)."
)

# ---------------------------- SECTION 3: LONG-SHORT ----------------------------
st.divider()
st.markdown("### 3. גישה 2 – Long-Short (האקטיבית)")
st.markdown(
    """
מצמידים את הסקטור החזק ביותר לחלש ביותר. דוגמה: **לונג XLE, שורט XLY**, בסכום שווה
($5,000 כל רגל). התוצאה: חשיפה דולרית נטו 0 → **dollar-neutral**, ובקירוב גם
**market-beta-neutral** (כי שני ה-ETFs נושאים בטא דומה לשוק).

הספרד תופס את ההפרש היחסי – אם XLE עולה 8% ו-XLY עולה 3%, אתה מרוויח ~5% על הספרד,
**בלי תלות בכיוון השוק**.

**עלויות וסיכונים:**
- **שורט דורש חשבון מרג'ין.** ברוקרים זרים (IBKR, TastyTrade) – זמין; ברוקרים ישראלים – לרוב לא.
- **Borrow fee** – בד"כ 50–200 bps לשנה על ETFs נזילים, יכול לקפוץ במצבי לחץ.
- **Wash-sale rules** (ארה"ב) – הפסדים בקיזוז מס נחסמים אם קונים מחדש בתוך 30 יום.
- **דיבידנדים** – אתה משלם dividends במקום לקבל, ו**לא** מקבל qualified rate.
- **מס:** רווחים על שורט בארה"ב תמיד **short-term** (מס הכנסה רגיל).

**Sizing rule of thumb:** ספרד יחיד = 5–15% מ-NLV של התיק; Stop = 1.5× סטיית התקן
הצפויה של הספרד על אופק ההחזקה.
"""
)

# Synthetic dollar-neutral PnL chart - illustrative
dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=60, freq="B")
spy_curve = pd.Series([100 - (i / 59) * 10 for i in range(60)], index=dates)
xle_curve = pd.Series([100 - (i / 59) * 6 for i in range(60)], index=dates)
xly_curve = pd.Series([100 - (i / 59) * 14 for i in range(60)], index=dates)
spread_ret = (xle_curve / 100 - 1) - (xly_curve / 100 - 1)
spread_curve = (1 + spread_ret) * 100

fig_ls = go.Figure()
fig_ls.add_trace(go.Scatter(x=spy_curve.index, y=spy_curve.values, mode="lines",
                            name="SPY (שוק)", line=dict(color="#888", width=2, dash="dot")))
fig_ls.add_trace(go.Scatter(x=xle_curve.index, y=xle_curve.values, mode="lines",
                            name="XLE (לונג)", line=dict(color="#2ecc71", width=2)))
fig_ls.add_trace(go.Scatter(x=xly_curve.index, y=xly_curve.values, mode="lines",
                            name="XLY (שורט)", line=dict(color="#e74c3c", width=2)))
fig_ls.add_trace(go.Scatter(x=spread_curve.index, y=spread_curve.values, mode="lines",
                            name="ספרד Long-Short", line=dict(color="#1f77b4", width=3)))
fig_ls.update_layout(
    height=320, margin=dict(l=10, r=10, t=30, b=10),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    title="המחשה: שוק יורד 10%, אבל הספרד מרוויח ~4%",
    legend=dict(orientation="h", y=-0.18),
    xaxis=dict(showgrid=False),
    yaxis=dict(title="אינדקס (התחלה=100)", showgrid=True,
               gridcolor="rgba(128,128,128,0.15)"),
)
st.plotly_chart(fig_ls, use_container_width=True,
                config={"displayModeBar": False, "scrollZoom": False, "displaylogo": False})
st.caption("נתונים סינתטיים – להמחשה בלבד. אינם מייצגים ביצועי עבר אמיתיים.")

# ---------------------------- SECTION 4: PURE MOMENTUM ----------------------------
st.divider()
st.markdown("### 4. גישה 3 – Pure Momentum / Top-N (האגרסיבית)")
st.markdown(
    """
הגישה הכי אגרסיבית: מתעלמים ממאקרו, ממחזור, מ-RRG. רק **תשואות עבר**.

**הכלל:** בכל סוף חודש, דרג את 11 סקטורי ה-SPDR לפי תשואת N החודשים האחרונים.
החזק את **Top-K** בלבד, במשקל שווה. מה שיצא מ-Top-K – נמכר. מה שנכנס – נקנה.

**פרמטרים שעבדו היסטורית:**
- **N (lookback)** – 3, 6, או 12 חודשים. הספרות האקדמית מעדיפה **6–12** חודשים
  ל-cross-sectional momentum סקטוריאלי (Jegadeesh & Titman, Asness et al.).
- **K (כמה להחזיק)** – 2–4. **K=3** הוא בחירה נפוצה: מספיק ריכוז כדי לתפוס trend,
  מספיק פיזור כדי שלא תיהרס מסקטור אחד.

**יתרונות:** מכני לחלוטין, אין שיפוט אנושי, אין הטיות רגשיות. תופס רוטציות גדולות
(XLE 2022, XLK 2023).

**חסרונות:** Whipsaws בנקודות מפנה – נכנס מאוחר, יוצא מאוחר. Turnover גבוה → עלויות
ומס. מוטה לסקטור 1–2 ב-trend ארוך (XLK שלט 2014–2020 ובלע את כל הסל). יכול להפסיד
למדד **שנים** ברצף.

> זה בדיוק מה שמודול 7 יבחן ב-backtest עם 20 שנות נתונים.
"""
)

# ---------------------------- SECTION 5: SIZING & RISK ----------------------------
st.divider()
st.markdown("### 5. Sizing וניהול סיכון – ללא קשר לגישה")
st.markdown(
    """
**Vol-scaling:** סקטור עם תנודתיות גבוהה יותר נושא יותר סיכון לאותו דולר.

| סקטור | סטיית תקן שנתית מוערכת | יחס ל-XLP |
|---|---|---|
| XLK (טכנולוגיה) | ~22% | 1.57× |
| XLE (אנרגיה) | ~28% | 2.00× |
| XLV (בריאות) | ~16% | 1.14× |
| XLP (Staples) | ~14% | 1.00× |
| XLU (Utilities) | ~15% | 1.07× |

כלומר, $1 ב-XLK שווה בערך **1.5×** הסיכון של $1 ב-XLP. משקל שווה ≠ סיכון שווה.
מקצוענים עושים **inverse-vol weighting** או **risk-parity**.

**Stop Loss:** בפוזיציה סקטוריאלית בודדה – 8–15% מתחת לעלות. בספרד Long-Short – 5–8%
על הספרד עצמו (לא על כל רגל).

**מגבלות פוזיציה:** אף סקטור יחיד לא יעבור **25% מהתיק** (כלל אצבע נגד concentration risk).

**תדירות איזון:** **חודשית** = נקודה מתוקה. שבועית = רעש ועלויות. רבעונית = מפספס נקודות מפנה.
"""
)

# ---------------------------- SECTION 6: TAX ----------------------------
st.divider()
st.markdown("### 6. שיקולי מס")
st.markdown(
    """
**חשבון חייב-מס (Taxable, ארה"ב):** כל איזון מפיק רווח/הפסד חייבים. **Wash-sale** חוסם
הפסדים אם קונים את אותו ETF (או דומה מאוד) בתוך 30 יום. מס על רווחים קצרי טווח (< שנה)
= מס הכנסה רגיל. ארוך טווח = 15–20%. **Pure Momentum** עם איזון חודשי = כמעט תמיד רווחים
קצרי טווח → מס גבוה.

**חשבון פטור-מס (IRA, 401k, או בישראל: קרן השתלמות, קופת גמל IRA):** אין מס שוטף.
Pure Momentum **ישים** בלי קנס מס. זה ההבדל המעשי הכי גדול בין הגישות.

**הערה למשקיע הישראלי:** כללי המיסוי שונים מארה"ב. רווחי הון נומינליים מסקטור זר חייבים
במס 25% (וצמודים לדולר). **הקורס הזה אינו ייעוץ מס.** ודא היכן הקרן ממוקמת ומה היציאה
ממנה גוררת. קרן השתלמות נזילה, IRA פרטית, קופת גמל IRA – כולן מאפשרות מסחר פטור מס שוטף.
"""
)

# ---------------------------- SECTION 7: BROKERS ----------------------------
st.divider()
st.markdown("### 7. ברוקרים וכלים (קונטקסט ישראלי)")
st.markdown(
    """
**SPDR Sector ETFs (XLB, XLC, … XLY):** זמינים בכל ברוקר אמריקאי – **IBKR, TastyTrade,
Schwab, Fidelity**. עמלות זעירות (לפעמים $0), ספרדים צרים, נזילות אדירה.

**ברוקרים ישראלים:** חיוב גבוה על השקעות זרות, עמלות מטבע, ולעיתים אין גישה לשורט.
אם הסכום קטן – **עדיין IBKR**. עלות פתיחת חשבון $0, מינימום הפקדה $0.

**מינימום השקעה:** SPY נסחר ב-~$500–600 ליחידה. XLE ~$80, XLK ~$200, XLP ~$80.
**שברי מניות (fractional)** זמינים ב-IBKR Pro – מאפשרים לבנות תיק $1,000 עם הטיות.

**טיפ פרקטי:** התחל ב-paper trading (חשבון דמו ב-IBKR) במשך 1–3 חודשים. תרגם את החלטות
מודול 4 לפוזיציות במחשבון של מודול 6, פתח אותן בדמו, ועקוב. רק אחרי שזה זורם – עבור לכסף
אמיתי, בסכומים קטנים.
"""
)

# ---------------------------- WRAP-UP ----------------------------
st.divider()
st.info(
    "**איפה אתה עכשיו:** הבנת את הגישות. הצעד הבא – מודול 7 (Backtest) – בודק את "
    "Pure Momentum על 20 שנות נתונים אמיתיים, ומראה איפה הוא עובד ואיפה הוא נכשל בענק."
)

# ---------------------------- QUIZ ----------------------------
st.divider()
QUIZ_QUESTIONS = [
    {
        "q": "איזו גישה נחשבת לרוב לכי יעילה מבחינת מס לאורך שנה?",
        "options": [
            "Overweight tilt – turnover נמוך מאוד",
            "Long-Short – יוצר הרבה אירועי מס",
            "Pure Momentum – איזון חודשי מייצר רווחים קצרי טווח",
            "כולן זהות מבחינת מס",
        ],
        "answer": 0,
        "explain": "Overweight tilt עם איזון רבעוני/חודשי שומר על turnover נמוך, ולכן פחות אירועי מס.",
    },
    {
        "q": "מדוע פוזיציית Long-Short נחשבת market-neutral?",
        "options": [
            "כי שני הסקטורים יושבים באותה תעשייה",
            "כי החשיפות הדולריות מתקזזות – אין חשיפה נטו לכיוון השוק",
            "כי השורט תמיד מרוויח",
            "כי משתמשים ב-options ולא ב-ETFs",
        ],
        "answer": 1,
        "explain": "$ שווה לונג + $ שווה שורט = חשיפה נטו 0. הספרד תופס רק את ההפרש היחסי.",
    },
    {
        "q": "מהו lookback אופייני ב-cross-sectional momentum סקטוריאלי?",
        "options": ["1–2 שבועות", "1 חודש", "6–12 חודשים", "5 שנים"],
        "answer": 2,
        "explain": "הספרות האקדמית (Jegadeesh & Titman, Asness) ממליצה על 6–12 חודשים.",
    },
    {
        "q": "למה משקל דולרי שווה ≠ סיכון שווה בין סקטורים?",
        "options": [
            "כי הדיבידנדים שונים",
            "כי לסקטורים שונים סטיות תקן (volatility) שונות",
            "כי העמלות שונות",
            "כי המס שונה",
        ],
        "answer": 1,
        "explain": "XLK עם vol ~22% נושא יותר סיכון מ-XLP עם vol ~14% – לאותו דולר.",
    },
    {
        "q": "מה הגודל המתאים לחשיפה הסקטוריאלית עבור משקיע מתחיל?",
        "options": [
            "100% מהתיק – להאמין בתזה במלואה",
            "מוגבל; זה satellite, לא core. רוב התיק נשאר במדד רחב",
            "אף פעם לא להחזיק סקטורים – רק SPY",
            "תלוי רק בגיל המשקיע",
        ],
        "answer": 1,
        "explain": "ההטיה הסקטוריאלית היא satellite (20–40% מהתיק). הליבה נשארת מדד רחב.",
    },
]
render_quiz("module_6", QUIZ_QUESTIONS)
