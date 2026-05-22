import streamlit as st


_SESSION_FLAG = "consent_ok"


_HE_TEXT = """
**אזהרה והסכמה – חובה לקרוא**

הקורס הזה נועד **למטרות לימוד בלבד**. הוא **אינו** ייעוץ פיננסי, ייעוץ השקעות, או ייעוץ מס.
מחברי הקורס אינם יועצים פיננסיים מורשים, ואין כאן המלצה לבצע פעולה כלשהי בכספך.

**Sector Rotation** היא אסטרטגיה אקטיבית של החלפת חשיפה בין סקטורים שונים של שוק המניות
לפי שלב המחזור הכלכלי. למרות שיש לה רקורד אקדמי ארוך, **היא לא ערובה לתשואה עודפת** מעל
מדד רחב. אסטרטגיות מבוססות מומנטום סובלות מ-drawdowns חדים סביב נקודות מפנה בשוק,
ויכולות להפסיד למדד שנים שלמות ברציפות. תוצאות backtest מציגות עבר – **ביצועי עבר אינם
מבטיחים ביצועי עתיד**.

הסיווג של שלב המחזור הכלכלי בקורס הזה מתבסס על מודל הוריסטי פשוט מעל נתוני FRED.
הוא **לא** משקף את עמדת ה-Federal Reserve, NBER, או כל גוף מקצועי אחר. אינדיקטורי מאקרו
מתעדכנים באיחור (לפעמים חודשים) ומתוקנים – הסיווג יכול להשתנות רטרואקטיבית.

כל המחשבונים, הגרפים, ההמלצות הסקטוריאליות, וה-backtests הם **ממחישים בלבד**, לא מותאמים
למצב הפיננסי שלך. בחירה לפעול על בסיס משהו שלמדת כאן – באחריותך הבלעדית. שקול להתייעץ
עם איש מקצוע מורשה לפני כל פעולה.

על ידי לחיצה על "אני מסכים", אתה מאשר:
- אני מעל גיל 18.
- אני מבין שהקורס חינוכי בלבד ולא ייעוץ.
- אני מקבל אחריות מלאה על כל החלטה פיננסית שאקבל.
- אני מבין שייתכן ואפסיד כסף, אולי את כולו.
"""

_EN_TEXT = """
**Disclaimer & Consent – please read**

This course is for **educational purposes only**. It is **not** financial advice, investment advice,
or tax advice. The authors are not licensed financial advisors, and nothing here is a recommendation
to take any action with your money.

**Sector Rotation** is an active strategy of shifting exposure between equity sectors based on the
stage of the business cycle. While it has a long academic track record, **it is not a guarantee of
excess return** over a broad benchmark. Momentum-based strategies suffer sharp drawdowns around
market turning points and may underperform the index for years in a row. Backtest results show the
past – **past performance does not guarantee future results**.

The business-cycle phase classification used in this course is based on a simple heuristic over FRED
data. It does **not** represent the official view of the Federal Reserve, NBER, or any other
professional body. Macro indicators are released with lag (sometimes months) and revised – the
classification can change retroactively.

All calculators, charts, sector recommendations, and backtests are **illustrative only**, not
tailored to your financial situation. Acting on anything you learn here is **your sole
responsibility**. Consult a licensed professional before taking action.

By clicking "I Agree", you confirm:
- I am at least 18 years old.
- I understand the course is educational, not advice.
- I take full responsibility for any financial decision I make.
- I understand I may lose money, possibly all of it.
"""


def require_consent() -> bool:
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
