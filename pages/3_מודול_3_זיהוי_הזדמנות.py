from utils.page import bootstrap, page_end
from utils.quiz import render_quiz
import streamlit as st

bootstrap("מודול 3 – זיהוי הזדמנות")

st.markdown("## 3️⃣ מודול 3 – זיהוי הזדמנות אמיתית")
st.caption("מ-mid-price ל-Bid/Ask, חישוב רווח אחרי 3 ספרדים, slippage, סף הרווחיות.")
st.divider()

st.markdown(
    """
### מה לא סיפרנו לך במודול 2

במודול 2 השתמשנו ב-**mid-price** (ממוצע bid/ask) – שזו הפשטה. בשוק האמיתי
**אתה לא יכול לקנות במחיר ה-mid**. תמיד תקנה ב-Ask ותמכור ב-Bid. ולכן:

- בכל **leg** מתוך 3 הלולאה, אתה משלם **חצי ספרד**.
- ב-3 legs ביחד = **3 × חצי ספרד** של חצי ספרד = ~ספרד וחצי שלם.

נוסיף לזה: **slippage** (המחיר זז בין הרגע שראית למה שביצעת), עמלות הברוקר,
ו-swap אם החזקת overnight. ההר נהיה תלול.
"""
)

st.divider()

st.markdown("### 🎯 הלולאה הריאלית (לא ה-mid)")

st.markdown(
    """
**לולאה:** USD → EUR → JPY → USD.

מה אני באמת משלם ב-3 הצעדים?
"""
)

st.code(
    """STEP 1: USD → EUR     קונה EUR — משלם EUR/USD ASK
STEP 2: EUR → JPY     מוכר EUR מול JPY — מקבל EUR/JPY BID
STEP 3: JPY → USD     מוכר JPY מול USD — בעצם קונה USD/JPY,
                       זה אומר משלם USD/JPY ASK (כי אני קונה USD)""",
    language="text",
)

st.markdown(
    """
שים לב: בכל leg יש כיוון ספציפי – ולכן בכל leg משתמשים בצד הספציפי של הציטוט
(Bid או Ask). זה לא סימטרי, וזה למה ה"חצי ספרד" איננו זהה בכל leg.
"""
)

st.divider()

st.markdown("### 🧪 מחשבון רווח/הפסד עם Bid/Ask")

st.caption("הזן Bid ו-Ask לכל אחד מ-3 הזוגות. המחשבון יחשב את התוצאה הריאלית של הלולאה.")

st.markdown("**EUR/USD:**")
c1, c2 = st.columns(2)
with c1:
    eurusd_bid = st.number_input("EUR/USD Bid", min_value=0.0001, value=1.08495, step=0.00001, format="%.5f")
with c2:
    eurusd_ask = st.number_input("EUR/USD Ask", min_value=0.0001, value=1.08505, step=0.00001, format="%.5f")

st.markdown("**USD/JPY:**")
c3, c4 = st.columns(2)
with c3:
    usdjpy_bid = st.number_input("USD/JPY Bid", min_value=0.001, value=149.495, step=0.001, format="%.3f")
with c4:
    usdjpy_ask = st.number_input("USD/JPY Ask", min_value=0.001, value=149.505, step=0.001, format="%.3f")

st.markdown("**EUR/JPY:**")
c5, c6 = st.columns(2)
with c5:
    eurjpy_bid = st.number_input("EUR/JPY Bid", min_value=0.001, value=162.195, step=0.001, format="%.3f")
with c6:
    eurjpy_ask = st.number_input("EUR/JPY Ask", min_value=0.001, value=162.215, step=0.001, format="%.3f")

start_usd = st.number_input("💰 הון התחלתי (USD)", min_value=100.0, value=1_000_000.0, step=10_000.0, format="%.2f")

