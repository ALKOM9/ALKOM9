"""Module 4 - Live Macro Dashboard (FRED).

The heart of the course: pulls ~8 indicators from FRED, computes derived
features, classifies the current business-cycle phase, and shows sector
tilts. Everything is cached for 6 hours, so the only real cost is the very
first hit per day.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.page import bootstrap
from utils.style import page_header
from utils.fred import SERIES_INFO, get_many, latest_value
from utils.cycle import detect_phase, PHASE_LABELS_HE, phase_to_sectors
from utils.market import SECTORS
from utils.quiz import render_quiz


bootstrap("מודול 4 – Macro Dashboard")
page_header("📊 מודול 4 – Macro Dashboard חי", "8 אינדיקטורים מ-FRED + סיווג אוטומטי של שלב המחזור")

st.markdown(
    """
זה הלב של הקורס. כל הנתונים נשלפים בזמן אמת מ-**FRED** (Federal Reserve Economic Data) – מאגר
פתוח של הפד של St. Louis. הסיווג של שלב המחזור מתבסס על המודל ההוריסטי שלמדת במודולים 1–3:
מרווח עקום התשואות, מצב שוק העבודה, אינפלציה, ייצור תעשייתי, ועוד.

> ⚠️ זוהי הערכה הוריסטית, **לא** ההגדרה הרשמית של NBER (אותה מקבלים רק רטרואקטיבית, חודשים אחרי שמיתון התחיל). השתמש בזה כאחד הקלטים, לא כפסק דין.
"""
)

# ---------------------------- DATA FETCH ----------------------------

INDICATORS = [
    "T10Y2Y",
    "UNRATE",
    "ICSA",
    "CPIAUCSL",
    "INDPRO",
    "BAMLH0A0HYM2",
    "FEDFUNDS",
    "UMCSENT",
]

try:
    with st.spinner("שולף נתונים מ-FRED... (כניסה ראשונה ביום ~10 שניות, אחריה מ-cache)"):
        series_data = get_many(INDICATORS, start="2000-01-01")
except RuntimeError as e:
    st.error(f"⚠️ {e}")
    st.info(
        "אין מפתח FRED מוגדר. ראה את הקובץ `FRED_API_QUICK.md` בריפו להוראות הרשמה בחינם (2 דקות)."
    )
    st.stop()


# ---------------------------- DERIVED FEATURES ----------------------------

def _value_at_offset(df: pd.DataFrame, months: int) -> float:
    if df.empty:
        return float("nan")
    s = df["value"].dropna()
    if s.empty:
        return float("nan")
    target = s.index[-1] - pd.DateOffset(months=months)
    past = s.loc[s.index <= target]
    if past.empty:
        return float("nan")
    return float(past.iloc[-1])


def _pct_yoy(df: pd.DataFrame) -> float:
    if df.empty:
        return float("nan")
    s = df["value"].dropna()
    if s.empty:
        return float("nan")
    target = s.index[-1] - pd.DateOffset(years=1)
    past = s.loc[s.index <= target]
    if past.empty:
        return float("nan")
    return float((s.iloc[-1] / past.iloc[-1] - 1.0) * 100.0)


unrate_now = latest_value(series_data["UNRATE"])[1]
unrate_3m = _value_at_offset(series_data["UNRATE"], 3)
ff_now = latest_value(series_data["FEDFUNDS"])[1]
ff_6m = _value_at_offset(series_data["FEDFUNDS"], 6)

indicator_inputs = {
    "T10Y2Y": latest_value(series_data["T10Y2Y"])[1],
    "UNRATE": unrate_now,
    "UNRATE_3m_chg": unrate_now - unrate_3m if pd.notna(unrate_3m) else None,
    "ICSA_yoy": _pct_yoy(series_data["ICSA"]),
    "CPIAUCSL_yoy": _pct_yoy(series_data["CPIAUCSL"]),
    "INDPRO_yoy": _pct_yoy(series_data["INDPRO"]),
    "BAMLH0A0HYM2": latest_value(series_data["BAMLH0A0HYM2"])[1],
    "FEDFUNDS_6m_chg": ff_now - ff_6m if pd.notna(ff_6m) else None,
    "UMCSENT_yoy": _pct_yoy(series_data["UMCSENT"]),
}


# ---------------------------- PHASE CLASSIFICATION ----------------------------

phase, score, all_scores = detect_phase(indicator_inputs)
phase_label = PHASE_LABELS_HE.get(phase, phase)

st.markdown("### 🎯 שלב המחזור – הסיווג של המודל")

col_phase, col_score = st.columns([2, 1])
with col_phase:
    st.markdown(
        f"<div style='background:#1c1f26;border:2px solid #1f77b4;border-radius:14px;"
        f"padding:1rem 1.2rem;font-size:1.4rem;font-weight:700;text-align:center;'>"
        f"{phase_label}</div>",
        unsafe_allow_html=True,
    )
with col_score:
    st.metric("רמת ביטחון", f"{score * 100:.0f}%")

# Bar chart of all phase scores
score_df = pd.DataFrame(
    {
        "phase": [PHASE_LABELS_HE[p] for p in ["early", "mid", "late", "recession"]],
        "score": [all_scores.get(p, 0) for p in ["early", "mid", "late", "recession"]],
    }
)
fig_scores = go.Figure(
    go.Bar(
        x=score_df["score"],
        y=score_df["phase"],
        orientation="h",
        marker_color=["#2ecc71", "#3498db", "#f39c12", "#e74c3c"],
        text=[f"{s*100:.0f}%" for s in score_df["score"]],
        textposition="inside",
    )
)
fig_scores.update_layout(
    height=240,
    margin=dict(l=10, r=10, t=20, b=10),
    xaxis=dict(range=[0, 1], tickformat=".0%", showgrid=False),
    yaxis=dict(autorange="reversed"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    showlegend=False,
)
st.plotly_chart(fig_scores, use_container_width=True, config={"displayModeBar": False})


# ---------------------------- SECTOR RECOMMENDATIONS ----------------------------

st.markdown("### 🧭 הטיות סקטוריאליות לפי השלב")

tilts = phase_to_sectors(phase)
ow, uw = tilts["overweight"], tilts["underweight"]

if not ow and not uw:
    st.info("השלב 'לא ודאי' – אין המלצה ברורה. שב במדד רחב, חכה לסיגנל יותר חזק.")
else:
    col_ow, col_uw = st.columns(2)
    with col_ow:
        st.markdown("**🟢 Overweight (חשיפה מוגברת):**")
        if ow:
            for t in ow:
                meta = SECTORS.get(t, {"name_he": t, "emoji": ""})
                st.markdown(f"- {meta['emoji']} **{t}** – {meta['name_he']}")
        else:
            st.markdown("_(אין)_")
    with col_uw:
        st.markdown("**🔴 Underweight (חשיפה מופחתת):**")
        if uw:
            for t in uw:
                meta = SECTORS.get(t, {"name_he": t, "emoji": ""})
                st.markdown(f"- {meta['emoji']} **{t}** – {meta['name_he']}")
        else:
            st.markdown("_(אין)_")

with st.expander("איך לקרוא את ההמלצות"):
    st.markdown(
        """
