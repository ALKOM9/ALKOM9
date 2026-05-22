"""Module 5 - Relative Strength + Relative Rotation Graph (RRG).

Teaches RS from first principles in Hebrew, then introduces Julius de
Kempenaer's JdK methodology (RS-Ratio + RS-Momentum), and renders a live
RRG of the 11 SPDR sectors vs SPY.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.page import bootstrap
from utils.style import page_header
from utils.quiz import render_quiz
from utils.market import (
    SECTORS,
    SECTOR_TICKERS,
    BENCHMARK,
    get_sector_prices,
    relative_strength,
)
from utils.rrg import (
    compute_rrg,
    latest_rrg_point,
    quadrant,
    quadrant_label_he,
    plot_rrg,
)


bootstrap("מודול 5 – Relative Strength + RRG")
page_header(
    "📈 מודול 5 – כוח יחסי וגרף סיבוב (RRG)",
    "מהבסיס של RS ועד מתודולוגיית JdK של דה-קמפנר – וגרף חי של 11 המגזרים",
)

# --- Opening ---
st.markdown(
    """
כוח יחסי (Relative Strength, בקיצור **RS**) הוא הכלי המנוצל בחסר ביותר בעולם
ההשקעות הפרטיות. הוא עונה על שאלה פשוטה אחת:

> **האם נכס X מנצח כרגע את המדד המוביל, ובאיזה כיוון הפער זז?**

כשמרכיבים את *רמת* הכוח היחסי יחד עם *מומנטום* הכוח היחסי, אפשר לארוז את כל
מגזרי השוק לכדי תמונה דו-ממדית אחת – **גרף ה-RRG (Relative Rotation Graph)**.

זמן קריאה משוער: ~12 דקות.
"""
)

# --- Section 1: RS basics ---
st.markdown("## 1. הבסיס – מהו כוח יחסי?")
st.markdown(
    """
**הגדרה מתמטית:** $RS_t = P_t(\\text{נכס}) / P_t(\\text{מדד-יחס})$.
לרוב נורמלים כך ש-100 = הנקודה הראשונה.

**איך קוראים:**
- קו RS **עולה** → הנכס מנצח את המדד.
- קו RS **יורד** → הנכס מפסיד למדד, גם אם המחיר המוחלט עולה.
- קו RS **שטוח** → נע יחד עם המדד, אין מידע סקטוריאלי.

**הכלל הזהב:** ה*שיפוע* של RS הוא מה שמעניין, לא הרמה. שיפוע חיובי = כסף חכם
זורם פנימה. שיפוע שלילי = כסף יוצא, גם אם המחיר עוד בעלייה.
"""
)

# Live RS demo for a few sectors
st.markdown("### דוגמה חיה – XLK, XLE, XLV מול SPY")

DEMO_TICKERS = ["XLK", "XLE", "XLV"]
DEMO_COLORS = {"XLK": "#3b82f6", "XLE": "#ef4444", "XLV": "#10b981"}

rs_df: pd.DataFrame = pd.DataFrame()
try:
    prices_2y = get_sector_prices(period="2y", interval="1wk")
    if not prices_2y.empty and BENCHMARK in prices_2y.columns:
        rs_df = relative_strength(prices_2y, benchmark=BENCHMARK)
except Exception as exc:  # noqa: BLE001
    st.warning(f"שגיאה בשליפת מחירים: {exc}")

if rs_df.empty:
    st.info("נתונים חיים לא זמינים – מציג נתונים מודגמים.")
    idx = pd.date_range(end=pd.Timestamp.today(), periods=104, freq="W")
    rng = np.random.default_rng(42)
    rs_df = pd.DataFrame(
        {
            "XLK": 100 + np.cumsum(rng.normal(0.25, 1.0, len(idx))),
            "XLE": 100 + np.cumsum(rng.normal(-0.05, 1.4, len(idx))),
            "XLV": 100 + np.cumsum(rng.normal(0.05, 0.6, len(idx))),
        },
        index=idx,
    )

fig_rs = go.Figure()
for t in DEMO_TICKERS:
    if t in rs_df.columns:
        name_he = SECTORS.get(t, {}).get("name_he", t)
        fig_rs.add_trace(
            go.Scatter(
                x=rs_df.index,
                y=rs_df[t],
                mode="lines",
                name=f"{t} – {name_he}",
                line=dict(width=2, color=DEMO_COLORS[t]),
            )
        )
fig_rs.add_hline(y=100, line_dash="dot", line_color="#888", line_width=1)
fig_rs.update_layout(
    title=dict(text="RS יחסית ל-SPY (בסיס 100)", x=0.5),
    height=380,
    margin=dict(l=30, r=20, t=50, b=30),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    dragmode="pan",
    legend=dict(orientation="h", y=-0.18),
    modebar=dict(remove=["lasso2d", "select2d", "autoScale2d"]),
)
st.plotly_chart(fig_rs, use_container_width=True, config={"displaylogo": False})

st.caption(
    "שים לב: קו מעל 100 = ניצח את SPY מאז ההתחלה. שיפוע עולה בחלון האחרון = "
    "מנצח גם *עכשיו*."
)

st.divider()

# ============================================================
# SECTION 2 - JdK FORMULATION
# ============================================================
st.markdown("## 2. מ-RS לגרף RRG – הפורמולציה של JdK")
st.markdown(
    """
