from utils.page import bootstrap, page_end
from utils.quiz import render_quiz
import streamlit as st

bootstrap("מודול 8 – ניהול סיכונים")

st.markdown("## 8️⃣ מודול 8 – ניהול סיכונים בארביטראז' פורקס")
st.caption("Execution risk, latency risk, broker risk, leg risk, position sizing.")
st.divider()

st.markdown(
    """
### למה זה לא 'סיכון אפס' למרות הסיפור

ההגדרה האקדמית של ארביטראז' היא **רווח ללא סיכון**. במציאות, ברגע שאתה רץ
לבצע 3 עסקאות בפלטפורמה אמיתית, מתווספים סיכונים:
"""
)

st.divider()

st.markdown("### 🎯 1. Execution Risk – הסיכון שלא תבצע את כל ה-3 ה-legs")

st.markdown(
    """
ארביטראז' משולש דורש לסגור **3 עסקאות בו-זמנית**. אבל בפועל:

- אתה שולח leg 1 → ה-LP מקבל → מבצע → מאשר. זמן: 5–50 ms.
- שולח leg 2 → אותה דבר.
- שולח leg 3 → אותה דבר.

**בזמן הזה (15–150 ms בסך הכל), המחירים זזו.** הפערית שראית כשתכננת
כבר לא קיימת. אם חישבת רווח של 3 bp ובינתיים שני המחירים זזו לרעתך
בכל 1 bp – נשארת עם הפסד.

**מה קורה אם leg כושל באמצע?** נשארת עם פוזיציה לא מאוזנת. למשל קנית EUR
ומכרת JPY, אבל לא ביצעת את ה-USD-leg. עכשיו אתה חשוף לסיכון מטבע ישיר.
חייב לסגור את הפוזיציה במחיר שייתן הברוקר – לרוב במחיר רע, ולפעמים בהפסד
שגדול ממה שתכננת לרווח.
"""
)

st.warning(
    "⚠️ HFT מקצועי **מבצע את 3 ה-legs במקביל דרך אטומיק engine**. "
    "קמעונאי עם UI ידני **לא יכול לעשות זאת**. אתה תמיד מסתכן ב-leg-risk."
)

st.divider()

st.markdown("### ⏱️ 2. Latency Risk – הזמן בין החלטה לביצוע")

st.markdown(
    """
מילישנייה אחת מספיקה כדי שהפערית תיעלם. במודול 4 ראינו שמיקרושניות הן
ההפרש בין HFT לקמעונאי – וזה רלוונטי גם פה.

**מקורות לטנסי בקמעונאי:**
1. עיבוד הקליק בדפדפן/אפליקציה (1–5 ms).
2. WiFi/4G לאינטרנט שלך (10–80 ms).
3. אינטרנט עד לברוקר (20–150 ms).
4. תור פנימי של הברוקר (5–50 ms).
5. הברוקר → LP (10–100 ms).
6. LP last-look (5–30 ms).

**סה"כ ~50–400 ms.** בזמן הזה השוק מצליח לעשות מיליון אירועים.
"""
)

st.divider()

st.markdown("### 🏦 3. Broker Risk – הסיכון מהברוקר עצמו")

st.markdown(
    """
- **חדלות פירעון** – הברוקר פושט רגל ואתה מאבד את הכסף שלא היה מבוטח.
  בארה"ב יש SIPC (עד $500k), באירופה ICF (€20k), בישראל אין כיסוי מקביל
  משמעותי לפורקס OTC. בדוק לאן הופקד הכסף שלך.
- **שינויי תנאים פתאומיים** – הרחבת ספרדים, הגדלת requirements, סגירת
  פוזיציות באופן חד צדדי בעת תנודתיות.
- **מניפולציה במחירים** (Market Maker) – stop hunting, slippage לא סימטרי.
- **הקפאת חשבון / עיכוב משיכות** – אם החשבון "מעורר חשד".

**כללי אצבע בסיסיים:**
1. ברוקרים מפוקחים (FCA UK, ASIC אוסטרליה, BaFin גרמניה, ESMA EU) > non-regulated.
2. כסף מופרד (segregated funds) > omnibus.
3. ביקורות (audited) חיצוניות > self-reported.
4. ביקורות עצמאיות (forexpeacearmy, trustpilot) – קרא תלונות, לא שבחים.
"""
)

st.divider()