- **Overweight** = להחזיק יותר מהמשקל ההיסטורי של הסקטור בתוך התיק.
- **Underweight** = להחזיק פחות (או לדלג).
- אלה הטיות **קלות**, לא החלפה מוחלטת. נניח קור של 70% במדד רחב + 30% להטיה לפי השלב.
- **ביצועי עבר אינם מבטיחים ביצועי עתיד.** הסיווג יכול להיות שגוי, במיוחד סביב נקודות מפנה.
- פרטים על איך לתרגם הטיה ל-positions אמיתיים – ראה **מודול 6 (יישום)** ו-**מודול 8 (שילוב בתיק)**.
"""
    )


# ---------------------------- INDICATOR CARDS ----------------------------

st.divider()
st.markdown("### 📈 8 האינדיקטורים – ערכים עדכניים")

CARD_CFG = [
    {"id": "T10Y2Y", "format": "{v:+.2f}%", "yoy": False},
    {"id": "UNRATE", "format": "{v:.1f}%", "yoy": False},
    {"id": "ICSA", "format": "{v:,.0f}K", "yoy": True, "scale": 0.001},
    {"id": "CPIAUCSL", "format": "{v:.1f}", "yoy": True},
    {"id": "INDPRO", "format": "{v:.1f}", "yoy": True},
    {"id": "BAMLH0A0HYM2", "format": "{v:.2f}%", "yoy": False},
    {"id": "FEDFUNDS", "format": "{v:.2f}%", "yoy": False},
    {"id": "UMCSENT", "format": "{v:.1f}", "yoy": True},
]


def _mini_chart(df: pd.DataFrame, years: int = 5) -> go.Figure:
    if df.empty:
        return go.Figure()
    cutoff = df.index[-1] - pd.DateOffset(years=years)
    window = df.loc[df.index >= cutoff]
    fig = go.Figure(
        go.Scatter(
            x=window.index,
            y=window["value"],
            mode="lines",
            line=dict(color="#1f77b4", width=2),
            fill="tozeroy" if window["value"].min() >= 0 else None,
            fillcolor="rgba(31,119,180,0.12)",
        )
    )
    fig.update_layout(
        height=130,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False, showticklabels=False),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


for cfg in CARD_CFG:
    sid = cfg["id"]
    info = SERIES_INFO[sid]
    df = series_data.get(sid, pd.DataFrame())
    date, val = latest_value(df)
    scale = cfg.get("scale", 1.0)
    val_disp = val * scale if pd.notna(val) else val

    with st.container(border=True):
        st.markdown(f"**{info['name_he']}** ({sid})")
        cols = st.columns([2, 1])
        with cols[0]:
            if pd.notna(val):
                st.markdown(
                    f"<div style='font-size:1.7rem;font-weight:700;direction:ltr;text-align:left;'>"
                    f"{cfg['format'].format(v=val_disp)}</div>",
                    unsafe_allow_html=True,
                )
                if cfg.get("yoy"):
                    yoy = _pct_yoy(df)
                    if pd.notna(yoy):
                        color = "#2ecc71" if yoy >= 0 else "#e74c3c"
                        arrow = "▲" if yoy >= 0 else "▼"
                        st.markdown(
                            f"<div style='color:{color};direction:ltr;text-align:left;'>"
                            f"YoY: {arrow} {yoy:+.1f}%</div>",
                            unsafe_allow_html=True,
                        )
                if pd.notna(date):
                    st.caption(f"נכון ל-{date.strftime('%Y-%m-%d')}")
            else:
                st.markdown("_אין נתונים_")
        with cols[1]:
            st.plotly_chart(_mini_chart(df), use_container_width=True, config={"displayModeBar": False})

        st.caption(info["interpretation"])


# ---------------------------- METHODOLOGY ----------------------------

st.divider()
with st.expander("🔬 איך המודל מסווג את השלב"):
    st.markdown(
        """