**הבעיה עם RS גולמי:** מספר אחד לזמן אחד – קשה להשוות 11 מגזרים בבת אחת.

**הפתרון של Julius de Kempenaer** (בלומברג, סוף שנות ה-2000): לפרק את ה-RS לשני
רכיבים מנורמלים סביב 100, ולצייר אותם על שני צירים מאונכים.

**1. JdK RS-Ratio – ציר X:**
$\\text{RS-Ratio} = 100 \\cdot (P/B) / \\overline{P/B}_{\\text{lookback}}$ —
*רמת* הכוח היחסי. מעל 100 = חזק יחסית, מתחת 100 = חלש.

**2. JdK RS-Momentum – ציר Y:** קצב השינוי של RS-Ratio, גם הוא סביב 100.
מעל 100 = ה-RS משתפר, מתחת ל-100 = הוא מתדרדר (גם אם עדיין גבוה).

### ארבעת הרבעים
"""
)

quadrant_table = pd.DataFrame(
    [
        {
            "רובע": "🟢 מובילים (Leading)",
            "מיקום": "ימין-עליון",
            "RS-Ratio": "> 100",
            "Momentum": "> 100",
            "פעולה": "להחזיק / Overweight",
        },
        {
            "רובע": "🟡 נחלשים (Weakening)",
            "מיקום": "ימין-תחתון",
            "RS-Ratio": "> 100",
            "Momentum": "< 100",
            "פעולה": "להקטין / Trim",
        },
        {
            "רובע": "🔴 פיגרים (Lagging)",
            "מיקום": "שמאל-תחתון",
            "RS-Ratio": "< 100",
            "Momentum": "< 100",
            "פעולה": "להימנע / Underweight",
        },
        {
            "רובע": "🔵 משתפרים (Improving)",
            "מיקום": "שמאל-עליון",
            "RS-Ratio": "< 100",
            "Momentum": "> 100",
            "פעולה": "מועמדים לקנייה",
        },
    ]
)
st.dataframe(quadrant_table, hide_index=True, use_container_width=True)

st.markdown(
    """
### סיבוב טיפוסי – נגד כיוון השעון

> **משתפרים → מובילים → נחלשים → פיגרים → משתפרים → ...**

לא תמיד חלק, אבל זה הקצב הבסיסי. **ה"זנב" (tail)** – N הנקודות השבועיות
האחרונות – מגלה לאן הסקטור פונה. מעבר מ"משתפרים" ל"מובילים" הוא ההתאוצה
השורית הקלאסית.
"""
)

st.divider()

# ============================================================
# SECTION 3 - LIVE RRG
# ============================================================
st.markdown("## 3. ה-RRG החי – 11 מגזרי SPDR מול SPY")

rrg_df: pd.DataFrame = pd.DataFrame()
prices_3y: pd.DataFrame = pd.DataFrame()
try:
    with st.spinner("שולף 3 שנות מחירים שבועיים מ-yfinance..."):
        prices_3y = get_sector_prices(period="3y", interval="1wk")
    if prices_3y.empty:
        st.warning("נתונים חיים לא זמינים כרגע. נסה לרענן בעוד דקה.")
    else:
        rrg_df = compute_rrg(
            prices_3y, benchmark=BENCHMARK, lookback=14, smoothing=10
        )
except Exception as exc:  # noqa: BLE001
    st.warning(f"שגיאה בחישוב RRG: {exc}")

if not rrg_df.empty:
    name_map = {t: SECTORS[t]["name_he"] for t in SECTOR_TICKERS}
    fig_rrg = plot_rrg(rrg_df, SECTOR_TICKERS, name_map, tail_length=8)
    fig_rrg.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(
        fig_rrg, use_container_width=True, config={"displaylogo": False}
    )

    # Summary table
    rows = []
    for t in SECTOR_TICKERS:
        try:
            rs_ratio, rs_mom = latest_rrg_point(rrg_df, t)
        except ValueError:
            continue
        q = quadrant(rs_ratio, rs_mom)
        rows.append(
            {
                "Ticker": t,
                "מגזר": SECTORS[t]["name_he"],
                "RS-Ratio": round(rs_ratio, 2),
                "Momentum": round(rs_mom, 2),
                "רובע": quadrant_label_he(q),
            }
        )
    if rows:
        st.markdown("### מצב נוכחי לכל מגזר")
        summary = pd.DataFrame(rows).sort_values("RS-Ratio", ascending=False)
        st.dataframe(summary, hide_index=True, use_container_width=True)
        st.caption(
            "הטבלה ניתנת למיון בלחיצה על כותרת עמודה. שים לב לפיזור בין הרבעים – "
            "ככל שיש יותר שונות, השוק במצב 'סיבוב' אקטיבי."
        )
else:
    st.info("טבלת המגזרים תוצג כשנתוני yfinance יחזרו להיות זמינים.")

st.divider()

# ============================================================
# SECTION 4 - HOW TO READ THE TAIL
# ============================================================
st.markdown("## 4. איך קוראים את הזנב")
st.markdown(
    """
