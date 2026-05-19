"""Triangular Arbitrage Course – Home / entry point.

Streamlit Cloud points to this file. It handles:
    1. Page config + RTL/mobile styling
    2. Password gate (st.secrets["password"])
    3. Bilingual consent gate
    4. Welcome screen with module overview

Modules live in pages/ as a native Streamlit multipage app.
"""
from utils.page import bootstrap, page_end
import streamlit as st


bootstrap("קורס Triangular Arbitrage")

st.title("🔺 קורס Triangular Arbitrage – מט\"ח")
st.caption("קורס אינטראקטיבי בעברית על ארביטראז' משולש בשוק המט\"ח – 8 מודולים, מחשבונים, חידונים וסורק חי.")

st.markdown(
    """
ברוכים הבאים. כדי להתחיל, פתחו את התפריט הצדדי (☰ למעלה משמאל בטלפון) ובחרו מודול.

אם זו הפעם הראשונה – התחילו ב**מודול 1** והמשיכו לפי הסדר.

**הקורס עוסק אך ורק בשוק המט"ח (Forex). אין כאן תוכן על קריפטו.**
"""
)

st.divider()

st.markdown("### 📚 מבנה הקורס")

modules = [
    ("1️⃣", "יסודות מט\"ח",              "שערי חליפין, Bid ו-Ask, איך מצטטים זוגות מטבעות, שעות מסחר."),
    ("2️⃣", "המתמטיקה",                  "Implied Cross Rate – הנוסחה המרכזית של ארביטראז' משולש."),
    ("3️⃣", "זיהוי הזדמנות",             "ספרד אחרי עמלות, Slippage, ניתוח Bid/Ask לכל leg."),
    ("4️⃣", "נגד HFT",                   "למה הזדמנויות נסגרות תוך מיקרושניות: Colocation, Latency, Last-Look."),
    ("5️⃣", "פינות חיות",                "זוגות אקזוטיים, שעות שקטות, רגעי חדשות וסוף שבוע."),
    ("6️⃣", "ברוקרים ועמלות",            "Market Maker / STP / ECN, Spread, Commission, Swap – העלות האמיתית."),
    ("7️⃣", "סורק מט\"ח חי",              "פיד יומי חינמי מ-ECB דרך frankfurter.app, חישוב Implied מול Market."),
    ("8️⃣", "ניהול סיכונים",             "Execution, Latency, Broker, Counterparty Risk, ומחשבון Risk of Ruin."),
    ("9️⃣", "מציאת עסקאות במהירות",     "שני נתיבים: ידני (workflow אופטימלי) ואוטומטי (ארכיטקטורה, latency, קוד Python)."),
    ("🔎",  "כלי איתור ברוקרים",         "רגולטורים, ברוקרים מפוקחים לפי מדינה, צ'קליסט בדיקה ודגלים אדומים."),
]

for emoji, title, desc in modules:
    st.markdown(f"**{emoji} {title}** – {desc}")

st.divider()

st.info(
    "💡 **טיפ:** בטלפון, התפריט הצדדי נסגר אוטומטית אחרי בחירת מודול. "
    "כדי לפתוח אותו שוב, לחצו על ה-☰ בפינה השמאלית למעלה."
)

with st.expander("🔒 פרטיות וגישה"):
    st.markdown(
        """
- הסיסמה מאוחסנת ב-**Streamlit Secrets**, לא בקוד.
- הקוד עצמו ציבורי – אבל הסיסמה אינה בקוד, היא נשמרת בנפרד ב-Streamlit.
- אין שמירת נתוני משתמשים, אין עוגיות (cookies) ארוכות טווח, אין מעקב.
- כדי להחליף סיסמה: Streamlit Cloud → Settings → Secrets.
"""
    )

with st.expander("❓ עזרה ופתרון בעיות"):
    st.markdown(
        """
- האפליקציה איטית בכניסה? היא נרדמת אחרי כמה ימי חוסר שימוש – לחצו "Yes, wake it up" וחכו כ-30 שניות.
- שיניתם את הסיסמה והמערכת לא מקבלת? בצעו **Reboot** לאפליקציה אחרי שמירה ב-Secrets.
- בעיה אחרת? צלמו מסך ושלחו לי (Claude) – אתקן.
"""
    )

page_end()