# Loop A: USD -> EUR -> JPY -> USD
# 1) USD->EUR: buy EUR, pay EUR/USD ASK -> EUR = USD / Ask
eur_amount_a = start_usd / eurusd_ask
# 2) EUR->JPY: sell EUR vs JPY, get EUR/JPY BID -> JPY = EUR * Bid
jpy_amount_a = eur_amount_a * eurjpy_bid
# 3) JPY->USD: sell JPY vs USD, equiv buying USD with JPY -> pay USD/JPY ASK -> USD = JPY / Ask
final_usd_a = jpy_amount_a / usdjpy_ask
pnl_a = final_usd_a - start_usd
pct_a = (pnl_a / start_usd) * 100

# Loop B: reverse: USD -> JPY -> EUR -> USD
# 1) USD->JPY: buy JPY (sell USD), get USD/JPY BID -> JPY = USD * Bid
jpy_amount_b = start_usd * usdjpy_bid
# 2) JPY->EUR: sell JPY vs EUR (buy EUR with JPY) -> pay EUR/JPY ASK -> EUR = JPY / Ask
eur_amount_b = jpy_amount_b / eurjpy_ask
# 3) EUR->USD: sell EUR vs USD, get EUR/USD BID -> USD = EUR * Bid
final_usd_b = eur_amount_b * eurusd_bid
pnl_b = final_usd_b - start_usd
pct_b = (pnl_b / start_usd) * 100

st.markdown("#### תוצאה ריאלית של הלולאה")
loop_col1, loop_col2 = st.columns(2)
with loop_col1:
    st.markdown("**כיוון A: USD → EUR → JPY → USD**")
    st.metric("USD סופי", f"{final_usd_a:,.2f}", delta=f"{pnl_a:+,.2f} ({pct_a:+.4f}%)")
with loop_col2:
    st.markdown("**כיוון B: USD → JPY → EUR → USD**")
    st.metric("USD סופי", f"{final_usd_b:,.2f}", delta=f"{pnl_b:+,.2f} ({pct_b:+.4f}%)")

best_pct = max(pct_a, pct_b)
if best_pct > 0.001:
    st.success(f"✅ הכיוון הטוב יותר מרוויח **{best_pct:+.4f}%** (לפני slippage ועמלות).")
elif best_pct > -0.001:
    st.info("⚖️ שני הכיוונים בערך אפס. הספרד אכל את הפערית. אין הזדמנות.")
else:
    st.error(f"❌ שני הכיוונים בהפסד ({best_pct:.4f}% הוא הטוב פחות). הספרד גדול מהפערית.")

st.caption("נסה: צמצם את הספרדים (Ask−Bid) ב-90% – תראה איך הרווח קופץ. זה למה ל-HFT יש יתרון.")

st.divider()

st.markdown("### 🎲 Slippage – מה זה ולמה זה חשוב")

st.markdown(
    """
**Slippage** = ההפרש בין המחיר שראית כשלחצת על "קנה" לבין המחיר שבאמת קיבלת.
הוא נובע מ:

1. **מהירות:** הזמן בין השליחה לעיבוד (יחידות מילישניות עד מאות מילישניות
   לקמעונאי, מיקרושניות לבנקים).
2. **נזילות:** אם ה-order שלך גדול ביחס לעומק ה-orderbook, אתה "אוכל" כמה רמות.
3. **תנודתיות:** בחדשות חמות המחיר רץ – תלחץ ב-1.0850 ותקבל 1.0855.

**Slippage טיפוסי בקמעונאי:**

- שעות שיא (London/NY), majors: **0.1–0.5 pip** לכיוון.
- שעות שקטות / חדשות: **1–5 pips** בקלות.
- ב-3 legs מצטבר slippage של **0.3–15 pips**.

**במונחי basis points** (לזוג כמו EUR/USD ב-1.0850): 1 pip ≈ 0.92 bp.
3 pips slippage = ~2.8 bp = יותר מכל הפערית התיאורטית שראינו במודול 2.
"""
)

