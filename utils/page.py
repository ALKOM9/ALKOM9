"""Shared page bootstrap: page config + style + auth + consent gates.

Every page (app.py and pages/*.py) calls bootstrap() at the top.
"""
from __future__ import annotations

import streamlit as st

from utils.auth import require_password, logout_button
from utils.consent import require_consent
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
