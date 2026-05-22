"""Module 8 - Integrating Sector Rotation into a Real Portfolio.

Closing module of the Sector Rotation course. Teaches portfolio-level sizing
of the rotation sleeve, the core-satellite framework, rebalancing rules,
behavioral pitfalls, and when *not* to use rotation. Includes an interactive
portfolio builder.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.market import BENCHMARK, SECTOR_TICKERS, SECTORS
from utils.page import bootstrap
from utils.quiz import render_quiz
from utils.style import page_header


bootstrap("מודול 8 – שילוב בתיק")
page_header(
    "🧩 מודול 8 – שילוב Sector Rotation בתיק אמיתי",
    "אסטרטגיה טובה בלי סייזינג נכון = הימור. במודול הזה לומדים כמה מהתיק צריך להיות רוטציה.",
)

# ---------------------------- OPENING ----------------------------

st.markdown(
    """
רוב המשקיעים הפרטיים שלומדים אסטרטגיה אקטיבית עושים את אותה הטעות: **הם נכנסים All-In**.
הדאטה ברור – ככה מתפוצצים. המודול הזה לא עוסק עוד באסטרטגיה עצמה. הוא עוסק ב**סייזינג** –
כמה גדול צריך להיות ה"שרוול" (sleeve) של Sector Rotation בתוך התיק האמיתי שלך, ואיך הוא
משתלב עם ליבת אינדקס פסיבית, אג"ח, מזומן ולוויינים אחרים.

עברנו דרך ארוכה:
- **מודולים 1-3** – התיאוריה: מחזור עסקים, שלביו, ואיזה סקטור מוביל בכל שלב.
- **מודול 4** – לוח מחוונים מאקרו חי שמסווג את השלב הנוכחי.
- **מודול 5** – RRG וניתוח מחיר יחסי לזיהוי מנהיגות סקטוריאלית.
- **מודול 6** – סגנונות יישום (Top-Down, Momentum, Hybrid).
- **מודול 7** – בדיקת ביצועים (backtest) של אסטרטגיית מומנטום קלאסית.

עכשיו השאלה הסופית: **איפה זה יושב בתיק שלך?**
"""
)

st.divider()

# ---------------------------- CORE-SATELLITE ----------------------------

st.markdown("## 🏛️ Section 1 – מסגרת Core-Satellite")

st.markdown(
    """
המבנה שעובד למשקיעים פרטיים מתוחכמים נקרא **Core-Satellite**. מפרידים את התיק
לשלושה דליים נפרדים, כל אחד עם תפקיד מוגדר:

- **ליבה פסיבית (Core) – 60%-90% מהתיק.** ETF פסיבי של מדד רחב (VOO / SPY / VTI / VT).
  התפקיד: חשיפה ארוכת טווח לאקוויטי, ביטא שוק, עמלות נמוכות, תחלופה נמוכה, מסים נמוכים.
  **זה הדלי שאסור לגעת בו** מסיבות של "אני חושב שטכנולוגיה תעלה".
- **לוויינים אקטיביים (Satellite) – 10%-40%.** כאן יושב Sector Rotation, יחד עם
  הטיות פקטוריאליות (Value/Quality/Momentum) או בחירת מניות בודדות. התפקיד: אלפא
  אינקרמנטלית אם יש לך יכולת, או רכב לימוד אם עדיין לא.
- **אג"ח / מזומן – דלי נפרד** לפי פרופיל סיכון אישי וגיל. **לא משתנה** מ-Sector
  Rotation. אם החלטת על 20% אג"ח, זה נשאר 20% גם כשהשרוול האקטיבי מסתובב.

