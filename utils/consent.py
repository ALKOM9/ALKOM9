import streamlit as st


_SESSION_FLAG = "consent_ok"


_HE_TEXT = """
**אזהרה והסכמה – חובה לקרוא**

הקורס הזה נועד **למטרות לימוד בלבד**. הוא **אינו** ייעוץ פיננסי, ייעוץ השקעות, או ייעוץ מס.
מחברי הקורס אינם יועצים פיננסיים מורשים, ואין כאן המלצה לבצע פעולה כלשהי בכספך.

מסחר ב-Triangular Arbitrage בשוק המט"ח (פורקס) – כמו כל מסחר במטבעות – כרוך ב**סיכון משמעותי לאובדן הון**,
כולל הפסד מעל הסכום שהושקע. השוק מאוכלס במשתתפים מקצועיים עם תשתיות HFT, קולוקיישן,
ולטנסי מתחת למילישנייה – הזדמנויות אמיתיות נסגרות במיקרושניות, ולקמעונאי כמעט בלתי אפשרי לזכות בהן.

ביצועי עבר **אינם** מבטיחים ביצועי עתיד. כל מחשבוני הקורס, הסקריפטים, והדוגמאות הם
**ממחישים בלבד**, ולא מותאמים למצב הפיננסי שלך. בחירה לפעול על בסיס משהו שלמדת כאן –
היא באחריותך הבלעדית. שקול להתייעץ עם איש מקצוע מורשה לפני כל פעולה.

על ידי לחיצה על "אני מסכים", אתה מאשר:
- אני מעל גיל 18.
- אני מבין שהקורס הוא חינוכי בלבד ולא ייעוץ.
- אני מקבל אחריות מלאה על כל החלטה פיננסית שאקבל.
- אני מבין שייתכן ואפסיד כסף, אולי את כולו.
"""

_EN_TEXT = """
**Disclaimer & Consent – please read**

This course is for **educational purposes only**. It is **not** financial advice, investment advice,
or tax advice. The authors are not licensed financial advisors, and nothing here is a
recommendation to take any action with your money.

Trading Triangular Arbitrage in the FX (forex) market – like any currency trading – carries **substantial risk of loss**,
potentially exceeding the amount invested. The market is dominated by professional participants with
HFT infrastructure, colocation, and sub-millisecond latency. Real opportunities close within
microseconds, and it is nearly impossible for a retail trader to win them consistently.

Past performance does **not** guarantee future results. All calculators, scripts, and examples in
this course are **illustrative only**, not tailored to your financial situation. Acting on anything
you learn here is **your sole responsibility**. Consult a licensed professional before taking action.

By clicking "I Agree", you confirm:
- I am at least 18 years old.
- I understand the course is educational, not advice.
- I take full responsibility for any financial decision I make.
- I understand I may lose money, possibly all of it.
"""


def require_consent() -> bool:
    """Render the bilingual consent gate. Stops the script if not accepted."""
    if st.session_state.get(_SESSION_FLAG):
        return True

    st.markdown("## ⚠️ הסכמה / Consent")
    st.markdown("<div class='consent-card'>" + _HE_TEXT + "</div>", unsafe_allow_html=True)
    st.markdown("<div class='consent-card en'>" + _EN_TEXT + "</div>", unsafe_allow_html=True)

    agree = st.checkbox(
        "✅ אני קראתי, הבנתי, ואני מסכים  /  I have read, understood, and I agree.",
        key="consent_checkbox",
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("אני מסכים / I Agree", use_container_width=True, type="primary"):
            if agree:
                st.session_state[_SESSION_FLAG] = True
                st.rerun()
            else:
                st.warning("יש לסמן את התיבה לפני אישור. / Please tick the box first.")
    with col2:
        if st.button("יציאה / Exit", use_container_width=True):
            st.session_state.clear()
            st.stop()

    st.stop()
    return False