המודל מציין ניקוד לכל אחד מארבעת השלבים על סמך תנאים מבוססי-חוקים. דוגמאות:

- **מיתון:** עקום תשואות הפוך (T10Y2Y<0), עלייה באבטלה מעל 0.2 נק׳ ב-3 חודשים, ייצור תעשייתי YoY שלילי, מרווחי HY מעל 6%.
- **התאוששות מוקדמת:** אבטלה יורדת, ריבית הפד יורדת, עקום תלול (T10Y2Y>1), ייצור פונה מעלה.
- **אמצע מחזור:** אינפלציה 0–3%, עקום תקין (0.5–2%), ייצור YoY>1.5%, מרווחי HY נמוכים.
- **סוף מחזור:** אינפלציה>3%, הפד מהדק (ΔFF 6m>0.5pp), עקום שטוח, אבטלה ברף נמוך.

כל תנאי תורם ~10–25 נקודות אחוז. המקסימום (אחרי clamping ל-1.0) הוא השלב הזוכה. ביטחון מתחת ל-30% → "לא ודאי".

זהו מודל **חינוכי**, לא מקצועי. בשוק האמיתי אנשי מחקר משלבים גם:
- שינויים שבועיים (כדי לזהות נקודות מפנה מהר)
- מודלי probit (סטטיסטיים, לא חוקים קשיחים)
- נתונים אלטרנטיביים (כרטיסי אשראי, משלוחים, גוגל-טרנדס)
- שיפוט אנושי על אירועים חד-פעמיים (קורונה, חוב תקרה, מלחמות)
"""
    )

with st.expander("⏱️ עיכובי פרסום ותיקונים"):
    st.markdown(
        """
