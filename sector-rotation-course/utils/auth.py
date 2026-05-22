import streamlit as st


_SESSION_FLAG = "auth_ok"


def _get_expected_password() -> str | None:
    """Pull password from st.secrets. Returns None if missing."""
    try:
        return st.secrets["password"]
    except Exception:
        return None


def require_password() -> bool:
    """Render password prompt. Returns True when authenticated.

    Stops the script (st.stop) when not authenticated so the rest of the
    page does not execute.
    """
    if st.session_state.get(_SESSION_FLAG):
        return True

    expected = _get_expected_password()

    st.markdown("<div class='lock-emoji'>🔒</div>", unsafe_allow_html=True)
    st.markdown("### כניסה לקורס")
    st.caption("הקלד את הסיסמה שהגדרת ב-Streamlit Secrets.")

    if expected is None:
        st.error(
            "⚠️ לא נמצאה סיסמה ב-Streamlit Secrets.\n\n"
            "פתח את Streamlit Cloud → Settings → Secrets, "
            "והוסף:\n\npassword = \"YOUR_STRONG_PASSWORD\"\n\n"
            "אחר כך Save → Reboot."
        )
        st.stop()

    with st.form("login_form", clear_on_submit=False):
        pw = st.text_input("סיסמה", type="password", autocomplete="current-password")
        submitted = st.form_submit_button("היכנס")

    if submitted:
        if pw == expected:
            st.session_state[_SESSION_FLAG] = True
            st.rerun()
        else:
            st.error("סיסמה שגויה. נסה שוב.")

    st.stop()
    return False  # unreachable but keeps type-checkers happy


def logout_button(label: str = "🚪 התנתק") -> None:
    """Render a logout button in the sidebar."""
    with st.sidebar:
        if st.button(label, use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
