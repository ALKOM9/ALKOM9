from utils.page import bootstrap, page_end
from utils.quiz import render_quiz
import streamlit as st

bootstrap("מודול 2 – המתמטיקה")

st.markdown("## 2️⃣ מודול 2 – המתמטיקה של ארביטראז' משולש")
st.caption("Implied cross rate, הנוסחה המרכזית, ומחשבון אינטראקטיבי.")
st.divider()

st.markdown(
    """
### הרעיון

בארביטראז' משולש סוגרים **לולאה של שלוש עסקאות** שמתחילה ומסתיימת באותו מטבע.
אם מחיר ה-cross שמופיע בשוק שונה מה-cross שמתקבל מחישוב של שני זוגות אחרים,
נוצר פער קטן. בעולם תיאורטי ללא עלויות אפשר היה לעבור על הלולאה ולקבל יותר
ממה ששמתם.

**דוגמה ללולאה:** USD → EUR → JPY → USD.
"""
)

st.divider()

st.markdown("### 🧮 הנוסחה המרכזית – Implied Cross")

st.markdown(
    """
אם ידועים שני המחירים `EUR/USD` ו-`USD/JPY`, אפשר **לחשב** מה צריך להיות
`EUR/JPY` בעקיפין:
"""
)

st.latex(r"\text{EUR/JPY}_{\text{implied}} \;=\; \text{EUR/USD} \times \text{USD/JPY}")

st.markdown(
    """
**למה זה עובד?** כי "כמה ין שווה יורו" =
"כמה דולר שווה יורו" × "כמה ין שווה דולר". הדולר מצטמצם מתמטית, ונשארת היחס
הישיר בין יורו לין.

**מתי כדאי לקנות את ה-cross ישירות, ומתי לעבור דרך הצלעות?** ההפרש בין
ה-implied (העקיף) למחיר הישיר בשוק הוא בדיוק ההזדמנות התיאורטית.
"""
)

st.divider()

st.markdown("### 🔁 התנאי לארביטראז' (לולאה רווחית)")

st.markdown(
    """
מתחילים עם דולר אחד, עוברים שלוש המרות, ובודקים אם חזרנו לכמות שגדולה מ-1:
"""
)

st.latex(
    r"\text{Profit Factor} \;=\; \frac{1}{\text{EUR/USD}} \times \frac{1}{\text{USD/JPY}} \times \text{EUR/JPY}_{\text{market}}"
)

st.markdown("ובאופן שקול:")

st.latex(
    r"\text{Profit Factor} \;=\; \frac{\text{EUR/JPY}_{\text{market}}}{\text{EUR/JPY}_{\text{implied}}}"
)

st.markdown(
    """
- אם **Profit Factor > 1** – הלולאה רווחית בכיוון זה (לפני עלויות).
- אם **Profit Factor < 1** – הלולאה רווחית **בכיוון ההפוך**.
- אם **Profit Factor = 1.0000…** במדויק – השוק "מתוקן" ואין הזדמנות.

**בעולם ללא עלויות הזה לא קיים.** עלויות (ספרד, עמלה, slippage) הופכות כמעט
כל פער קטן לבלתי-רווחי. נראה את המספרים במודול 3.
"""
)

st.divider()

st.markdown("### 🧪 מחשבון אינטראקטיבי")

st.caption("הזינו שלושה ציטוטים **תיאורטיים** (mid-price ללא ספרד). המחשבון יציג את ה-implied, את הסטייה ואת ה-Profit Factor.")

col1, col2 = st.columns(2)
with col1:
    eur_usd = st.number_input("EUR/USD (mid)", min_value=0.0001, value=1.0850, step=0.0001, format="%.5f")
    usd_jpy = st.number_input("USD/JPY (mid)", min_value=0.001, value=149.50, step=0.01, format="%.3f")
with col2:
    eur_jpy_market = st.number_input("EUR/JPY בשוק (mid)", min_value=0.001, value=162.20, step=0.01, format="%.3f")

eur_jpy_implied = eur_usd * usd_jpy
deviation_abs = eur_jpy_market - eur_jpy_implied
deviation_pct = (deviation_abs / eur_jpy_implied) * 100 if eur_jpy_implied else 0
profit_factor = eur_jpy_market / eur_jpy_implied if eur_jpy_implied else 0
profit_pct = (profit_factor - 1) * 100

st.markdown("#### תוצאות")
m1, m2, m3 = st.columns(3)
m1.metric("EUR/JPY Implied", f"{eur_jpy_implied:.4f}")
m2.metric("סטייה (pip)", f"{deviation_abs * 100:.1f}")
m3.metric("Profit Factor", f"{profit_factor:.6f}", delta=f"{profit_pct:+.4f}%")

