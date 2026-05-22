"""Module 3 - The Classical Sector Rotation Model (Sam Stovall).

Bridges Module 1 (business cycle phases) and Module 2 (sector ETFs) into
the canonical "if phase X, overweight Y" framework that Module 4 then
operationalizes with live FRED data.
"""
from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from utils.page import bootstrap
from utils.style import page_header
from utils.quiz import render_quiz
from utils.cycle import phase_to_sectors, PHASE_LABELS_HE
from utils.market import SECTORS


bootstrap("מודול 3 – הסיבוב הקלאסי")
page_header(
    "🔄 מודול 3 – מודל הסיבוב הסקטוריאלי הקלאסי",
    "איך המחזור (מודול 1) פוגש את הסקטורים (מודול 2) – המסגרת של Sam Stovall",
)


# ----- פתיחה -----

st.markdown(
    """
כאן המחזור הכלכלי (**מודול 1**) פוגש את הסקטורים (**מודול 2**).
מודל הסיבוב הסקטוריאלי הקלאסי טוען טענה פשוטה: **בשלבים שונים של המחזור,
סקטורים שונים מובילים.** Sam Stovall קודד את המסגרת הזו בספרו
*Standard & Poor's Guide to Sector Investing* (1996), והיא החזיקה מעמד
טוב להפליא – אם כי עם הסתייגויות חשובות שנכסה.

בסוף המודול תהיה לך אינטואיציה ברורה של "אם אנחנו בשלב X, עודף משקל ב-Y"
– האינטואיציה הזו תקבל מימוש אוטומטי במודול 4 עם נתוני FRED חיים.
"""
)


# ----- הגלגל של Stovall -----

st.divider()
st.markdown("## 🎡 הגלגל של Stovall")
st.markdown(
    "הגלגל מתחיל ב-12 בשעון (תחתית מחזור / התאוששות מוקדמת) ומסתובב **עם "
    "כיוון השעון** דרך מחזור עסקים שלם:"
)

# Wheel data: (ticker, angle_deg_clockwise_from_12, phase_label_he)
WHEEL: list[tuple[str, float, str]] = [
    ("XLF", 0, "התאוששות מוקדמת"),
    ("XLY", 30, "התאוששות מוקדמת"),
    ("XLI", 75, "אמצע מחזור"),
    ("XLC", 90, "אמצע מחזור"),
    ("XLK", 110, "אמצע מחזור"),
    ("XLB", 150, "סוף מחזור"),
    ("XLE", 180, "סוף מחזור"),
    ("XLP", 215, "שיא שוק"),
    ("XLV", 240, "שיא שוק"),
    ("XLU", 290, "תחילת דובי"),
    ("XLRE", 330, "תחתית / חזרה ל-XLF"),
]

# Convert clockwise-from-12 to standard polar (counter-clockwise from 3 o'clock)
def _polar_angle(clockwise_deg_from_12: float) -> float:
    return (90 - clockwise_deg_from_12) % 360


fig_wheel = go.Figure()

# Background ring with phase arcs (visual context)
PHASE_ARCS = [
    (345, 75, "rgba(46,204,113,0.18)"),
    (75, 150, "rgba(52,152,219,0.18)"),
    (150, 225, "rgba(243,156,18,0.18)"),
    (225, 345, "rgba(231,76,60,0.18)"),
]
for start, end, color in PHASE_ARCS:
    thetas = (list(range(start, 360)) + list(range(0, end + 1))
              if end < start else list(range(start, end + 1)))
    fig_wheel.add_trace(go.Scatterpolar(
        r=[1.0] * len(thetas), theta=[_polar_angle(t) for t in thetas],
        mode="lines", line=dict(color=color, width=42),
        hoverinfo="skip", showlegend=False,
    ))

