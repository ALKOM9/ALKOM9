from utils.page import bootstrap, page_end
from utils.quiz import render_quiz
import streamlit as st

bootstrap("מודול 6 – ברוקרים ועמלות")

st.markdown("## 6️⃣ מודול 6 – ברוקרים, ספרדים ועלויות אמיתיות")
st.caption("Market Maker / STP / ECN, spread קבוע מול משתנה, commission, swap, ועלות אמיתית של עסקה.")
st.divider()

st.markdown(
    """
### למה הברוקר מרוויח עליך גם כשלא הרווחת

ברוקר פורקס לא עובד בחינם. הוא מרוויח על:
1. **Spread** (תמיד) – ההפרש בין Bid ל-Ask.
2. **Commission** – עמלה קבועה לכל $100,000 שנסחרים, אצל חלק מהמודלים.
3. **Swap (rollover)** – הפרשי ריבית בין שני המטבעות, אם החזקת לילה.
4. **Slippage A-symmetric** – הברוקר לוקח את הצד "הטוב" של ה-fill (ראינו במודול 4).
5. **Marketing kickback** מ-LPs (אצל חלק).

הבחירה של מודל הברוקר משפיעה ישירות על העלות שלך, **ובארביטראז' זה קריטי**.
"""
)

st.divider()

st.markdown("### 🏷️ 3 סוגי ברוקרים")

st.markdown("**1. Market Maker (DD – Dealing Desk)**")
st.markdown(
    """
- הוא ה-counterparty שלך. כשאתה קונה, הוא מוכר לך *מתוך המלאי שלו*.
- ספרד בדרך כלל **קבוע** (1–3 pips ב-EUR/USD).
- בלי commission ישירה.
- **קונפליקט אינטרסים:** כשאתה מרוויח, הברוקר מפסיד. ויש לו כלים להאט סדרים,
  להוסיף slippage, או לדחות בעת תנודתיות.
- דוגמאות: רוב הברוקרים הקמעונאיים הגדולים, חלק מהפלטפורמות הישראליות.
"""
)

st.markdown("**2. STP (Straight Through Processing)**")
st.markdown(
    """
- מעביר את ההזמנה ישירות ל-LP חיצוני (בנק / ספק נזילות).
- ספרד **משתנה**, בדרך כלל 0.8–2 pips ב-EUR/USD.
- ייתכנו commissions קטנות (~$3–$7 לכל $100k).
- פחות קונפליקט אינטרסים (הוא מרוויח על הספרד שלו, לא מההפסד שלך).
- דוגמאות: ברוקרים אירופאיים בינוניים.
"""
)

st.markdown("**3. ECN (Electronic Communications Network)**")
st.markdown(
    """
- אגרגציה של ספקי נזילות מרובים – אתה רואה את ה-orderbook האמיתי.
- ספרד הכי **צר** (0.0–0.5 pips ב-EUR/USD בשעות שיא).
- **commission תמיד** – ~$5–$10 לכל $100k (round-turn).
- הכי קרוב לתנאי המסחר של המוסדיים.
- מתאים יותר לנפחים גבוהים.
- דוגמאות: ברוקרי ECN בריטיים / אוסטרליים.
"""
)

st.info(
    "💡 **לארביטראז' תיאורטי, ECN הוא הבחירה היחידה.** Market Maker עם ספרד 1.5 pip × 3 legs = ~4.5 pips ספרד מצטבר. "
    "ECN עם ספרד 0.3 pip + commission = ~1.5 pips מצטבר. ההפרש = כל הפערית הפוטנציאלית בעולם."
)

st.divider()

st.markdown("### 💰 Swap / Rollover")

st.markdown(
    """
**Swap** = הפרשי הריבית בין שני המטבעות בזוג, שמשולמים/נגבים כל יום בשעה 22:00 NY
על פוזיציות שמוחזקות overnight.

דוגמה (USD/JPY ב-2025): ריבית USD ~5%, ריבית JPY ~0.5%.
- אם long USD/JPY (יש לך USD, חייב JPY) → **מקבל** ~4.5% / 365 ביום.
- אם short USD/JPY (יש לך JPY, חייב USD) → **משלם** ~4.5% / 365 ביום.

**בארביטראז' משולש שנמשך פחות משנייה swap לא רלוונטי.** הוא הופך לבעיה אם
הברוקר תקוע, הסדר נשאר פתוח לילה, או שאחד מ-3 ה-legs לא נסגר.
"""
)

st.divider()

st.markdown("### 🧮 מחשבון עלויות מלא")

st.caption("הזן את פרמטרי הברוקר שלך לכל leg. המחשבון יציג עלות מצטברת ויאמר לך אם הפערית התיאורטית עוברת את הסף.")

col_b1, col_b2 = st.columns(2)
with col_b1:
    notional = st.number_input("גודל עסקה ($ לכל leg)", min_value=1000.0, value=100_000.0, step=1000.0)
    spread_per_leg = st.number_input("ספרד ממוצע (pips, לכל leg)", min_value=0.0, value=0.8, step=0.1)
with col_b2:
    commission_per_100k = st.number_input("Commission ($ לכל $100k, round-turn)", min_value=0.0, value=7.0, step=0.5)
    slippage_per_leg = st.number_input("Slippage צפוי (pips, לכל leg)", min_value=0.0, value=0.3, step=0.1)

theoretical_edge_bp = st.slider(
    "פערית תיאורטית (basis points)",
    min_value=0.0, max_value=20.0, value=4.0, step=0.1,
)