הרעיון הגדול: **חומת אש (firewall) בין הליבה ללוויינים**. הליבה לא יודעת ולא צריכה
לדעת על הרוטציה. השרוול לא נוגע בליבה.
"""
)


def _core_satellite_donut() -> go.Figure:
    allocations = [
        {"name": "שמרני (80/15/5)", "values": [80, 15, 5]},
        {"name": "מאוזן (65/25/10)", "values": [65, 25, 10]},
        {"name": "אגרסיבי (50/30/20)", "values": [50, 30, 20]},
    ]
    labels = ["ליבה פסיבית", 'אג"ח / מזומן', "רוטציית סקטורים"]
    colors = ["#2ca02c", "#1f77b4", "#ff7f0e"]
    fig = go.Figure()
    n = len(allocations)
    for i, alloc in enumerate(allocations):
        fig.add_trace(
            go.Pie(
                labels=labels,
                values=alloc["values"],
                name=alloc["name"],
                title=dict(text=alloc["name"], font=dict(size=13)),
                hole=0.55,
                domain=dict(x=[i / n + 0.01, (i + 1) / n - 0.01], y=[0, 1]),
                marker=dict(colors=colors, line=dict(color="#0e1117", width=2)),
                textinfo="percent",
                textfont=dict(size=12),
                sort=False,
            )
        )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=380,
        margin=dict(l=10, r=10, t=40, b=40),
        title="שלוש דוגמאות לחלוקה Core-Satellite",
        legend=dict(orientation="h", y=-0.05),
        dragmode="pan",
    )
    return fig


st.plotly_chart(
    _core_satellite_donut(),
    use_container_width=True,
    config={"displayModeBar": False},
)

st.caption(
    "מימין לשמאל: גישה שמרנית (שרוול קטן, מתאים למתחילים), מאוזנת (משקיע עם ניסיון), ואגרסיבית (לא מומלץ ללא רקורד מוכח של שנים)."
)

st.divider()

# ---------------------------- SLEEVE SIZE ----------------------------

st.markdown("## 📏 Section 2 – כמה גדול שרוול הרוטציה צריך להיות?")

st.markdown(
    """
ההחלטה הזו תלויה ב**רמת הניסיון והמשמעת שלך**, לא ברמת הביטחון שלך באסטרטגיה.
הנה עץ החלטה פרקטי:

#### 🌱 שלב "לומד" – 0%-5% מהתיק
אם זה עתה סיימת את הקורס הזה, אתה כאן. תתייחס לרוטציה כ-**Paper Trading + פוזיציות
אמת קטנות**. המטרה: לראות אם אתה באמת מצליח לעקוב אחרי כללים גם כשכואב, לא להרוויח
כסף. 5% מתיק של $20K זה $1,000 – מספיק כדי שיהיה אכפת לך, מעט מספיק כדי שטעות לא
תהרוס את החיים.

#### 🚀 שלב "מבצע" – 5%-15%
אחרי **שנה+ של ביצוע ממושמע** – הלכת אחרי הכללים, לא נטשת בדרו-דאון, ראית סייקל
אחד שלם. עכשיו אפשר להגדיל בזהירות.

#### 🏆 שלב "Edge מוכח" – 15%-30%
דורש **3+ שנים של מסחר חי** + Sharpe מעל 0.5 אחרי עלויות + Hit Rate מעל 55%.
זה לא משהו שאתה מצהיר עליו – זה משהו שהדאטה אומרת.

