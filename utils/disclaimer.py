"""Persistent NOT-FINANCIAL-ADVICE disclaimers, shown on every page.

The owner of this course is NOT a licensed advisor. Nothing here is a
recommendation. These helpers are called from utils.page.bootstrap so
the disclaimers appear automatically on app.py and every page in pages/.
"""
from __future__ import annotations

import streamlit as st


_RIBBON_HTML = """
<div class="disclaimer-ribbon">
  <div class="he">
    ⚠️ <strong>אזהרה:</strong> אינני יועץ פיננסי או יועץ השקעות. אין כאן ייעוץ, אין כאן המלצה.
    התוכן <strong>חינוכי בלבד</strong>. כל פעולה בכספך – באחריותך הבלעדית.
  </div>
  <div class="en">
    ⚠️ <strong>Disclaimer:</strong> I am <strong>not</strong> a licensed financial or investment advisor.
    Nothing here is advice or a recommendation. Content is <strong>educational only</strong>.
    Any action you take with your money is your sole responsibility.
  </div>
</div>
"""

_FOOTER_HTML = """
<div class="disclaimer-footer">
  <div class="he">
    <strong>הבהרה משפטית.</strong> בעל הקורס אינו יועץ פיננסי, אינו יועץ השקעות, ואינו יועץ מס.
    כל המידע, המחשבונים, הסקריפטים והדוגמאות באתר הם <strong>למטרות לימוד והמחשה בלבד</strong>,
    אינם מהווים ייעוץ, אינם בגדר המלצה, ואינם מתחשבים במצבך הפיננסי האישי.
    מסחר בפורקס או ארביטראז' כרוך בסיכון משמעותי לאובדן הון – אולי כולו.
    ביצועי עבר אינם מבטיחים ביצועי עתיד. הסתמכות על תוכן כלשהו כאן היא באחריותך הבלעדית.
    מומלץ להתייעץ עם בעל רישיון מתאים לפני כל פעולה.
  </div>
  <div class="en">
    <strong>Legal notice.</strong> The course owner is not a licensed financial, investment,
    or tax advisor. All information, calculators, scripts, and examples are
    <strong>for educational and illustrative purposes only</strong>, are not advice,
    are not a recommendation, and do not take your personal financial situation into account.
    Trading FX or arbitrage carries substantial risk of loss — possibly all of it.
    Past performance does not guarantee future results. Any reliance on content here is at
    your sole risk. Consult a licensed professional before taking any action.
  </div>
</div>
"""

_SIDEBAR_HTML = """
<div class="sidebar-disclaimer">
  <div>⚠️ <strong>לא ייעוץ פיננסי.</strong> חינוכי בלבד. אינני יועץ מורשה ואין כאן המלצה.</div>
  <div class="en">⚠️ <strong>Not financial advice.</strong> Educational only. I am not a licensed advisor; nothing here is a recommendation.</div>
</div>
"""


def render_top_ribbon() -> None:
    st.markdown(_RIBBON_HTML, unsafe_allow_html=True)


def render_footer() -> None:
    st.markdown(_FOOTER_HTML, unsafe_allow_html=True)


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(_SIDEBAR_HTML, unsafe_allow_html=True)
