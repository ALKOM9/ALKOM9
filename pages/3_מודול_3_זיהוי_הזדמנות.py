from utils.page import bootstrap, page_end
from utils.quiz import render_quiz
import streamlit as st

bootstrap("מודול 3 – זיהוי הזדמנות")

st.markdown("## 3️⃣ מודול 3 – זיהוי הזדמנות אמיתית")
st.caption("מעבר מ-mid price ל-Bid/Ask, חישוב רווח אחרי שלושה ספרדים, slippage וסף הרווחיות.")
st.divider()

st.markdown(
    """
### מה שלא סיפרתי לכם במודול 2

במודול 2 השתמשנו ב-**mid price** (הממוצע בין Bid ל-Ask), וזו הפשטה.
בשוק האמיתי **אי אפשר לקנות במחיר ה-mid**: תמיד קונים ב-Ask ומוכרים ב-Bid.
מכאן נובע:

- בכל **leg** (צלע) של הלולאה משלמים **חצי ספרד**.
- בלולאה של שלוש צלעות = **3 חצאי ספרד**, כלומר בערך ספרד וחצי שלם.

לזה מתווספים: **slippage** (פער בין המחיר שראיתם לבין המחיר שבו העסקה
התבצעה בפועל), עמלות הברוקר, ו-swap אם החזקתם פוזיציה לתוך הלילה.
ההר נהיה תלול במהירות.
"""
)

st.divider()

st.markdown("### 🎯 הלולאה בעולם האמיתי (לא mid)")

st.markdown("**לולאה:** USD → EUR → JPY → USD. מה משלמים בפועל בכל אחד משלושת הצעדים?")

st.code(
    """STEP 1: USD → EUR     קונים EUR מול USD       → משלמים EUR/USD ASK
STEP 2: EUR → JPY     מוכרים EUR מול JPY      → מקבלים EUR/JPY BID
STEP 3: JPY → USD     מוכרים JPY מול USD,     → משלמים USD/JPY ASK
                       בפועל קונים USD עם JPY
""",
    language="text",
)

st.markdown(
    """
שימו לב: לכל leg יש כיוון ספציפי, ובכל leg מתבצע שימוש בצד אחר של הציטוט
(Bid או Ask). לכן "חצי הספרד" אינו זהה בכל leg, אבל הסכום הכולל קרוב לו.
"""
)

st.divider()

st.markdown("### 🧪 מחשבון רווח/הפסד עם Bid ו-Ask")

st.caption("הזינו Bid ו-Ask לכל אחד משלושת הזוגות. המחשבון יציג את התוצאה הריאלית של הלולאה בשני הכיוונים.")

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

start_usd = st.number_input("💰 הון התחלתי ($)", min_value=100.0, value=1_000_000.0, step=10_000.0, format="%.2f")

eur_amount_a = start_usd / eurusd_ask
jpy_amount_a = eur_amount_a * eurjpy_bid
final_usd_a = jpy_amount_a / usdjpy_ask
pnl_a = final_usd_a - start_usd
pct_a = (pnl_a / start_usd) * 100

jpy_amount_b = start_usd * usdjpy_bid
eur_amount_b = jpy_amount_b / eurjpy_ask
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
    st.info("⚖️ שני הכיוונים סביב האפס. הספרד אכל את הפערית, ואין הזדמנות.")
else:
    st.error(f"❌ שני הכיוונים בהפסד (הטוב מבין השניים: {best_pct:.4f}%). הספרד גדול מהפערית.")

st.caption("נסו להקטין את הספרדים (Ask − Bid) ב-90% – תראו כיצד הרווח קופץ. בדיוק לזה ל-HFT יש יתרון.")

st.divider()

st.markdown("### 🎲 Slippage – מה זה ולמה זה חשוב")