#### ⚠️ מעל 30% – אזור סכנה
אתה מהמר את עתידך הפיננסי על אסטרטגיה אחת. גם מנהלי קרנות מקצועיים לא עושים זאת
בלי גידור. אם אתה שם, יש סיכוי גבוה שאתה נופל לאחת מהטעויות שנדבר עליהן ב-Section 5.
"""
)

st.info(
    "💡 כלל הזהב: **התחל קטן יותר ממה שאתה חושב שאתה צריך**. אפשר תמיד להגדיל אחרי "
    "שיש דאטה. אי אפשר להחזיר כסף שאיבדת בגלל סייזינג מופרז בתחילת הדרך."
)

st.divider()

# ---------------------------- INTERACTIVE BUILDER ----------------------------

st.markdown("## 🧮 Section 3 – בונה תיק אינטראקטיבי")

st.markdown(
    "הזז את הסליידרים ובדוק איך נראית חלוקת התיק שלך. כל המספרים מתעדכנים בזמן אמת."
)

nlv = st.number_input(
    "שווי נטו כולל (USD)", min_value=100, value=10000, step=100
)

core_pct = st.slider("ליבה פסיבית (%)", 40, 95, 70)
bonds_pct = st.slider("אג\"ח / מזומן (%)", 0, 40, 15)
rotation_pct = st.slider("רוטציית סקטורים (%)", 0, 30, 10)
other_pct = 100 - core_pct - bonds_pct - rotation_pct

# Validation
col_a, col_b = st.columns(2)
with col_a:
    st.metric("שאר (מזומן חופשי / מניות בודדות)", f"{other_pct}%")
with col_b:
    total_used = core_pct + bonds_pct + rotation_pct
    st.metric("סך כל הקצאה ידנית", f"{total_used}%")

if other_pct < 0:
    st.error(
        f"❌ סך הקצאה {total_used}% חורג מ-100%. הקטן אחד מהסליידרים ב-{-other_pct}%."
    )
elif other_pct > 30:
    st.warning(
        f"⚠️ נשאר {other_pct}% לא מוקצה – זה הרבה מזומן 'אבוד'. שקול להגדיל ליבה או אג\"ח."
    )
else:
    st.success("✅ הקצאה תקינה.")

# Dollar amounts
core_usd = nlv * core_pct / 100
bonds_usd = nlv * bonds_pct / 100
rotation_usd = nlv * rotation_pct / 100
other_usd = nlv * max(other_pct, 0) / 100

st.markdown("### 💵 ההקצאה בדולרים")
df_alloc = pd.DataFrame(
    {
        "דלי": ["ליבה פסיבית (VOO/VTI)", 'אג"ח / מזומן', "רוטציית סקטורים", "שאר"],
        "%": [core_pct, bonds_pct, rotation_pct, max(other_pct, 0)],
        "USD": [
            f"${core_usd:,.0f}",
            f"${bonds_usd:,.0f}",
            f"${rotation_usd:,.0f}",
            f"${other_usd:,.0f}",
        ],
    }
)
st.dataframe(df_alloc, use_container_width=True, hide_index=True)

# Sample rotation sleeve breakdown
if rotation_pct > 0 and other_pct >= 0:
    st.markdown("### 🎯 פירוט שרוול הרוטציה (דוגמה: 3 סקטורים שווה-משקל)")
    sample_tickers = ["XLK", "XLI", "XLV"]
    per_ticker = rotation_usd / len(sample_tickers)
    rotation_rows = []
    for tkr in sample_tickers:
        meta = SECTORS.get(tkr, {})
        name_he = meta.get("name_he", tkr)
        emoji = meta.get("emoji", "")
        rotation_rows.append(
            {
                "טיקר": tkr,
                "סקטור": f"{emoji} {name_he}",
                "USD": f"${per_ticker:,.0f}",
                "% מהתיק": f"{rotation_pct / len(sample_tickers):.1f}%",
            }
        )
    st.dataframe(pd.DataFrame(rotation_rows), use_container_width=True, hide_index=True)
    st.caption(
        "טיקרים לדוגמה בלבד – הסקטורים בפועל ייקבעו לפי האות מ-Module 4 (מקרו) או Module 5 (RRG/Momentum)."
    )

# Pie chart of allocation
st.markdown("### 🥧 חלוקת התיק (תרשים)")


def _portfolio_pie() -> go.Figure:
    labels = ["ליבה פסיבית", 'אג"ח / מזומן', "רוטציית סקטורים", "שאר"]
    values = [core_pct, bonds_pct, rotation_pct, max(other_pct, 0)]
    colors = ["#2ca02c", "#1f77b4", "#ff7f0e", "#7f7f7f"]
    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.5,
                marker=dict(colors=colors, line=dict(color="#0e1117", width=2)),
                textinfo="label+percent",
                textfont=dict(size=13),
                sort=False,
            )
        ]
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=380,
        margin=dict(l=10, r=10, t=20, b=20),
        showlegend=True,
        legend=dict(orientation="h", y=-0.05),
        dragmode="pan",
    )
    return fig


st.plotly_chart(
    _portfolio_pie(),
    use_container_width=True,
    config={"displayModeBar": False, "displaylogo": False},
)

# Mini dashboard – portfolio vol and beta (rough)
st.markdown("### 📊 Mini Dashboard – הערכת סיכון (משוערת)")

SPY_VOL = 16.0  # annualized %, long-term
ROT_VOL = 22.0  # rotation sleeve, slightly higher due to concentration
BOND_VOL = 5.0
OTHER_VOL = 18.0

# Simple weighted vol (NOT covariance-aware, just for intuition)
weights = [core_pct, bonds_pct, rotation_pct, max(other_pct, 0)]
vols = [SPY_VOL, BOND_VOL, ROT_VOL, OTHER_VOL]
betas = [1.0, 0.0, 1.1, 0.9]

if sum(weights) > 0:
    norm_w = [w / sum(weights) for w in weights]
    port_vol = sum(w * v for w, v in zip(norm_w, vols))
    port_beta = sum(w * b for w, b in zip(norm_w, betas))
else:
    port_vol = 0.0
    port_beta = 0.0

mcol1, mcol2, mcol3 = st.columns(3)
mcol1.metric("תנודתיות שנתית משוערת", f"{port_vol:.1f}%")
mcol2.metric("ביטא לשוק (לעומת SPY)", f"{port_beta:.2f}")
mcol3.metric("חשיפה אקטיבית", f"{rotation_pct}%")

st.caption(
    f"הערכות גסות בלבד מבוססות ספרות: SPY ביטא 1.0, שרוול רוטציה ביטא ~1.1 "
    f"(בנצ'מרק {BENCHMARK}), אג\"ח ביטא 0. תנודתיות מחושבת כממוצע משוקלל ולא "
    "מתחשבת בקורלציות בין הדליים – המספר האמיתי בדרך כלל נמוך יותר."
)

st.divider()

# ---------------------------- REBALANCING ----------------------------

st.markdown("## 🔁 Section 4 – כללי איזון מחדש (Rebalancing)")

st.markdown(
    """