# Sector markers
r_marker = 1.0
m_thetas = [_polar_angle(a) for _, a, _ in WHEEL]
m_text = [f"{SECTORS[t]['emoji']} {t}" for t, _, _ in WHEEL]
m_hover = [
    f"{SECTORS[t]['emoji']} <b>{t}</b><br>{SECTORS[t]['name_he']}<br><i>{ph}</i>"
    for t, _, ph in WHEEL
]

fig_wheel.add_trace(
    go.Scatterpolar(
        r=[r_marker] * len(WHEEL),
        theta=m_thetas,
        mode="markers+text",
        text=m_text,
        textposition="middle center",
        textfont=dict(size=13, color="#ffffff"),
        marker=dict(
            size=46,
            color=["#2ecc71", "#2ecc71", "#3498db", "#3498db", "#3498db",
                   "#f39c12", "#f39c12", "#9b59b6", "#9b59b6", "#e74c3c", "#1abc9c"],
            line=dict(color="#0e1117", width=2),
        ),
        hovertext=m_hover,
        hoverinfo="text",
        showlegend=False,
    )
)

# Phase quadrant labels (outer ring)
PHASE_LABEL_POS = [
    (30, "🌱 התאוששות"),
    (115, "🚀 אמצע"),
    (190, "🔥 סוף מחזור"),
    (290, "🧊 דובי / מיתון"),
]
fig_wheel.add_trace(
    go.Scatterpolar(
        r=[1.55] * len(PHASE_LABEL_POS),
        theta=[_polar_angle(a) for a, _ in PHASE_LABEL_POS],
        mode="text",
        text=[lbl for _, lbl in PHASE_LABEL_POS],
        textfont=dict(size=14, color="#cfd2d6"),
        hoverinfo="skip",
        showlegend=False,
    )
)

fig_wheel.update_layout(
    height=520,
    margin=dict(l=10, r=10, t=20, b=10),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    polar=dict(
        bgcolor="rgba(0,0,0,0)",
        radialaxis=dict(visible=False, range=[0, 1.8]),
        angularaxis=dict(
            direction="counterclockwise",
            tickmode="array",
            tickvals=[0, 90, 180, 270],
            ticktext=["", "", "", ""],
            showgrid=False,
            showline=False,
        ),
    ),
    showlegend=False,
)

st.plotly_chart(fig_wheel, use_container_width=True, config={"displayModeBar": False})

st.caption(
    "סדר הגלגל (עם כיוון השעון מ-12): XLF → XLY → XLI → XLC → XLK → XLB → XLE → "
    "XLP → XLV → XLU → XLRE → ובחזרה ל-XLF. ריחוף על נקודה חושף שם סקטור והשלב."
)


# ----- מטריצת שלב ↔ סקטור (משתמש ב-phase_to_sectors) -----

st.divider()
st.markdown("## 📋 מטריצת שלב ↔ סקטור")
st.markdown(
    "הטבלה למטה נשלפת **דינמית** מהפונקציה `phase_to_sectors()` – אותה פונקציה "
    "שמודול 4 ישתמש בה. כך הקורס נשאר עקבי לאורך כל המודולים."
)


def _tickers_to_he(tickers: list[str]) -> str:
    if not tickers:
        return "—"
    parts = [
        f"{SECTORS[t]['emoji']} {t} ({SECTORS[t]['name_he']})"
        for t in tickers if t in SECTORS
    ]
    return " · ".join(parts) if parts else "—"


PHASE_RATIONALE_HE: dict[str, str] = {
    "early": "ריבית נמוכה, עקום תלול, אופטימיות חוזרת, ביקושים מתעוררים",
    "mid": "צמיחה יציבה, אינפלציה מתונה, capex עולה, מרווחי אשראי הדוקים",
    "late": "אינפלציה גבוהה, הפד מהדק, capex מתעייף, ריצה אחרונה של סחורות",
    "recession": "בריחה לאיכות, רווחים קורסים, ביקושים לא-גמישים שורדים",
}

PHASE_ORDER = ["early", "mid", "late", "recession"]

