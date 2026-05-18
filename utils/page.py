"""Shared page bootstrap: page config + style + auth + consent gates.

Every page (app.py and pages/*.py) calls bootstrap() at the top, and
page_end() at the bottom. Persistent NOT-FINANCIAL-ADVICE disclaimers
(bilingual HE+EN) are rendered automatically: top ribbon, sidebar, footer.
"""
from __future__ import annotations

import streamlit as st

from utils.auth import require_password, logout_button
from utils.consent import require_consent
from utils.disclaimer import render_footer, render_sidebar, render_top_ribbon
from utils.style import inject_global_styles


def bootstrap(page_title: str = "קורס Triangular Arbitrage") -> None:
    st.set_page_config(
        page_title=page_title,
        page_icon="🔺",
        layout="centered",
        initial_sidebar_state="auto",
    )
    inject_global_styles()
    require_password()
    require_consent()
    logout_button()
    render_sidebar()
    render_top_ribbon()


def page_end() -> None:
    """Render the legal footer. Call at the bottom of each page file."""
    render_footer()