st.divider()

st.markdown("### 🚦 סף הרווחיות – Break-Even")

st.markdown(
    """
כדי שעסקת ארביטראז' תהיה רווחית, **הפערית התיאורטית חייבת להיות גדולה מסכום העלויות**:
"""
)

st.latex(
    r"\text{Edge}_{\text{net}} \;=\; \text{Profit}_{\text{theoretical}} - \text{Spread}_{\text{total}} - \text{Slippage} - \text{Commission} - \text{Swap}"
)

st.markdown(
    """
דוגמה לחישוב הסף עבור קמעונאי טיפוסי:

| רכיב | עלות |
|---|---|
| 3 spreads (0.5 pip × 3 zogot) | ~1.4 bp |
| Slippage צפוי (3 legs, שעות שיא) | ~1.0 bp |
| Commission ($7 per $100k × 3 legs ÷ $1M) | ~2.1 bp |
| **סה"כ break-even** | **~4.5 bp** |

כלומר, **כדי להרוויח אפילו דולר אחד** קמעונאי צריך פערית גדולה מ-4.5 bp.
פערים כאלה קיימים אצל HFT שמודדים ב-microseconds, **לא** אצלך בטלפון על
פלטפורמה קמעונאית.
"""
)

st.warning(
    "⚠️ **המסקנה הקשה.** בשוק פורקס משוכלל, פערים בני-זיהוי לטווח ארוך = פשוט לא קיימים לקמעונאי. "
    "מי שמציע לך 'בוט ארביטראז' מובטח' – מנסה למכור לך אשליה."
)

st.divider()

render_quiz(
    "module3",
    [
        {
            "q": "כשאני 'קונה EUR מול USD', באיזה צד של הציטוט אני נמצא?",
            "options": [
                "Bid (מוכר)",
                "Mid (אמצע)",
                "Ask (קונה)",
                "תלוי בברוקר",
            ],
            "answer": 2,
            "explain": "תמיד קונים ב-Ask ומוכרים ב-Bid. הברוקר 'מציע' לך את הסחורה במחיר ה-Ask.",
        },
        {
            "q": "כמה ספרדים חצויים אתה משלם בלולאה של 3 legs?",
            "options": ["1", "1.5", "3", "6"],
            "answer": 2,
            "explain": "כל leg = חצי ספרד (אתה חוצה מ-mid לצד אחד), 3 legs = 3 חצאי ספרד ≈ ספרד וחצי שלם של זוג טיפוסי.",
        },
        {
            "q": "מהו slippage?",
            "options": [
                "עמלת הברוקר",
                "ההפרש בין מחיר שראית למחיר שקיבלת",
                "ריבית overnight",
                "מס רווחי הון",
            ],
            "answer": 1,
            "explain": "Slippage = price slippage. נובע מהשהיית רשת, נזילות חסרה, או תנודתיות מהירה.",
        },
        {
            "q": "אם הפערית התיאורטית = 3 bp ועלויות = 4.5 bp, מה התוצאה?",
            "options": [
                "רווח של 1.5 bp",
                "הפסד של 1.5 bp",
                "אפס בדיוק",
                "תלוי בכיוון",
            ],
            "answer": 1,
            "explain": "3 − 4.5 = −1.5 bp. הפסד ודאי לפני שבכלל סיכון, latency, או כל גורם נוסף.",
        },
        {
            "q": "באיזו שעה הספרדים יהיו הכי צרים בדרך כלל?",
            "options": [
                "סשן Sydney לבדו",
                "חפיפת London × NY",
                "סופ\"ש",
                "פתיחת השבוע באוסטרליה",
            ],
            "answer": 1,
            "explain": "12:00–16:00 UTC = שיא הנזילות העולמי, מה שמצמצם את הספרדים. בזמנים שקטים הספרדים מתרחבים.",
        },
    ],
)

page_end()