- **אורך הזנב:** מקובל 6–10 שבועות. כאן נשתמש ב-8.
- **כל נקודה** היא צילום שבועי של (RS-Ratio, RS-Momentum) של אותו מגזר.
- **הכיוון חשוב יותר מהמיקום.** סקטור ב"פיגרים" עם זנב פונה *ימינה-למעלה* שורי
  יותר מסקטור ב"מובילים" עם זנב פונה *שמאלה-למטה*.
- **זנב מתפתל סביב (100, 100)** = נע יחד עם SPY. לא מעניין למסחר רוטציוני.
- **זנב המכסה מרחק גדול** = סקטור תנודתי. הזדמנות או אזהרה – תלוי בכיוון.
"""
)

st.divider()

# ============================================================
# SECTION 5 - READING PATTERNS
# ============================================================
st.markdown("## 5. תבניות קריאה נפוצות")
st.markdown(
    """
**הגירה המונית (Mass Migration).** קבוצת מגזרים שלמה נעה יחד בכיוון אחד.
טיפוסי כשהמאקרו מתחלף – למשל כל המחזוריים (XLY, XLF, XLI) עוברים יחד
מ"פיגרים" ל"משתפרים" כשהחלמה מתחילה.

**רוטציה נגדית (Counter-Rotation).** דפנסיביים (XLP, XLU, XLV) ב"מובילים"
בזמן שהמחזוריים יורדים ל"פיגרים". סימן קלאסי לפחד / סוף-מחזור / תחילת מיתון.

**זינוק אנרגיה (Energy Surge).** XLE קופץ מ"פיגרים" ל"מובילים" תוך 1–2 שבועות.
שכיח בראלי סחורות או הלם היצע (גיאו-פוליטיקה, OPEC). אינדיקטור סוף-מחזור.

**דומיננטיות טכנולוגית.** XLK ב"מובילים" שבועות רבים ברצף. המשטר של 2017–2021,
נשבר ב-2022, ושוחזר חלקית ב-2023–2024 (גל ה-AI).
"""
)

st.divider()

# ============================================================
# SECTION 6 - RRG VS CYCLE
# ============================================================
st.markdown("## 6. RRG מול סיווג המחזור (מודול 4)")
st.markdown(
    """
- מסווג המחזור ממודול 4 = **פונדמנטלי** (קלטי מאקרו: עקום תשואות, אבטלה,
  אינפלציה, ייצור).
- ה-RRG = **טכני** (מחירים, מה שהשוק חושב).

**ההמלצה:** *שני המקורות צריכים להסכים.*

| המאקרו אומר | ה-RRG מראה | פעולה |
|---|---|---|
| Late Cycle, OW XLE | XLE עמוק ב"מובילים" | ✅ אישור. ביטחון גבוה |
| Recession, OW XLP/XLU | עוברים ל"מובילים" | ✅ אישור. גודל רגיל |
| Recovery, OW XLY/XLK | עדיין ב"פיגרים" | ⚠️ מקדים או טועים. גודל קטן |
| Mid Cycle, ניטרלי | מגזר אחד בולט ב"מובילים" | ↗️ הטיה טקטית קלה |
"""
)

st.divider()

# ============================================================
# SECTION 7 - LIMITATIONS
# ============================================================
st.markdown("## 7. מגבלות שחשוב להכיר")
st.markdown(
    """