# Costs (in basis points). 1 pip on EUR/USD ≈ 0.92 bp. We'll approximate 1 pip ≈ 1 bp for simplicity.
# Spread cost: half-spread per leg × 3 legs = 1.5 × spread total in pips
spread_cost_bp = 1.5 * spread_per_leg
slippage_cost_bp = 3 * slippage_per_leg
# Commission: per 100k round-turn × 3 legs, expressed as bp of notional
commission_bp = (commission_per_100k * 3) / (notional / 100_000 * notional) * 10_000 if notional else 0
# Simplify: commission per leg as bp = (commission / notional) * 10000, ×3 legs
commission_bp = ((commission_per_100k) / 100_000 * 10_000) * 3

total_cost_bp = spread_cost_bp + slippage_cost_bp + commission_bp
net_bp = theoretical_edge_bp - total_cost_bp

st.markdown("#### פירוט עלויות")
st.table(
    [
        {"רכיב": "ספרד (3 legs × 0.5)", "עלות (bp)": f"{spread_cost_bp:.2f}"},
        {"רכיב": "Slippage (3 legs)",   "עלות (bp)": f"{slippage_cost_bp:.2f}"},
        {"רכיב": "Commission (3 legs)", "עלות (bp)": f"{commission_bp:.2f}"},
        {"רכיב": "סה\"כ עלויות",         "עלות (bp)": f"{total_cost_bp:.2f}"},
    ]
)

st.markdown(f"#### תוצאה: **{net_bp:+.2f} bp נטו** (= {net_bp / 100:+.4f}%)")

if net_bp > 0.5:
    st.success(f"✅ הפערית מספיקה. רווח תיאורטי {net_bp:.2f} bp = {net_bp * notional / 10_000:.2f}$ לעסקה של {notional:,.0f}$.")
elif net_bp > -0.5:
    st.warning("⚠️ הפערית כמעט נאכלת בעלויות. רווח/הפסד גבולי – לא שווה את הסיכון.")
else:
    st.error(f"❌ העלויות גדולות מהפערית ב-{-net_bp:.2f} bp. הפסד ודאי.")

st.caption("💡 שיט את ה-slider של 'פערית תיאורטית' למעלה כדי לראות כמה גדולה הפערית צריכה להיות כדי שהעסקה תהיה רווחית.")

st.divider()

st.markdown("### ⚠️ עלויות נסתרות שלא הוזכרו")

st.markdown(
    """
- **Withdrawal fees** – חלק מהברוקרים גובים $25–$50 על כל משיכה. אם אתה רץ
  3,000 עסקאות זה לא משמעותי. אם אתה משך פעמיים בחודש – שווה לבדוק.
- **Inactivity fees** – $10–$30 לחודש אם אין פעילות. רלוונטי אם הפסקת באמצע.
- **Currency conversion** – אם החשבון בש"ח וה-LPs במט"ח, יש המרה. עלות 0.3–1%.
- **Tax** – רווח הון, ~25%. לא הברוקר גובה, אבל זה משפיע על P&L האמיתי שלך.
"""
)

st.divider()

render_quiz(
    "module6",
    [
        {
            "q": "באיזה סוג ברוקר הספרד הכי צר אבל יש commission?",
            "options": ["Market Maker", "STP", "ECN", "P2P"],
            "answer": 2,
            "explain": "ECN = orderbook אמיתי, ספרד מינימלי, commission קבוע. STP מינימלי או חינם. MM ספרד רחב אבל בלי commission.",
        },
        {
            "q": "במצב ארביטראז' שנמשך פחות משנייה, האם swap רלוונטי?",
            "options": [
                "כן, תמיד",
                "לא – משולם רק על overnight",
                "תלוי בזוג",
                "רק בסופ\"ש",
            ],
            "answer": 1,
            "explain": "Swap נקבע ב-22:00 NY על פוזיציות פתוחות. עסקה תוך-יומית קצרה לא משלמת swap.",
        },
        {
            "q": "Market Maker יש לו קונפליקט אינטרסים?",
            "options": [
                "אין שום קונפליקט",
                "כן – הוא ה-counterparty שלך, ומפסיד כשאתה מרוויח",
                "רק בזוגות exotic",
                "רק כשהבורסה סגורה",
            ],
            "answer": 1,
            "explain": "MM הוא הצד השני של העסקה שלך. כשמרוויח, הוא מפסיד — ויש לו כלים (slippage, requote) להגן על עצמו.",
        },
        {
            "q": "ב-3 legs עם spread 0.8 pip, מה הספרד המצטבר (חצי ספרד × 3)?",
            "options": [
                "0.8 pip",
                "1.2 pip",
                "2.4 pip",
                "4.8 pip",
            ],
            "answer": 1,
            "explain": "ספרד אפקטיבי לכל leg = חצי הספרד = 0.4. 3 legs × 0.4 = 1.2 pip ספרד מצטבר (~1.1 bp ב-EUR/USD).",
        },
        {
            "q": "מהו רכיב העלות שלא ראינו במחשבון אבל יכול לחתוך לרווחיות?",
            "options": [
                "המתח של הברוקר",
                "Withdrawal / inactivity fees",
                "WiFi של הבית",
                "התלוש של עובד הסניף",
            ],
            "answer": 1,
            "explain": "Withdrawal fees, inactivity fees, ו-currency conversion – פחות בולטות בעסקה בודדת, אבל מצטברות אם מסחרים בנפחים גבוהים.",
        },
    ],
)

page_end()