התיק נוטה לסטות מהיעד לאורך זמן – לוויינים מנצחים גדלים, מפסידים מצטמקים. אם לא
מאזנים, התיק "נהיה אגרסיבי יותר אחרי שווקים שעלו" וההפך – בדיוק הפוך ממה שאתה רוצה.

#### 📅 Calendar Rebalance (איזון לפי לוח שנה)
חודשי או רבעוני. **התאם את התדירות לתדירות אסטרטגיית הרוטציה** – אם הרוטציה מתחלפת
חודשית (Top-3 momentum), איזון חודשי. אם רבעונית, איזון רבעוני. **מינוס:** מייצר
תחלופה (turnover) גם כשהסטיות קטנות.

#### 📏 Threshold Rebalance (איזון לפי סף)
אזן רק כשדלי כלשהו סטה ביותר מ-X% מהיעד (טיפוסי: 5%). **פחות מסחר, יותר יעיל מס**.
זה הכלל המועדף בחשבונות חייבי-מס. מינוס: סטיות יכולות להצטבר אם השוק רגוע.

#### ⚖️ Hybrid (המומלץ לרובכם)
איזן רבעונית, **או** אם דלי סטה מעל 5%, מה שיגיע קודם. שילוב טוב של דיסציפלינה
ויעילות.

#### 🧾 Tax-Loss Harvesting (קציר הפסדים)
בחשבונות חייבי-מס (לא ב-IRA / 401k), נצל הפסדים על נייר: מכור XLE עם הפסד, קנה
**VDE (Vanguard Energy)** מיד. חשיפה כמעט זהה, אבל זה לא **wash sale** כי זו קרן
שונה. שמור את ההפסד למיסוי השנה.
"""
)

with st.expander("📖 העמקה: חישוב יעילות מס של Threshold Rebalance"):
    st.markdown(
        """
- **Calendar רבעוני** על שרוול 15%: ממוצע 3-4 שינויים בשנה, 12 פעולות מסחר.
- **Threshold 5%**: ממוצע 1-2 שינויים בשנה, 4-8 פעולות.
- **חיסכון מס נטו** בארה"ב בשיעור מס 25% על רווחים קצרי-טווח: ~0.3%-0.6% בשנה
  על תיק טיפוסי. נשמע מעט – זה משמעותי על פני 20 שנה.
        """
    )

st.divider()

# ---------------------------- BEHAVIORAL ----------------------------

st.markdown("## 🧠 Section 5 – מלכודות התנהגותיות")

st.markdown(
    """