- **החלקה כבדה → עיכוב.** ה-RRG ממרק חזק. תפניות מפוספסות בזמן אמת, השיהוי
  הטיפוסי 4–8 שבועות. אל תצפה לזהות את שפל המגזר ביום שהוא קרה.
- **דרושה נזילות.** עובד מצוין על ETFs סקטוריאליים גדולים. אל תפעיל על
  מיקרו-קאפ או מניות בודדות פחות נזילות – הרעש יהרוס את האות.
- **בחירת ה-lookback קריטית.** ברירת המחדל של דה-קמפנר ל-ETFs סקטוריאליים היא
  **10–14 שבועות** על נתונים שבועיים – זה גם מה שאנחנו משתמשים בו
  (lookback=14, smoothing=10).
- **סבלנות.** מגזר יכול לשבת ברובע אחד **חודשים**. RRG אינו כלי תוך-שבועי –
  הוא כלי טקטי לטווח של שבועות עד רבעונים.
"""
)

st.divider()

# ============================================================
# QUIZ
# ============================================================
QUIZ_QUESTIONS = [
    {
        "q": "זנב של מגזר שעובר מ'משתפרים' (שמאל-עליון) ל'מובילים' (ימין-עליון) – מה זה אומר?",
        "options": [
            "האטה של הכוח היחסי, סימן דובי",
            "האצה של הכוח היחסי, סימן שורי",
            "המגזר נע יחד עם SPY",
            "אין משמעות, זה רעש",
        ],
        "answer": 1,
        "explain": (
            "מעבר מ-Improving ל-Leading משמעו שגם ה-RS-Ratio עלה מעל 100 וגם "
            "ה-Momentum נשאר מעל 100 – האצה שורית קלאסית."
        ),
    },
    {
        "q": "מגזר בנקודה (RS-Ratio=95, RS-Momentum=105) באיזה רובע?",
        "options": [
            "🟢 מובילים",
            "🔵 משתפרים",
            "🟡 נחלשים",
            "🔴 פיגרים",
        ],
        "answer": 1,
        "explain": (
            "RS-Ratio<100 (חלש יחסית) + Momentum>100 (משתפר) = רובע 'משתפרים' "
            "(שמאל-עליון). מועמד פוטנציאלי לקנייה."
        ),
    },
    {
        "q": "מה ההבדל בין JdK RS-Ratio לבין JdK RS-Momentum?",
        "options": [
            "אין הבדל, זה אותו מספר",
            "RS-Ratio = רמת הכוח היחסי. RS-Momentum = קצב השינוי שלו",
            "RS-Ratio למניות, RS-Momentum למדדים",
            "RS-Momentum מתעלם מהמדד הבנצ'מרק",
        ],
        "answer": 1,
        "explain": (
            "RS-Ratio מתאר *איפה* הכוח היחסי נמצא עכשיו (מעל/מתחת 100). "
            "RS-Momentum הוא הנגזרת – *כמה מהר* הכוח היחסי משתנה."
        ),
    },
    {
        "q": "ה-RRG וסיווג המחזור ממודול 4 *סותרים* זה את זה. מה הצעד הזהיר?",
        "options": [
            "לסחור בגודל גדול בכיוון של המאקרו",
            "להתעלם מהמאקרו ולסמוך רק על RRG",
            "להמתין או לסחור בגודל קטן עד שיש הסכמה",
            "להפוך את הפוזיציה לכיוון ההפוך מהשניים",
        ],
        "answer": 2,
        "explain": (
            "כשהמקור הפונדמנטלי והמקור הטכני לא מסכימים – או שאתה מקדים, או "
            "שאחד מהם טועה. גודל קטן או המתנה הם הצעד הזהיר."
        ),
    },
    {
        "q": "מהו סדר הסיבוב הטיפוסי על ה-RRG?",
        "options": [
            "מובילים → משתפרים → פיגרים → נחלשים",
            "משתפרים → מובילים → נחלשים → פיגרים → משתפרים",
            "פיגרים → נחלשים → מובילים → משתפרים",
            "אין סדר – הסיבוב אקראי",
        ],
        "answer": 1,
        "explain": (
            "הסיבוב הקלאסי הוא נגד כיוון השעון: מ-Improving אל Leading אל "
            "Weakening אל Lagging וחזרה אל Improving."
        ),
    },
]

render_quiz("module5", QUIZ_QUESTIONS)

st.divider()
st.caption(
    "מודול 5 הסתיים. במודול הבא נשלב את שלב המחזור (מודול 4) עם המיקום ב-RRG "
    "כדי לבנות 'תיק טקטי' שמתואם גם פונדמנטלית וגם טכנית."
)