for phase in PHASE_ORDER:
    tilts = phase_to_sectors(phase)
    ow = _tickers_to_he(tilts["overweight"])
    uw = _tickers_to_he(tilts["underweight"])
    label = PHASE_LABELS_HE[phase]
    reason = PHASE_RATIONALE_HE[phase]
    with st.container(border=True):
        st.markdown(f"### {label}")
        st.markdown(f"**🟢 Overweight:** {ow}")
        st.markdown(f"**🔴 Underweight:** {uw}")
        st.caption(f"למה: {reason}")


# ----- Deep dives -----

st.divider()
st.markdown("## 🔬 למה דווקא הסקטורים האלה בכל שלב")

with st.expander("🌱 התאוששות מוקדמת – הרכישות הראשונות", expanded=False):
    st.markdown(
        """
- **הרקע המאקרו:** עקום תשואות תלול, הפד סיים להוריד ריבית או עדיין מוריד.
- **XLY (Discretionary):** הצרכן חוזר לבזבז – אמזון, טסלה, Home Depot נהנים מההתאוששות.
- **XLF (Financials):** עקום תלול = בנקים מרוויחים על מרווח הריבית (NIM גבוה).
- **XLI (Industrials):** הפעילות התעשייתית מתחילה מחדש, הזמנות נכנסות.
- **XLB (Materials):** ביקוש לבנייה ולנחושת חוזר.
- **XLRE (Real Estate):** ריבית נמוכה = משכנתאות נגישות = נדל\"ן בורח קדימה.
- **להימנע:** מסקטורים הגנתיים שפיגרו בזינוק. **XLU** סובלת מתחרות עם איגרות חוב
  שעדיין מציעות תשואה סבירה ביחס לסיכון.
"""
    )

with st.expander("🚀 אמצע מחזור – הצמיחה הבריאה", expanded=False):
    st.markdown(
        """
- **הרקע המאקרו:** צמיחה יציבה, capex עולה, אינפלציה במטרה, רווחיות חברות שיא.
- **XLK (Technology):** סיפור הפרודוקטיביות זורח – הוצאות הון על תוכנה, ענן ושבבים.
- **XLC (Communication):** מונופולי mega-cap (Meta, Google) מנצלים תקציבי פרסום שמנים.
- **XLI (Industrials):** עוד חזק, חברות הון מוציאות על מכונות ותשתית.
- **להימנע:** הגנתיים נשחקים – **XLU** ו-**XLP** מפגרים כשהצמיחה חזקה,
  כי המשקיעים רוצים סיכון, לא יציבות.
"""
    )

with st.expander("🔥 סוף מחזור – הריצה האחרונה", expanded=False):
    st.markdown(
        """
- **הרקע המאקרו:** אינפלציה עולה, הפד נצי, capex מתעייף, שוק העבודה הדוק.
- **XLE (Energy):** סחורות בדרך כלל **רצות אחרונות** לפני מיתון – ביקוש שיא + מחיר נפט שולי.
- **XLB (Materials):** המשך לוגיקת הסחורות + העברת אינפלציה למחירים.
- **XLV (Healthcare):** הגנתי קלאסי **עם** יכולת להעביר אינפלציה (תרופות, ביטוחים).
- **XLP (Staples):** הגנה חלקית – יכול להעביר חלק מהאינפלציה אבל לא הכל;
  ביצועים תלויים כמה כוח תמחור יש לכל חברה.
- **להימנע:** **XLY** – הצרכן נשחק מאינפלציה; **XLRE** – ריבית גבוהה משחיתה הערכות נדל\"ן.
"""
    )