האסטרטגיה רק חלק קטן מההצלחה. **המשמעת התנהגותית היא רוב הסיפור.** הנה החטאים
הקלאסיים שראיתי משקיעים פרטיים עושים שוב ושוב:

#### 1️⃣ הוספה אחרי רווח, הפחתה אחרי הפסד
פסיכולוגית טבעי, מתמטית הרסני. שרוול רוטציה **תמיד** יחווה drawdown – זה חלק
מהעיצוב. הוצאת כסף אחרי ירידה = להפסיד את ההתאוששות = לקנות בגבוה כשחוזרים.
**המספר חייב להישאר קבוע** עד שאתה משדרג שלב באופן יזום.

#### 2️⃣ הטיית הליבה ("רק קצת")
"אני אסובב את השרוול, ואני גם אקטין קצת את הליבה כי אני חושב ש-SPY יקר". זה
ההתחלה של הסוף. **חומת האש בין ליבה ולוויינים חייבת להיות קדושה.** אם תיגע בליבה,
תוך שנה כל התיק יהיה אקטיבי.

#### 3️⃣ הוספת מניות בודדות לצד הסקטורים
זה הופך **שיוך ביצועים (attribution)** לבלתי אפשרי. מי הרוויח – AAPL הספציפית
שלי או XLK? בלי לדעת, אי אפשר לשפר. **בחר אסטרטגיה אחת בכל שרוול.**

#### 4️⃣ בדיקה תכופה מדי
בדיקה יומית → ניחוש שני יומי → נטישת האסטרטגיה. **רוטציה סקטוריאלית היא תהליך
חודשי. סקירה חודשית מספיקה.** המסך הוא האויב.

#### 5️⃣ התעלמות ממסים
תשואה ברוטו של 12% בחשבון חייבי מס יכולה להיות 7% נטו אם התחלופה גבוהה.
**השוואות לפני מס מטעות.** תמיד חשב נטו לפי המדינה שלך.
"""
)

st.divider()

# ---------------------------- WHEN NOT TO ----------------------------

st.markdown("## 🚫 Section 6 – מתי **לא** לעשות Sector Rotation")

st.markdown(
    """
לא לכולם, ולא תמיד. הנה ארבעה תרחישים שבהם רוטציה היא טעות:

- **חשבון חייבי-מס קטן מ-$50K.** האלפא המצטברת קטנה מדי מכדי להתגבר על עלויות
  מסחר ותרגום מס. תיק קטן עדיף 100% פסיבי.
- **אי-יכולת להתחייב לסקירה חודשית מבוססת-כללים.** רוטציה דיסקרציונית הורסת את רוב
  האלפא בגלל הטיות התנהגותיות. אם אתה לא יכול להפעיל את הכלל גם כשכואב, אל תעשה.
- **ברוקר עם עלויות גבוהות.** 0.5%-1.0% לעסקה × 4 עסקאות לרבעון = 2%-4% עלות שנתית.
  גם אסטרטגיה שעובדת מפסידה לעלויות. השתמש ב-IBKR, Schwab, Fidelity או דומים
  עם 0% עמלות על ETF אמריקאי.
- **אופק השקעה קצר מ-3 שנים.** אסטרטגיות מומנטום פגיעות לזעזועים קצרי טווח.
  לכסף שאתה צריך ב-2026 או 2027, פסיבי + אג\"ח קצרות.
"""
)

st.divider()

# ---------------------------- WRAP ----------------------------

st.markdown("## 🎓 Section 7 – סיכום הקורס")

st.markdown(
    """
עברנו מסע ארוך. הנה מה שאתה צריך לקחת איתך:

- **Sector Rotation הקלאסי עובד בממוצע**, עם כאב משמעותי בדרך. אין ארוחות חינם.
- **מאקרו חי (מודול 4) + RRG (מודול 5)** נותנים יחד אות כיווני סביר. אחד לא מספיק.
- **מומנטום טהור (Backtest במודול 7)** מבוסס-כללים ועובד גם בלי שיקול דעת.
- **סייזינג הוא ההכרעה.** שרוול של 5% מוסיף תיבול בלי לסכן את הארוחה. שרוול של
  50% הוא הימור של חיים שדורש Edge אמיתי, שלרובכם אין (עדיין).

**הצעד הבא שלך:** קח את 90 הימים הבאים. הרץ את הרוטציה על נייר (Paper Trading)
בשרוול היפותטי של 10%. רשום כל החלטה. רשום מה הרגשת כשהיה drawdown. עוד 3 חודשים,
תחזור הנה וקרא את המודול הזה שוב. תופתע מכמה מטעויות התנהגותיות זיהית בעצמך.

**בהצלחה.** הקורס נגמר – העבודה האמיתית מתחילה.
"""
)

st.divider()

# ---------------------------- QUIZ ----------------------------

QUESTIONS = [
    {
        "q": "אתה זה עתה סיימת את הקורס. איזה גודל שרוול רוטציה מתאים לך?",
        "options": [
            "30% – אני בטוח באסטרטגיה",
            "0%-5% – שלב לימוד, פוזיציות קטנות",
            "50% – הולך All-In",
            "15%-30% – אם הבנתי את התיאוריה",
        ],
        "answer": 1,
        "explain": "מתחילים מ-0%-5% עד שיש לפחות שנה של ביצוע ממושמע. אסטרטגיה לא מוכחת + סייזינג גדול = הימור.",
    },
    {
        "q": "למה Threshold Rebalance עדיף בחשבון חייבי-מס?",
        "options": [
            "כי הוא נותן יותר אלפא",
            "כי הוא פחות מורכב מתמטית",
            "כי הוא מקטין תחלופה ובכך מקטין מס על רווחי הון קצרי-טווח",
            "כי הוא מבוסס על RRG",
        ],
        "answer": 2,
        "explain": "פחות פעולות מסחר → פחות מימוש רווחים → פחות מס. בחשבונות נטולי-מס (IRA) ההבדל זניח.",
    },
    {
        "q": "מהי 'חומת האש' בין ליבה ללוויינים במסגרת Core-Satellite?",
        "options": [
            "הליבה נשארת פסיבית; הלוויינים אקטיביים – ולא מערבבים ביניהם",
            "מבנה משפטי שמפריד את החשבונות",
            "תוכנת אבטחה של הברוקר",
            "החוק שאוסר להחזיק יותר מסקטור אחד",
        ],
        "answer": 0,
        "explain": "הליבה היא פסיבית לחלוטין ולא מוטה. הלוויינים אקטיביים. אסור 'לשפץ' את הליבה לפי השקפת רוטציה.",
    },
    {
        "q": "מהי הטעות ההתנהגותית הנפוצה ביותר בניהול שרוול אקטיבי?",
        "options": [
            "להחזיק יותר מדי סקטורים",
            "לחתוך כסף אחרי הפסדים ולהוסיף אחרי רווחים",
            "לבדוק את התיק פעם בחודש",
            "להשתמש ב-ETF במקום במניות בודדות",
        ],
        "answer": 1,
        "explain": "Drawdown הוא חלק מהעיצוב. יציאה אחרי ירידה = פספוס ההתאוששות = קנייה בגבוה. הסייז חייב להישאר קבוע.",
    },
    {
        "q": "באיזה מהמצבים הבאים **לא** כדאי לעשות Sector Rotation?",
        "options": [
            "חשבון חייבי-מס מתחת ל-$50K",
            "ברוקר עם 1% עמלת מסחר",
            "אופק השקעה של פחות מ-3 שנים",
            "כל התשובות נכונות",
        ],
        "answer": 3,
        "explain": "כל אחת מהן בנפרד הופכת את היחס תועלת/עלות לשלילי. שילוב של שתיים – על אחת כמה וכמה.",
    },
]

render_quiz("module_8", QUESTIONS)