st.markdown("### 💸 4. Counterparty Risk – הצד השני בעסקה")

st.markdown(
    """
אצל Market Maker, **הברוקר הוא הצד השני**. הוא יכול:
- לתת לך ספרד טוב כשאתה רגיל, ולהרחיב כשהוא מזהה אסטרטגיה רווחית מצידך.
- "להתאים" execution כדי להפסיד אותך (B-book accounting).
- לסיים מולך התקשרות ולמכור את היתרה.

אצל ECN/STP זה פחות – אבל קיים סיכון של LP אחד שלוקח על עצמו מעט מדי
ועלול לדחות ביצועים.
"""
)

st.divider()

st.markdown("### 📏 5. Position Sizing – כמה לסכן בעסקה")

st.markdown(
    """
גם אם הכל מסתדר טכנית, אתה עדיין צריך לדעת **כמה כסף לסכן**.
כללי אצבע סטנדרטיים בעולם המסחר:

- **1% rule** – לא לסכן יותר מ-1% מההון בעסקה בודדת.
- **2% rule** – הגבול המקסימלי לטרייידר אגרסיבי.
- **Risk of Ruin** – נוסחה: הסיכוי לאבד את כל ההון אם יש לך אחוז הצלחה p
  וסיכון לעסקה r:
"""
)

st.latex(r"\text{RoR} \approx \left(\frac{1-p}{p}\right)^{N}")

st.markdown(
    """
- p = הסתברות לעסקה רווחית (אחרי עלויות).
- N = מספר עסקאות שאתה מסוגל לעמוד בהפסד שלהן (לרוב N = 1/risk_pct).

**בארביטראז' קמעונאי p לרוב נמוך מ-0.5** (כי עלויות בולעות את הפערית).
זה אומר ש-RoR מתקרב ל-100% – כלומר **תאבד את כל ההון מתישהו** עם הסתברות גבוהה.
"""
)

st.error(
    "⛔ **אם p < 0.5 אחרי עלויות, אסטרטגיה עם risk_pct חיובי תוביל ל-bankruptcy בהסתברות 1.** "
    "זו תוצאה מתמטית, לא דעה. הימור הוא הימור גם כשקוראים לו 'ארביטראז'."
)

st.divider()

st.markdown("### 🧮 מחשבון Risk of Ruin")

c1, c2, c3 = st.columns(3)
with c1:
    win_prob = st.slider("הסתברות הצלחה p", 0.30, 0.70, 0.45, 0.01)
with c2:
    risk_per_trade = st.slider("Risk per trade (%)", 0.5, 10.0, 2.0, 0.5)
with c3:
    expected_trades = st.slider("מס' עסקאות צפויות", 10, 1000, 100, 10)

# Simplified RoR for fixed-fractional with binary outcomes:
# probability that the gambler's ruin starts at capital K (in units of risk).
# Using approximation: (q/p)^N where N = 100/risk_pct (number of losses to ruin) and q=1-p
N_to_ruin = 100 / risk_per_trade
q = 1 - win_prob
if win_prob == 0.5:
    ror = 1.0 if expected_trades >= N_to_ruin else expected_trades / N_to_ruin
elif win_prob < 0.5:
    # Underdog: ruin probability ≈ 1 if enough trades happen
    ror = min(1.0, (q / win_prob) ** N_to_ruin)
    # Adjust by # of trades (rough): if not enough trades, lower
    if expected_trades < N_to_ruin * 3:
        ror = min(ror, expected_trades / (N_to_ruin * 3))
else:
    ror = (q / win_prob) ** N_to_ruin

ror_pct = ror * 100

mcol1, mcol2 = st.columns(2)
mcol1.metric("Risk of Ruin (משוער)", f"{ror_pct:.1f}%")
mcol2.metric("עסקאות עד פשיטת רגל אם תפסיד ברצף", f"{int(N_to_ruin)}")

if ror_pct > 50:
    st.error(f"❌ סיכון פשיטת רגל גבוה ({ror_pct:.0f}%). אסטרטגיה זאת לא קיימא.")
elif ror_pct > 20:
    st.warning(f"⚠️ סיכון משמעותי לפשיטת רגל ({ror_pct:.0f}%). שקול להקטין risk-per-trade.")
elif ror_pct > 5:
    st.info(f"📐 סיכון מתון לפשיטת רגל ({ror_pct:.0f}%).")