with st.expander("🧊 מיתון – הישרדות מעל הכל", expanded=False):
    st.markdown(
        """
- **הרקע המאקרו:** רווחים קורסים, אבטלה עולה, מרווחי אשראי מתרחבים, סנטימנט שלילי.
- **XLP (Staples):** אנשים ממשיכים לקנות משחת שיניים, חלב, סבון. ביקוש לא-גמיש.
- **XLV (Healthcare):** ביקוש לבריאות לא משתנה במיתון – חולים נשארים חולים.
- **XLU (Utilities):** תשואות מפוקחות-רגולציה, הכנסות יציבות.
- **להימנע:** **XLF** – הפסדי אשראי וצמצום NIM; **XLY** – צרכן מצמצם ראשון;
  **XLI** – capex קופא; **XLE** – ביקוש לנפט קורס עם הפעילות.
"""
    )


# ----- עדויות אמפיריות -----

st.divider()
st.markdown("## 📚 עדויות אמפיריות – האם זה באמת עובד?")
st.markdown(
    """
- **Stovall (1996):** העבודה המקורית הראתה תשואה עודפת ממוצעת של כ-**3% בשנה**
  על-פני קנה-והחזק של S&P 500 – **אם** הסיבוב מתוזמן נכון. הקץ' המפורסם:
  "מתוזמן נכון". רוב המשקיעים הפרטיים מאחרים את כל המהלכים.

- **מחקר אקדמי תומך:**
  - *Jagannathan & Korajczyk* – הראו שביצועים סקטוריאליים אינם אקראיים בין-מחזורית.
  - *Andrade et al.* – תיעדו דפוסי החזר חוצי-סקטור הקשורים לשלב המחזור.
  - *Ahmerkamp & Grant (2013)* – אישרו אפקטי מומנטום קרוס-סקטוריאליים.
  - *Asness, Moskowitz & Pedersen (2013) – "Value and Momentum Everywhere":*
    מומנטום עובד גם ברמת סקטור, לא רק מניות בודדות.

- **המקרה הנגדי – שינויי משטר:**
  - **2010–2021:** ריבית 0% שברה את הגלגל. XLK שלט בכל שלב, "אמצע מחזור" החזיק 11 שנה.
  - **2022:** ניסוב מהיר ל"סוף מחזור" – ו-**Value/Energy** היכו את כולם, בניגוד לאינטואיציה
    שמיתון מגיע "בקרוב".
  - השוק תמיד נע מהר מהמודל. הסיבוב הקלאסי הוא **מסגרת חשיבה**, לא דטרמיניזם.
"""
)


# ----- הסתייגויות פרקטיות -----

st.divider()
st.markdown("## ⚠️ הסתייגויות פרקטיות חשובות")

st.markdown(
    """
1. **שלבי המחזור מזוהים רטרואקטיבית.** NBER מכריזה על מיתון **חודשים אחרי**
   שהוא התחיל. עד שאתה "יודע" שאתה ב"סוף מחזור" – הסיבוב כבר חצי-בוצע.

2. **תשואות סקטוריאליות רועשות בטווח קצר.** הסיבוב עובד הכי טוב באופקים של
   **3–6 חודשים**, לא שבועי. רעש שבועי יבלע את הסיגנל.

3. **הימנע מביטחון יתר.** המודל הספרי **הפסיד ל-QQQ** בין 2010 ל-2021.
   הוא עובד **בממוצע, על פני מחזורים**, לא בכל חלון.

4. **עלויות עסקה.** ריבלאנס תכוף שורף 1–3% בשנה בעמלות, מסים ו-slippage.
   אם אתה מסובב פעם בחודש, ייתכן שאיבדת את כל היתרון.

5. **המודל הוריסטי, לא צופה.** הוא ממפה מצב נוכחי לסקטורים, לא חוזה את המצב הבא.
"""
)


# ----- גשר למודול 4 -----

