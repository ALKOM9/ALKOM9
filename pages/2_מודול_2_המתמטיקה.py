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

בארביטראז' משולש סוגרים **לולאה של 3 עסקאות** שמתחילה ומסתיימת באותו מטבע.
אם המחיר של ה-cross בשוק שונה מה-cross המחושב מתוך שני זוגות אחרים – נוצרת
פערית קטנה. בעולם בלי עלויות, יכולת לעבור על הלולאה ולקבל יותר ממה ששמת.

**דוגמה ללולאה:** USD → EUR → JPY → USD.
"""
)

st.divider()

st.markdown("### 🧮 הנוסחה המרכזית – Implied Cross")

st.markdown(
    """
אם אני יודע שני מחירים: `EUR/USD` ו-`USD/JPY`, אני יכול **לחשב** מה צריך
להיות `EUR/JPY` באופן עקיף:
"""
)

st.latex(r"\text{EUR/JPY}_{\text{implied}} \;=\; \text{EUR/USD} \times \text{USD/JPY}")

st.markdown(
    """
**למה זה עובד?** כי "כמה ין בעבור יורו" =
"כמה דולר בעבור יורו" × "כמה ין בעבור דולר".
ה-USD מתבטל מתמטית.

**מתי קונים cross ישירות במקום לחשב?** ההפרש בין ה-implied (עקיף) ל-market (ישיר)
הוא בדיוק ההזדמנות.
"""
)

st.divider()

st.markdown("### 🔁 התנאי לארביטראז' (לולאה רווחית)")

st.markdown(
    """
מתחילים עם 1 דולר. עוברים 3 המרות. בודקים אם חזרנו ליותר מ-1:
"""
)

st.latex(
    r"\text{Profit Factor} \;=\; \frac{1}{\text{EUR/USD}} \times \frac{1}{\text{USD/JPY}} \times \text{EUR/JPY}_{\text{market}}"
)

st.markdown(
    """
או באופן שקול:
"""
)

st.latex(
    r"\text{Profit Factor} \;=\; \frac{\text{EUR/JPY}_{\text{market}}}{\text{EUR/JPY}_{\text{implied}}}"
)

st.markdown(
    """
- אם **Profit Factor > 1** → הלולאה רווחית בכיוון הזה (אגנוסטית לעלויות).
- אם **Profit Factor < 1** → הלולאה רווחית **בכיוון ההפוך**.
- אם **Profit Factor = 1.000…** (מדויק) → אין הזדמנות, השוק "מתוקן".

**בלי עלויות העולם הזה לא קיים** – עלויות (ספרד, עמלה, slippage) הופכות
כמעט כל פערית קטנה ללא-רווחית. נראה את זה במספרים במודול 3.
"""
)

st.divider()

st.markdown("### 🧪 מחשבון אינטראקטיבי")

st.caption("הזן שלושה ציטוטים *תיאורטיים* (mid-price, בלי ספרד). המחשבון יראה את ה-implied, את הסטייה ואת ה-profit factor.")

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
    st.success("⚖️ השוק מתוקן (סטייה מתחת ל-0.005%). אין הזדמנות תיאורטית.")
elif profit_pct > 0:
    st.info(f"🔁 בלולאה **USD → EUR → JPY → USD** יש +{profit_pct:.4f}% תיאורטיים (לפני עלויות).")
else:
    st.info(f"🔁 בלולאה ההפוכה **USD → JPY → EUR → USD** יש +{-profit_pct:.4f}% תיאורטיים (לפני עלויות).")

st.caption("💡 ספרדים טיפוסיים בעולם האמיתי מוסיפים ~0.5–2 pip לכל leg. נחזור לזה במודול 3.")

st.divider()

st.markdown("### 🧠 דוגמה מספרית מלאה")

st.markdown(
    """
נניח שצברתי 1,000,000 דולר. ה-mid-prices:

- `EUR/USD = 1.0850` (1 EUR = 1.0850 USD)
- `USD/JPY = 149.50` (1 USD = 149.50 JPY)
- `EUR/JPY = 162.20` (1 EUR = 162.20 JPY)

**Implied EUR/JPY** = 1.0850 × 149.50 = **162.21175**.
ה-market (162.20) **קצת נמוך**, כלומר היורו "זול" בציטוט הישיר.

**הלולאה:** USD → JPY (קנה ין) → EUR (קנה יורו עם הין) → USD (חזרה לדולר).
"""
)

st.code(
    """STEP 1: USD → JPY     1,000,000 × 149.50 = 149,500,000 JPY
STEP 2: JPY → EUR     149,500,000 / 162.20 ≈ 921,701.6 EUR
STEP 3: EUR → USD     921,701.6 × 1.0850 ≈ 1,000,046.2 USD
RESULT: +46.2 USD מתוך מיליון = 0.0046% תיאורטי (4.6 בסיס points).""",
    language="text",
)

st.warning(
    "⚠️ **4.6 בסיס points זה הגבול התחתון.** ספרדים אמיתיים על 3 legs קלים יבלעו את כל זה. "
    "בנקים גדולים סוגרים פערים קטנים מ-0.5 bp תוך מיקרושניות. למסחר קמעונאי אין סיכוי בפערים בגודל הזה."
)

st.divider()

render_quiz(
    "module2",
    [
        {
            "q": "מהי הנוסחה ל-Implied EUR/JPY?",
            "options": [
                "EUR/USD + USD/JPY",
                "EUR/USD − USD/JPY",
                "EUR/USD × USD/JPY",
                "EUR/USD / USD/JPY",
            ],
            "answer": 2,
            "explain": "כפל. ה-USD מתבטל: (EUR/USD) × (USD/JPY) = EUR/JPY.",
        },
        {
            "q": "אם Implied = 162.21 וה-market = 162.20, מה ה-Profit Factor?",
            "options": ["1.0000", "0.99994", "1.00006", "162.20"],
            "answer": 1,
            "explain": "162.20 ÷ 162.21 ≈ 0.99994. כלומר הלולאה בכיוון הזה מפסידה ~0.006% לפני עלויות. הכיוון ההפוך מרוויח את אותה הסטייה.",
        },
        {
            "q": "Profit Factor = 1 פירושו…",
            "options": [
                "רווח גדול",
                "השוק מתוקן, אין הזדמנות",
                "הפסד גדול",
                "צריך לקנות יותר",
            ],
            "answer": 1,
            "explain": "PF=1 פירוש לולאה ש'מחזירה' את מה ששמת – בדיוק. אין פערית, אין סיבה להריץ אותה.",
        },
        {
            "q": "אם Profit Factor < 1, מה עושים?",
            "options": [
                "עוצרים",
                "מריצים בכיוון ההפוך",
                "מכפילים את הסכום",
                "מחכים שעה",
            ],
            "answer": 1,
            "explain": "אותה לולאה נסגרת בכיוון ההפוך – אם A→B→C→A מפסידה, אז A→C→B→A מרוויחה בדיוק אותו אחוז.",
        },
        {
            "q": "מהו 4.6 basis points במונחי אחוז?",
            "options": ["0.46%", "0.046%", "0.0046%", "46%"],
            "answer": 2,
            "explain": "1 basis point = 0.01%. 4.6 bp = 0.046%. וזה לפני שלקחנו ספרדים – שיבלעו את הרווח כולו.",
        },
    ],
)

page_end()
