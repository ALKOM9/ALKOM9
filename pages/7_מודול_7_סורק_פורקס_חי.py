from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import pandas as pd
import requests
import streamlit as st

from utils.page import bootstrap, page_end


bootstrap("מודול 7 – סורק פורקס חי")

st.markdown("## 7️⃣ מודול 7 – סורק פורקס חי (ECB reference rates)")
st.caption("פיד יומי חינמי מ-frankfurter.app (ECB) – הצגה של ה-implied cross מול ה-market cross.")
st.divider()

st.warning(
    "⚠️ **חשוב להבין מה זה הנתונים שלפניך:**\n\n"
    "- המקור הוא **ECB reference rates** דרך frankfurter.app, **חינמי וללא מפתח**.\n"
    "- הנתונים **לא live tradeable** – זה ציטוט mid-price יומי של הבנק המרכזי האירופי.\n"
    "- כדי לסחור באמת היית צריך פיד מ-LP אמיתי (bid/ask, סנטים בודדים של לטנסי, $$$).\n"
    "- **המטרה של הסורק הזה היא חינוכית בלבד:** להמחיש איך נראית הסטייה בין implied ל-market cross.\n"
    "- אינני יועץ פיננסי. אין כאן המלצה. אין כאן הזדמנות מסחר שאתה יכול לבצע."
)

st.divider()

# --- Triangle selector ---
TRIANGLES = {
    "EUR / USD / JPY": ("EUR", "USD", "JPY"),
    "EUR / GBP / USD": ("EUR", "GBP", "USD"),
    "GBP / USD / JPY": ("GBP", "USD", "JPY"),
    "AUD / USD / JPY": ("AUD", "USD", "JPY"),
    "USD / CHF / JPY": ("USD", "CHF", "JPY"),
    "EUR / USD / CHF": ("EUR", "USD", "CHF"),
}

st.markdown("### בחר משולש מטבעות")
triangle_name = st.selectbox("Triangle", list(TRIANGLES.keys()), index=0)
a, b, c = TRIANGLES[triangle_name]

st.caption(f"המשולש הנבחר: **{a} / {b} / {c}**. נקבל את 3 הציטוטים: {a}/{b}, {b}/{c}, {a}/{c}.")

# --- Fetch rates from frankfurter.app ---
@st.cache_data(ttl=300, show_spinner=False)
def fetch_rate(base: str, quote: str) -> Optional[dict]:
    """Returns {'rate': float, 'date': str} or None on error."""
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
    with st.spinner("מושך נתונים..."):
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
        "\n\nייתכן ש-frankfurter.app זמנית לא זמין. נסה שוב בעוד דקה."
    )
    page_end()
    st.stop()

if not all(quotes.get(k) and "rate" in quotes[k] for k in ("ab", "bc", "ac")):
    st.info("לחץ '🔄 משוך ציטוטים' כדי להתחיל.")
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
        {"זוג": f"{a}/{c}", "Mid (ECB) – בשוק": rate_ac_market},
    ]
)
st.dataframe(df, hide_index=True, use_container_width=True)

st.caption(f"📅 תאריך הנתונים: **{data_date}** · נמשך אצלך: {fetched_at}")

# --- Triangulation math ---
rate_ac_implied = rate_ab * rate_bc
deviation_abs = rate_ac_market - rate_ac_implied
deviation_bp = (deviation_abs / rate_ac_implied) * 10_000 if rate_ac_implied else 0
profit_factor = rate_ac_market / rate_ac_implied if rate_ac_implied else 0
profit_pct = (profit_factor - 1) * 100

st.markdown("### 🧮 חישוב ה-implied cross")

st.code(
    f"{a}/{c} implied = ({a}/{b}) × ({b}/{c}) = {rate_ab:.6f} × {rate_bc:.6f} = {rate_ac_implied:.6f}\n"
    f"{a}/{c} market  = {rate_ac_market:.6f}\n"
    f"סטייה          = {deviation_abs:+.6f}  ({deviation_bp:+.2f} bp)",
    language="text",
)

m1, m2, m3 = st.columns(3)
m1.metric(f"{a}/{c} Implied", f"{rate_ac_implied:.6f}")
m2.metric(f"{a}/{c} Market",  f"{rate_ac_market:.6f}", delta=f"{deviation_abs:+.6f}")
m3.metric("Deviation (bp)",   f"{deviation_bp:+.2f}",  delta=f"{profit_pct:+.4f}%")

# --- Interpretation ---
st.markdown("### 🚦 פירוש")

abs_bp = abs(deviation_bp)
if abs_bp < 0.5:
    st.success(
        f"⚖️ סטייה זניחה ({abs_bp:.2f} bp). ה-cross של {a}/{c} בשוק מתואם כמעט מושלם עם החישוב מתוך 3 הזוגות. "
        "ככה זה אמור להיראות ברוב הזמן בשוק יעיל."
    )
elif abs_bp < 3:
    st.info(
        f"📐 סטייה קטנה ({abs_bp:.2f} bp). זה בגדר הרעש של ECB reference rates שמתעדכנים פעם ביום ובאיחור. "
        "לא הזדמנות אמיתית – פערים בני-זיהוי כאלה חיים אצל LPs מיקרושניות בלבד."
    )
else:
    st.warning(
        f"📊 סטייה גדולה יחסית ({abs_bp:.2f} bp). זה כמעט תמיד מצביע על:\n"
        "- ECB rates עבור 3 הזוגות לא נמדדו באותה שנייה (יש לזכור: הם daily reference).\n"
        "- אחד הזוגות נסחר בדינמיקה שונה (למשל JPY בשעות אסיה).\n\n"
        "**זה לא 'הזדמנות ארביטראז' אמיתית' שאפשר לבצע.**"
    )

st.divider()

st.markdown("### 🧠 מה ללמוד מהסורק")

st.markdown(
    f"""
1. **ה-implied מאוד קרוב ל-market בפועל.** רוב הזמן הסטייה היא כמה bp בלבד.
2. **כשמופיעה סטייה גדולה ב-ECB reference rates, היא כמעט תמיד תוצר של desynchronization** —
   לא הזדמנות.
3. **כדי לדעת אם באמת הייתה הזדמנות**, היית צריך:
   - פיד **real-time** (μs-level), לא יומי.
   - **Bid/Ask**, לא mid.
   - מנגנון לבצע **3 הצעדים בו זמנית** בלי slippage – שזה לבד בלתי אפשרי מטלפון.

הסורק כאן מציג את הצד התיאורטי. בעולם האמיתי, הפער בין מה שאתה רואה ל-mid של ECB
לבין מה שאתה באמת יכול לסחור הוא **גדול יותר** מהפערית הפוטנציאלית.
"""
)

st.error(
    "⛔ **תזכורת קבועה:** אינני יועץ פיננסי. הנתונים בסורק הם **חינוכיים בלבד**. "
    "אין כאן המלצה לבצע פעולה כלשהי בכספך."
)

st.divider()

st.markdown("### 🔗 קרדיט וטכניקה")
st.markdown(
    """
- **המקור**: [frankfurter.app](https://www.frankfurter.app) – ECB reference rates, חינמי, בלי מפתח, בלי הגבלת קצב.
- **רענון**: בקליק "משוך ציטוטים", עם cache של 5 דקות (כדי לא להעמיס על השרת).
- **API endpoint**: `https://api.frankfurter.app/latest?from=EUR&to=USD`.
- **תיעוד מלא**: github.com/lmauertal/frankfurter.
"""
)

page_end()