st.markdown(
    """
**Slippage** = הפער בין המחיר שראיתם ברגע שלחצתם "קנה" לבין המחיר שבו העסקה
בוצעה בפועל. הוא נובע מ:

1. **מהירות תגובה:** הזמן בין השליחה לעיבוד (יחידות מילישניות עד מאות
   מילישניות אצל קמעונאי, מיקרושניות אצל בנקים).
2. **נזילות:** אם ה-order שלכם גדול ביחס לעומק ה-orderbook, אתם "אוכלים"
   כמה רמות מחיר.
3. **תנודתיות:** ברגעי חדשות חמות המחיר רץ – לוחצים על 1.0850 ומקבלים 1.0855.

**Slippage טיפוסי אצל קמעונאי:**

- שעות שיא (London/NY), Majors: **0.1–0.5 pip** לכיוון.
- שעות שקטות או רגעי חדשות: **1–5 pip** בקלות.
- בשלוש צלעות מצטבר slippage של **0.3–15 pip**.

**במונחי basis points** (לזוג כמו EUR/USD ב-1.0850): 1 pip ≈ 0.92 bp.
3 pip של slippage = כ-2.8 bp = יותר מכל הפערית התיאורטית שראינו במודול 2.
"""
)

st.divider()

st.markdown("### 🚦 סף הרווחיות – Break-Even")

st.markdown(
    """
כדי שעסקת ארביטראז' תהיה רווחית, **הפערית התיאורטית חייבת להיות גדולה מסך
העלויות**:
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
| שלושה ספרדים (0.5 pip × 3 זוגות) | ~1.4 bp |
| Slippage צפוי (3 legs, שעות שיא) | ~1.0 bp |
| עמלות ($7 לכל $100k × 3 legs ÷ $1M) | ~2.1 bp |
| **סך הכל break-even** | **~4.5 bp** |

כלומר, **כדי להרוויח אפילו דולר אחד** קמעונאי זקוק לפערית גדולה מ-4.5 bp.
פערים כאלה קיימים אצל HFT שמודדים זמן ב-microseconds, **לא** אצל מי שיושב
מול אפליקציה בטלפון.
"""
)

st.warning(
    "⚠️ **המסקנה הקשה.** בשוק מט\"ח משוכלל, פערים בני זיהוי שמחזיקים מעמד "
    "לאורך זמן פשוט לא קיימים עבור הקמעונאי. מי שמציע לכם 'בוט ארביטראז' "
    "שמרוויח באופן מובטח' – מנסה למכור לכם אשליה."
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
            "explain": "תמיד קונים ב-Ask ומוכרים ב-Bid. הברוקר 'מציע' לכם את הסחורה במחיר ה-Ask.",
        },
        {
            "q": "כמה ספרדים חצויים משלמים בלולאה של שלוש צלעות?",
            "options": ["1", "1.5", "3", "6"],
            "answer": 2,
            "explain": "כל leg = חצי ספרד (חוצים מ-mid לצד אחד), 3 legs = שלושה חצאי ספרד, כלומר בערך ספרד וחצי שלם של זוג טיפוסי.",
        },
        {
            "q": "מהו Slippage?",
            "options": [
                "עמלת הברוקר",
                "הפער בין המחיר שראיתם למחיר שבו העסקה בוצעה",
                "ריבית overnight",
                "מס רווחי הון",
            ],
            "answer": 1,
            "explain": "Slippage = החלקת מחיר. נובע מהשהיית רשת, נזילות חסרה, או תנודתיות מהירה.",
        },
        {
            "q": "אם הפערית התיאורטית = 3 bp והעלויות = 4.5 bp, מה התוצאה?",
            "options": [
                "רווח של 1.5 bp",
                "הפסד של 1.5 bp",
                "אפס בדיוק",
                "תלוי בכיוון",
            ],
            "answer": 1,
            "explain": "3 − 4.5 = −1.5 bp. הפסד ודאי, עוד לפני שלקחנו בחשבון סיכון, latency או כל גורם נוסף.",
        },
        {
            "q": "באיזו שעה הספרדים יהיו הצרים ביותר בדרך כלל?",
            "options": [
                "סשן Sydney לבדו",
                "חפיפת London × NY",
                "סוף השבוע",
                "פתיחת השבוע באוסטרליה",
            ],
            "answer": 1,
            "explain": "12:00–16:00 UTC = שיא הנזילות העולמי, ולכן הספרדים הצרים ביותר. בזמנים שקטים הספרדים מתרחבים.",
        },
    ],
)

page_end()