else:
    st.success(f"✅ סיכון נמוך ({ror_pct:.1f}%) – אבל זה דורש edge אמיתי (p > 0.55).")

st.caption("💡 שיט את p ל-0.45 ואת risk ל-5% – תראה שהסיכוי לאבד הכל מטפס לעשרות אחוזים תוך 100 עסקאות.")

st.divider()

st.markdown("### 🛡️ סיכום הגנות")

st.markdown(
    """
1. **אל תסחר ארביטראז' פורקס בכסף אמיתי** אלא אם יש לך תשתית מקצועית
   (colocation, FIX feed, IT engineer צמוד). כקמעונאי – זה לא רלוונטי.
2. אם בכל זאת – **התחל ב-demo**. רוץ 500 עסקאות בדמו, מדוד P&L אמיתי
   (עם slippage, requotes), ובדוק האם יש edge.
3. **אל תסכן יותר מ-1% מההון** בעסקה. גם אם אתה משוכנע שיש פערית.
4. **חכה לפיד אמיתי** – ECB rates ב-frankfurter (מודול 7) הם **לא** פיד
   trading. הם reference rates יומיים.
5. **שמור תיעוד** – כל עסקה, כל slippage. אחרי 30 יום אם ה-P&L האמיתי שלילי –
   עצור.
6. **אם אתה לא מבין לחלוטין** איך הולכת עסקה: spread, swap, leverage, margin
   call – אל תסחר.
"""
)

st.error(
    "⛔ **אינני יועץ פיננסי.** הכל בקורס הזה הוא חינוכי בלבד. "
    "לא מומלץ לפעול על בסיס שום דבר ממה שלמדת. "
    "אם אתה שוקל מסחר בכסף אמיתי – פנה ליועץ מורשה."
)

st.divider()

render_quiz(
    "module8",
    [
        {
            "q": "מהו leg risk?",
            "options": [
                "סיכון של פציעה בריצה",
                "הסיכון שאחד מ-3 ה-legs לא יבוצע ואתה תישאר חשוף",
                "סיכון שהברוקר יסגור עמך",
                "מס נוסף",
            ],
            "answer": 1,
            "explain": "Leg risk = חוסר היכולת לבצע את 3 ה-legs באטומיות. נשאר עם פוזיציה חלקית = סיכון מטבע ישיר.",
        },
        {
            "q": "אם הסתברות הצלחה p < 0.5 וריסק חיובי, מה הסיכוי לאבד את הכל בטווח ארוך?",
            "options": [
                "0%",
                "תלוי במזל",
                "מתקרב ל-100%",
                "תלוי בברוקר",
            ],
            "answer": 2,
            "explain": "תוצאה מתמטית של Gambler's Ruin. עם edge שלילי, ההפסד הסופי הוא ודאי בהינתן מספיק עסקאות.",
        },
        {
            "q": "מהו ה-'1% rule'?",
            "options": [
                "מקסימום 1% ספרד",
                "1% עמלה לעסקה",
                "לא לסכן יותר מ-1% מההון בעסקה בודדת",
                "1% מס",
            ],
            "answer": 2,
            "explain": "כלל בסיסי בניהול סיכונים: גודל הפסד מקסימלי בעסקה בודדת = 1% מההון. שורד 100 הפסדים רצופים.",
        },
        {
            "q": "מהי הסיבה לכך ש-execution לא יכול להיות אטומי בקמעונאי?",
            "options": [
                "חוקי SEC",
                "אין API",
                "כל leg נשלח בנפרד דרך UI/order, עם לטנסי בין השליחות",
                "Microsoft Windows מקרס",
            ],
            "answer": 2,
            "explain": "HFT שולח 3 legs במקביל מאותה מכונה לאותו LP. בקמעונאי כל leg הוא רוקוסט עצמאי עם לטנסי משלו.",
        },
        {
            "q": "מי מבטיח אותך אם הברוקר פושט רגל?",
            "options": [
                "תלוי במדינה ובסוג הברוקר – לא תמיד יש כיסוי",
                "תמיד יש כיסוי מלא",
                "המדינה משלמת",
                "אף אחד, לעולם",
            ],
            "answer": 0,
            "explain": "SIPC בארה\"ב (עד $500k), ICF באירופה (€20k), לא תמיד חל על פורקס OTC קמעונאי. בדוק לפני הפקדה.",
        },
    ],
)

page_end()
