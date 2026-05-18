from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import pandas as pd
import requests
import streamlit as st

from utils.page import bootstrap, page_end


bootstrap("מודול 7 – סורק מט\"ח חי")

st.markdown("## 7️⃣ מודול 7 – סורק מט\"ח חי (ECB Reference Rates)")
st.caption("פיד יומי חינמי מ-frankfurter.app (ECB) – הצגת ה-Implied Cross מול ה-Market Cross.")
st.divider()

st.warning(
    "⚠️ **חשוב להבין את משמעות הנתונים שלפניכם:**\n\n"
    "- המקור: **שערי ייחוס של הבנק המרכזי האירופי (ECB)** דרך frankfurter.app, חינמי וללא מפתח.\n"
    "- הנתונים **אינם Live Tradeable** – זהו ציטוט mid-price יומי של הבנק המרכזי האירופי.\n"
    "- כדי לסחור באמת היו צריכים feed מ-LP אמיתי (Bid/Ask, לטנסי בודדים של מילישניות, $$$).\n"
    "- **מטרת הסורק היא חינוכית בלבד:** להמחיש כיצד נראית הסטייה בין Implied ל-Market Cross.\n"
    "- אינני יועץ פיננסי. אין כאן המלצה. אין כאן הזדמנות מסחר שניתן לבצע."
)

st.divider()

TRIANGLES = {
    "EUR / USD / JPY": ("EUR", "USD", "JPY"),
    "EUR / GBP / USD": ("EUR", "GBP", "USD"),
    "GBP / USD / JPY": ("GBP", "USD", "JPY"),
    "AUD / USD / JPY": ("AUD", "USD", "JPY"),
    "USD / CHF / JPY": ("USD", "CHF", "JPY"),
    "EUR / USD / CHF": ("EUR", "USD", "CHF"),
}

st.markdown("### בחירת משולש מטבעות")
triangle_name = st.selectbox("Triangle", list(TRIANGLES.keys()), index=0)
a, b, c = TRIANGLES[triangle_name]

st.caption(f"המשולש הנבחר: **{a} / {b} / {c}**. נמשוך שלושה ציטוטים: {a}/{b}, {b}/{c}, {a}/{c}.")


@st.cache_data(ttl=300, show_spinner=False)
def fetch_rate(base: str, quote: str) -> Optional[dict]:
    """Returns {'rate': float, 'date': str} or {'error': str}."""
    url = f"https://api.frankfurter.app/latest?from={base}&to={quote}"
    try:
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        data = r.json()
        rate = data["rates"][quote]
        return {"rate": float(rate), "date": data.get("date", "")}
    except Exception as exc:
        return {"error": str(exc)}


fetch_button = st.button("🔄 משוך ציטוטים", type="primary", use_container_width=True)

