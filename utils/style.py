import streamlit as st


_GLOBAL_CSS = """
<style>
/* Hebrew RTL + mobile-friendly base */
html, body, [class*="css"] {
    direction: rtl;
    text-align: right;
}

/* Keep app block tight on mobile */
.main .block-container {
    padding-top: 1.2rem;
    padding-bottom: 3rem;
    padding-left: 1rem;
    padding-right: 1rem;
    max-width: 900px;
}

/* Larger base font, scale up on small screens */
html { font-size: 17px; }
@media (max-width: 768px) {
    html { font-size: 18px; }
    .main .block-container { padding-left: 0.6rem; padding-right: 0.6rem; }
    h1 { font-size: 1.7rem !important; line-height: 1.25 !important; }
    h2 { font-size: 1.35rem !important; }
    h3 { font-size: 1.15rem !important; }
}

/* Buttons large enough for finger taps */
.stButton > button, .stDownloadButton > button {
    min-height: 48px;
    font-size: 1.05rem;
    font-weight: 600;
    border-radius: 12px;
    width: 100%;
}

/* Inputs */
input, textarea, select { font-size: 1rem !important; }
[data-baseweb="input"] input, [data-baseweb="select"] {
    direction: rtl;
    text-align: right;
}

/* Math / formulas - keep LTR */
.formula, code, pre, .stCode {
    direction: ltr !important;
    text-align: left !important;
    unicode-bidi: embed;
}

/* Tables and dataframes look better LTR on mobile */
.stDataFrame, .stTable { direction: ltr; }

/* Metric cards */
[data-testid="stMetricValue"] { direction: ltr; }

/* Quiz blocks */
.quiz-correct {
    background: #143d2b;
    border: 1px solid #2ecc71;
    color: #b5f5d0;
    padding: 0.7rem 1rem;
    border-radius: 10px;
    margin-top: 0.6rem;
}
.quiz-wrong {
    background: #401818;
    border: 1px solid #e74c3c;
    color: #ffd5d0;
    padding: 0.7rem 1rem;
    border-radius: 10px;
    margin-top: 0.6rem;
}

/* Sidebar nav - keep readable in Hebrew */
[data-testid="stSidebar"] { direction: rtl; text-align: right; }
[data-testid="stSidebarNav"] a span { text-align: right; }

/* Prevent horizontal scroll on small phones */
body { overflow-x: hidden; }

/* Consent screen card */
.consent-card {
    background: #1c1f26;
    border: 1px solid #2a2f3a;
    border-radius: 14px;
    padding: 1.2rem;
    margin: 0.6rem 0 1rem 0;
    line-height: 1.6;
}
.consent-card.en { direction: ltr; text-align: left; }

/* Lock icon */
.lock-emoji { font-size: 2.4rem; display: block; text-align: center; margin: 0.5rem 0; }
</style>
"""


def inject_global_styles() -> None:
    """Inject base CSS for RTL + mobile responsiveness. Call once per page."""
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str | None = None) -> None:
    """Consistent header for module pages."""
    st.markdown(f"## {title}")
    if subtitle:
        st.caption(subtitle)
    st.divider()
