import streamlit as st


_SESSION_FLAG = "consent_ok"


_HE_TEXT = """
**אזהרה והסכמה – חובה לקרוא**

הקורס נועד **למטרות לימוד בלבד**. הוא **אינו** ייעוץ פיננסי, ייעוץ השקעות, או ייעוץ מס.
מחברי הקורס אינם יועצים פיננסיים מורשים, ואין כאן המלצה לבצע פעולה כלשהי בכספכם.

מסחר בארביטראז' משולש בשוק המט"ח (Forex), כמו כל מסחר במטבעות, כרוך ב**סיכון משמעותי לאובדן הון**,
ולעיתים אף בהפסד הגדול מהסכום שהושקע. השוק מורכב ברובו ממשתתפים מקצועיים בעלי תשתיות HFT,
Colocation ולטנסי מתחת למילישנייה. הזדמנויות אמיתיות נסגרות תוך מיקרושניות, ולקמעונאי כמעט
בלתי אפשרי לזכות בהן באופן עקבי.

ביצועי עבר **אינם** מבטיחים ביצועי עתיד. כל המחשבונים, הסקריפטים והדוגמאות בקורס הם
**להמחשה בלבד**, ואינם מותאמים למצב הפיננסי שלכם. כל פעולה שתבחרו לבצע על בסיס תוכן הקורס –
היא באחריותכם הבלעדית. מומלץ להתייעץ עם איש מקצוע מורשה לפני כל פעולה.

לחיצה על "אני מסכים" מהווה אישור לכך ש:
- אני מעל גיל 18.
- אני מבין שהקורס חינוכי בלבד ואינו ייעוץ.
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
        "✅ קראתי, הבנתי ואני מסכים  /  I have read, understood, and I agree.",
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