if fetch_button or "fx_quotes" not in st.session_state:
    with st.spinner("מושך נתונים…"):
        st.session_state["fx_quotes"] = {
            "ab": fetch_rate(a, b),
            "bc": fetch_rate(b, c),
            "ac": fetch_rate(a, c),
            "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        }

quotes = st.session_state.get("fx_quotes", {})

errors = [v for v in (quotes.get("ab"), quotes.get("bc"), quotes.get("ac")) if v and v.get("error")]
if errors:
    st.error(
        "❌ שגיאה במשיכת הציטוטים: " + ", ".join(e["error"] for e in errors) +
        "\n\nייתכן ש-frankfurter.app אינו זמין באופן זמני. נסו שוב בעוד דקה."
    )
    page_end()
    st.stop()

if not all(quotes.get(k) and "rate" in quotes[k] for k in ("ab", "bc", "ac")):
    st.info("לחצו '🔄 משוך ציטוטים' כדי להתחיל.")
    page_end()
    st.stop()

rate_ab = quotes["ab"]["rate"]
rate_bc = quotes["bc"]["rate"]
rate_ac_market = quotes["ac"]["rate"]
fetched_at = quotes["fetched_at"]
data_date = quotes["ab"].get("date", "")

st.markdown("### 📊 ציטוטים שנמשכו")
df = pd.DataFrame(
    [
        {"זוג": f"{a}/{b}", "Mid (ECB)": rate_ab},
        {"זוג": f"{b}/{c}", "Mid (ECB)": rate_bc},
        {"זוג": f"{a}/{c}", "Mid (ECB) בשוק": rate_ac_market},
    ]
)
st.dataframe(df, hide_index=True, use_container_width=True)

st.caption(f"📅 תאריך הנתונים: **{data_date}** · נמשך אצלכם: {fetched_at}")

rate_ac_implied = rate_ab * rate_bc
deviation_abs = rate_ac_market - rate_ac_implied
deviation_bp = (deviation_abs / rate_ac_implied) * 10_000 if rate_ac_implied else 0
profit_factor = rate_ac_market / rate_ac_implied if rate_ac_implied else 0
profit_pct = (profit_factor - 1) * 100

st.markdown("### 🧮 חישוב ה-Implied Cross")

st.code(
    f"{a}/{c} implied = ({a}/{b}) × ({b}/{c}) = {rate_ab:.6f} × {rate_bc:.6f} = {rate_ac_implied:.6f}\n"
    f"{a}/{c} market  = {rate_ac_market:.6f}\n"
    f"סטייה          = {deviation_abs:+.6f}  ({deviation_bp:+.2f} bp)",
    language="text",
)

m1, m2, m3 = st.columns(3)
m1.metric(f"{a}/{c} Implied", f"{rate_ac_implied:.6f}")
m2.metric(f"{a}/{c} Market",  f"{rate_ac_market:.6f}", delta=f"{deviation_abs:+.6f}")
m3.metric("סטייה (bp)",       f"{deviation_bp:+.2f}",  delta=f"{profit_pct:+.4f}%")

st.markdown("### 🚦 פירוש התוצאה")

abs_bp = abs(deviation_bp)
if abs_bp < 0.5:
    st.success(
        f"⚖️ סטייה זניחה ({abs_bp:.2f} bp). ה-cross של {a}/{c} בשוק מתואם כמעט "
        "באופן מושלם עם החישוב משלושת הזוגות. כך זה אמור להיראות ברוב הזמן בשוק יעיל."
    )
elif abs_bp < 3:
    st.info(
        f"📐 סטייה קטנה ({abs_bp:.2f} bp). זה בגדר הרעש של ECB Reference Rates "
        "שמתעדכנים פעם ביום ובאיחור מסוים. לא הזדמנות אמיתית – פערים בני זיהוי "
        "מסוג זה חיים אצל LPs מיקרושניות בלבד."
    )
else:
    st.warning(
        f"📊 סטייה גדולה יחסית ({abs_bp:.2f} bp). זה כמעט תמיד מצביע על:\n"
        "- שערי ECB עבור שלושת הזוגות לא נמדדו באותה שנייה (חשוב לזכור: אלה Daily Reference).\n"
        "- אחד הזוגות נסחר בדינמיקה שונה (למשל JPY בשעות אסיה).\n\n"
        "**זו אינה 'הזדמנות ארביטראז' אמיתית' שניתן לבצע.**"
    )

st.divider()

st.markdown("### 🧠 מה ללמוד מהסורק")

st.markdown(
    """
1. **ה-Implied קרוב מאוד ל-Market בפועל.** רוב הזמן הסטייה היא כמה bp בלבד.
2. **כשמופיעה סטייה גדולה בשערי ECB, היא כמעט תמיד תוצאה של חוסר סנכרון** –
   לא הזדמנות.
3. **כדי לדעת אם באמת הייתה הזדמנות**, יש צורך ב:
   - feed **Real-Time** ברמת μs, לא יומי.
   - **Bid/Ask**, לא mid.
   - מנגנון שמבצע את שלושת הצעדים **בו זמנית** ללא slippage – ולבד זה
     בלתי אפשרי מטלפון.

הסורק כאן מציג את הצד התיאורטי. בעולם האמיתי, הפער בין מה שאתם רואים ב-mid
של ECB לבין מה שאתם באמת יכולים לסחור הוא **גדול יותר** מהפערית הפוטנציאלית.
"""
)

st.error(
    "⛔ **תזכורת קבועה:** אינני יועץ פיננסי. הנתונים בסורק הם **חינוכיים בלבד**. "
    "אין כאן המלצה לבצע פעולה כלשהי בכספכם."
)

st.divider()

st.markdown("### 🔗 קרדיט וטכניקה")
st.markdown(
    """
- **המקור**: [frankfurter.app](https://www.frankfurter.app) – שערי ייחוס של
  ה-ECB, חינמי, ללא צורך במפתח, ללא הגבלת קצב.
- **רענון**: בלחיצה על "משוך ציטוטים", עם cache של 5 דקות (כדי לא להעמיס על השרת).
- **API Endpoint**: `https://api.frankfurter.app/latest?from=EUR&to=USD`.
"""
)

page_end()
