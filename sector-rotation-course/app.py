"""Sector Rotation Course – Home / entry point.

Streamlit Cloud points to this file. It handles:
    1. Page config + RTL/mobile styling
    2. Password gate (st.secrets["password"])
    3. Bilingual consent gate
    4. Welcome screen with module overview

Modules live in pages/ as a native Streamlit multipage app.
"""
from utils.page import bootstrap
import streamlit as st


bootstrap("קורס Sector Rotation")

st.title("🔄 קורס Sector Rotation")
st.caption("קורס אינטראקטיבי בעברית – 8 מודולים, Dashboard חי, RRG, backtest 20 שנה.")

st.markdown(
    """
ברוך הבא. פתח את התפריט הצדדי (☰ למעלה משמאל בטלפון) ובחר מודול להתחיל בו.

אם זו פעם ראשונה – התחל ב**מודול 1**, וקרא לפי הסדר. הכלים החיים (Dashboard, RRG, Backtest)
ב-4, 5, ו-7 נשענים על מה שתלמד במודולים 1–3.
"""
)

st.divider()

st.markdown("### 📚 מבנה הקורס")

modules = [
    ("1️⃣", "Business Cycle",        "ארבעת שלבי המחזור: התאוששות, אמצע, סוף, מיתון. עקומת תשואות, PMI, LEI."),
    ("2️⃣", "מיפוי סקטורים",          "11 ה-SPDR ETFs: XLK, XLF, XLE, XLV וכל השאר. מה כל אחד מייצג."),
    ("3️⃣", "הסיבוב הקלאסי",          "איזה סקטור עובד בכל שלב, ולמה. הכלל של Sam Stovall."),
    ("4️⃣", "Macro Dashboard חי",     "8 אינדיקטורים מ-FRED, סיווג אוטומטי של שלב המחזור היום."),
    ("5️⃣", "Relative Strength + RRG", "כוח יחסי, JdK RS-Ratio, JdK RS-Momentum. גרף RRG אינטראקטיבי."),
    ("6️⃣", "יישום",                 "Overweight, long-short, momentum: 3 דרכים לסחור את הרעיון."),
    ("7️⃣", "Backtest 20 שנה",        "Top-3 sectors momentum: Sharpe, drawdown, hit rate, אחזקות לפי תקופה."),
    ("8️⃣", "שילוב בתיק",            "כמה משקל לתת לסיבוב? איך משלבים עם core/satellite?"),
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
- ה-FRED API key רק בקריאות שרת→FRED, לא חשוף לדפדפן.
- אין שמירת נתונים, אין קוקיז ארוכי טווח, אין מעקב.
- כדי להחליף סיסמה: Streamlit Cloud → Settings → Secrets.
"""
    )

with st.expander("❓ עזרה ופתרון בעיות"):
    st.markdown(
        """
- האפליקציה איטית בכניסה? היא נרדמת אחרי כמה ימי חוסר שימוש – לחץ "Yes, wake it up" וחכה 30 שניות.
- מודול 4 לא מציג נתונים? בדוק שיש `fred_api_key` ב-Streamlit Secrets. ראה `FRED_API_QUICK.md`.
- שינית סיסמה אבל המערכת לא מקבלת? עשה **Reboot** לאפליקציה אחרי שמירה ב-Secrets.
- בעיה אחרת? צלם מסך ושלח לי (Claude) – אתקן.
"""
    )