if abs(profit_pct) < 0.005:
    st.success("⚖️ השוק מתוקן (סטייה קטנה מ-0.005%). אין הזדמנות תיאורטית.")
elif profit_pct > 0:
    st.info(f"🔁 בלולאה **USD → EUR → JPY → USD** יש רווח תיאורטי של +{profit_pct:.4f}% (לפני עלויות).")
else:
    st.info(f"🔁 בלולאה ההפוכה **USD → JPY → EUR → USD** יש רווח תיאורטי של +{-profit_pct:.4f}% (לפני עלויות).")

st.caption("💡 ספרדים בעולם האמיתי מוסיפים בדרך כלל 0.5–2 pip לכל leg. נחזור לכך במודול 3.")

st.divider()

st.markdown("### 🧠 דוגמה מספרית מלאה")

st.markdown(
    """
נניח שצברנו מיליון דולר. שלושת המחירים (mid):

- `EUR/USD = 1.0850` (1 EUR = 1.0850 USD)
- `USD/JPY = 149.50` (1 USD = 149.50 JPY)
- `EUR/JPY = 162.20` (1 EUR = 162.20 JPY)

**Implied EUR/JPY** = 1.0850 × 149.50 = **162.21175**.
ה-market (162.20) נמוך מעט מה-implied, כלומר היורו "זול" יחסית בציטוט הישיר.

**הלולאה:** USD → JPY (קונים ין) → EUR (קונים יורו עם הין) → USD (חוזרים לדולר).
"""
)

st.code(
    """STEP 1: USD → JPY     1,000,000 × 149.50 = 149,500,000 JPY
STEP 2: JPY → EUR     149,500,000 / 162.20 ≈ 921,701.6 EUR
STEP 3: EUR → USD     921,701.6 × 1.0850 ≈ 1,000,046.2 USD
תוצאה:                +46.2 USD מתוך מיליון = 0.0046% (4.6 basis points)""",
    language="text",
)

st.warning(
    "⚠️ **4.6 basis points הם הגבול העליון התיאורטי.** ספרדים אמיתיים על שלוש "
    "צלעות יבלעו את כל הרווח הזה. בנקים גדולים סוגרים פערים שקטנים מ-0.5 bp "
    "תוך מיקרושניות. לקמעונאי אין סיכוי לתפוס פערים בגודל הזה."
)

st.divider()

render_quiz(
    "module2",
    [
        {
            "q": "מהי הנוסחה הנכונה ל-Implied EUR/JPY?",
            "options": [
                "EUR/USD + USD/JPY",
                "EUR/USD − USD/JPY",
                "EUR/USD × USD/JPY",
                "EUR/USD / USD/JPY",
            ],
            "answer": 2,
            "explain": "מכפילים. ה-USD מצטמצם מתמטית: (EUR/USD) × (USD/JPY) = EUR/JPY.",
        },
        {
            "q": "אם Implied = 162.21 וה-market = 162.20, מהו ה-Profit Factor?",
            "options": ["1.0000", "0.99994", "1.00006", "162.20"],
            "answer": 1,
            "explain": "162.20 ÷ 162.21 ≈ 0.99994. כלומר, הלולאה בכיוון זה מפסידה כ-0.006% לפני עלויות. הכיוון ההפוך מרוויח את אותה הסטייה.",
        },
        {
            "q": "מה המשמעות של Profit Factor = 1?",
            "options": [
                "רווח גדול",
                "השוק מתוקן ואין הזדמנות",
                "הפסד גדול",
                "צריך להגדיל את הסכום",
            ],
            "answer": 1,
            "explain": "PF=1 פירושו שהלולאה 'מחזירה' בדיוק את ההון. אין פערית, ולכן אין סיבה לבצע אותה.",
        },
        {
            "q": "אם Profit Factor < 1, מה כדאי לעשות?",
            "options": [
                "לעצור",
                "להריץ את הלולאה בכיוון ההפוך",
                "להכפיל את הסכום",
                "להמתין שעה",
            ],
            "answer": 1,
            "explain": "אותה לולאה רווחית בכיוון ההפוך. אם A→B→C→A מפסידה X%, אז A→C→B→A מרוויחה בדיוק X% (לפני עלויות).",
        },
        {
            "q": "מהם 4.6 basis points במונחי אחוזים?",
            "options": ["0.46%", "0.046%", "0.0046%", "46%"],
            "answer": 2,
            "explain": "1 basis point = 0.01%. ולכן 4.6 bp = 0.046%. וזה לפני קיזוז של ספרדים – שיבלעו את כל הרווח.",
        },
    ],
)

page_end()