ה-FRED מתעדכן באיחור משתנה:
- **T10Y2Y, FEDFUNDS, BAMLH0A0HYM2** – יומי, עיכוב 1 יום.
- **ICSA** – שבועי, עיכוב ~5 ימים.
- **CPI, INDPRO, RSAFS** – חודשי, עיכוב 2–6 שבועות. **ועוברים תיקונים חודשים אחרי.**
- **UNRATE, PAYEMS** – חודשי (NFP יום שישי הראשון), עיכוב ~1 חודש.
- **UMCSENT** – חודשי, עיכוב ~3 שבועות (preliminary) ו-~5 שבועות (final).

כלומר: הסיווג שאתה רואה היום מבוסס בעיקר על נתוני **חודש קודם**, ויתכן ישתנה לאחור אחרי תיקונים.
"""
    )


# ---------------------------- QUIZ ----------------------------

st.divider()
render_quiz(
    "macro_dashboard",
    [
        {
            "q": "מהו עקום התשואות (T10Y2Y) שלילי?",
            "options": [
                "10Y נמוך מ-2Y (היפוך עקום)",
                "10Y גבוה מ-2Y",
                "ריבית פד מתחת ל-2%",
                "אינפלציה שלילית",
            ],
            "answer": 0,
            "explain": "T10Y2Y<0 = 10-Year נמוך מ-2-Year. היסטורית מבשר על מיתון תוך 6–24 חודשים.",
        },
        {
            "q": "סיגנל Sahm מהי?",
            "options": [
                "אינפלציה מעל 5%",
                "אבטלה עלתה ב-0.5 נק׳ מעל ממוצע 12 חודשים",
                "ייצור תעשייתי שלילי 3 חודשים ברציפות",
                "עקום הפוך מעל 6 חודשים",
            ],
            "answer": 1,
            "explain": "כלל Sahm: כשממוצע 3 חודשים של אבטלה עולה ב-0.5pp מעל המינימום של 12 חודשים אחרונים → מיתון התחיל.",
        },
        {
            "q": "מה ההמלצה הקלאסית למיתון?",
            "options": [
                "XLK, XLY, XLF",
                "XLP, XLV, XLU (defensive)",
                "XLE, XLB (cyclical)",
                "להחזיק 100% מזומן",
            ],
            "answer": 1,
            "explain": "במיתון: defensive sectors – Staples (XLP), Healthcare (XLV), Utilities (XLU). הביקוש שלהם פחות גמיש.",
        },
        {
            "q": "ה-HY OAS מתרחב מ-4% ל-7% – מה זה אומר?",
            "options": [
                "השוק נרגע, פחות סיכון",
                "סטרס פיננסי גובר, סיכון מיתון",
                "ריבית הפד עולה",
                "אינפלציה יורדת",
            ],
            "answer": 1,
            "explain": "מרווחי HY מתרחבים = משקיעים דורשים פיצוי גבוה יותר על חוב מסוכן. סימן מובהק לסטרס פיננסי.",
        },
        {
            "q": "למה הסיווג של המודל לא תמיד תואם את הכותרות בעיתון?",
            "options": [
                "המודל טועה תמיד",
                "החדשות עוקבות נרטיב, המודל עוקב נתונים – ויש פיגור פרסום ותיקונים",
                "FRED לא אמין",
                "צריך תמיד לעשות הפוך מהחדשות",
            ],
            "answer": 1,
            "explain": "נתוני מאקרו מתפרסמים באיחור ועוברים תיקונים. נרטיבים בתקשורת רצים קדימה. מסיבה זו NBER מכריזה על מיתון רק חודשים אחרי שהוא התחיל.",
        },
    ],
)