st.divider()
st.markdown("## ➡️ איך מודול 4 הופך את זה לפעולה")
st.markdown(
    """
**מודול 4 (Macro Dashboard):**
- שולף בזמן אמת ~8 אינדיקטורים מ-FRED (T10Y2Y, UNRATE, CPI, INDPRO, HY OAS, …).
- מסווג אוטומטית את שלב המחזור הנוכחי.
- מציג את ה-OW/UW המתאים – באמצעות **אותה** `phase_to_sectors()` שראית כאן.

**מודול 5 (RRG – Relative Rotation Graphs):**
- בודק האם **מחירי השוק עצמם** מסכימים עם הקריאה המאקרו-כלכלית.
- אם המאקרו אומר "סוף מחזור" אבל XLK עולה ב-RRG → התנהגות מסקרנת שדורשת הסבר.

**מודול 6 (יישום):** איך מתרגמים הטיות OW/UW ל-positions אמיתיים בתיק.

הסיבוב הקלאסי הוא **שלד**. הסטודיו מודולים 4–5 שמים עליו בשר חי מהשוק.
"""
)


# ----- Quiz -----

st.divider()
render_quiz(
    "module_3_classical",
    [
        {
            "q": "מה מנבא הגלגל של Stovall עבור סוף מחזור (Late cycle)?",
            "options": [
                "טכנולוגיה ושירותי תקשורת מובילים",
                "אנרגיה, חומרי גלם ובריאות מובילים",
                "פיננסים וצריכה לא-הכרחית מובילים",
                "מוצרי צריכה בסיסיים ושירותים ציבוריים מובילים",
            ],
            "answer": 1,
            "explain": "סוף מחזור: XLE + XLB (ריצה אחרונה של סחורות עם האינפלציה) + XLV (הגנתי עם כוח תמחור).",
        },
        {
            "q": "מדוע XLF (פיננסים) מוביל בהתאוששות מוקדמת?",
            "options": [
                "כי הבנקים מקבלים סבסוד ממשלתי",
                "כי עקום התשואות תלול – בנקים מרוויחים על מרווח הריבית (NIM)",
                "כי הבנקים פטורים ממסים בהתאוששות",
                "כי FED קונה מניות בנקים ישירות",
            ],
            "answer": 1,
            "explain": "עקום תלול = הבנקים לווים זול בקצר ומלווים יקר בארוך → מרווח הריבית (NIM) רחב → רווחיות גבוהה.",
        },
        {
            "q": "מה הסיבה הנפוצה ביותר לכך שהסיבוב הקלאסי **נכשל** בפרקטיקה?",
            "options": [
                "המודל מתמטית שגוי",
                "שלבי המחזור מזוהים רטרואקטיבית – עד שיודעים, הסיבוב כבר בוצע",
                "סקטורי SPDR לא מייצגים את הכלכלה",
                "FRED לא אמין",
            ],
            "answer": 1,
            "explain": "תיזמון. NBER מכריזה רטרואקטיבית, נתוני מאקרו מתפרסמים באיחור ועוברים תיקונים. עד שמזהים שלב – חלק גדול מהמהלך כבר התרחש.",
        },
        {
            "q": "מתי NBER מכריזה רשמית על תאריך תחילת מיתון?",
            "options": [
                "באותו רבעון שהוא התחיל",
                "שבוע אחרי שני רבעוני צמיחה שלילית",
                "חודשים עד שנה+ אחרי תחילת המיתון, בדיעבד",
                "מראש, על בסיס מודלים חיזויים",
            ],
            "answer": 2,
            "explain": "NBER היא ועדה אקדמית שמכריזה רטרואקטיבית. מיתון 2008 הוכרז 12/2008 (התחיל 12/2007). מיתון 2020 הוכרז 6/2020 (התחיל 2/2020).",
        },
        {
            "q": "איזה סקטור פחות **רגיש** לשינויי ריבית (ולכן פחות מושפע מהפד)?",
            "options": [
                "XLRE – נדל\"ן",
                "XLU – שירותים ציבוריים",
                "XLF – פיננסים",
                "XLE – אנרגיה",
            ],
            "answer": 3,
            "explain": "XLE נע בעיקר עם מחיר הנפט והביקוש הגלובלי. XLRE/XLU מתמחרים ישירות מול אג\"ח, XLF חי על עקום התשואות. אנרגיה הכי פחות מתואמת לריבית.",
        },
    ],
)
