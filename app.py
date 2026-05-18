"""Triangular Arbitrage Course – Home / entry point.

Streamlit Cloud points to this file. It handles:
    1. Page config + RTL/mobile styling
    2. Password gate (st.secrets["password"])
    3. Bilingual consent gate
    4. Welcome screen with module overview

Modules live in pages/ as a native Streamlit multipage app.
"""
from utils.page import bootstrap
import streamlit as st


bootstrap("קורס Triangular Arbitrage")

st.title("🔺 קורס Triangular Arbitrage")
st.caption("קורס אינטראקטיבי בעברית – 8 מודולים, מחשבונים, חידונים, סורק חי.")

st.markdown(
    """
ברוך הבא. פתח את התפריט הצדדי (☰ למעלה משמאל בטלפון) ובחר מודול להתחיל בו.

אם זו פעם ראשונה – התחל ב**מודול 1**, וקרא לפי הסדר.
"""
)

st.divider()

st.markdown("### 📚 מבנה הקורס")

modules = [
    ("1️⃣", "יסודות פורקס",            "Cross rates, bid/ask, איך מצטטים זוגות, שעות מסחר."),
    ("2️⃣", "המתמטיקה",                 "Implied cross rate, הנוסחה המרכזית של ארביטראז' משולש."),
    ("3️⃣", "זיהוי הזדמנות",            "ספרד אחרי עמלות, slippage, ניתוח bid/ask."),
    ("4️⃣", "נגד HFT",                  "מדוע הזדמנויות נסגרות במיקרושניות, colocation, latency."),
    ("5️⃣", "פינות חיות",               "זוגות אקזוטיים, שעות חפיפה בין שווקים."),
    ("6️⃣", "Crypto Triangular",        "BTC/USDT × ETH/BTC × ETH/USDT – ארביטראז' בקריפטו."),
    ("7️⃣", "סורק חי",                  "סקריפט Binance Public API שמתריע על סטיות."),
    ("8️⃣", "ניהול סיכונים",            "Execution risk, latency risk, exchange risk."),
]

for emoji, title, desc in modules:
    st.markdown(f"**{emoji} {title}** – {desc}")

st.divider()

st.info(
    "💡 **טיפ:** בטלפון, התפריט נסגר אוטומטית אחרי בחירה. "
    "כדי לפתוח אותו שוב לחץ על ה-☰ בפינה השמאלית למעלה."
)

with st.expander("🔒 פרטיות וגישה"):
    st.markdown(
        """
- הסיסמה מאוחסנת ב-**Streamlit Secrets**, לא בקוד.
- ה-repo ב-GitHub שלך **פרטי** – אף אחד לא רואה את הקוד.
- אין שמירת נתונים, אין קוקיז ארוכי טווח, אין מעקב.
- כדי להחליף סיסמה: Streamlit Cloud → Settings → Secrets.
"""
    )

with st.expander("❓ עזרה ופתרון בעיות"):
    st.markdown(
        """
- האפליקציה איטית בכניסה? היא נרדמת אחרי כמה ימי חוסר שימוש – לחץ "Yes, wake it up" וחכה 30 שניות.
- שינית סיסמה אבל המערכת לא מקבלת? עשה **Reboot** לאפליקציה אחרי שמירה ב-Secrets.
- בעיה אחרת? צלם מסך ושלח לי (Claude) – אתקן.
"""
    )
