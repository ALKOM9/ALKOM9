"""Reusable 5-question quiz component for course modules."""
from __future__ import annotations

import streamlit as st


def render_quiz(module_key: str, questions: list[dict]) -> None:
    """Render a multi-choice quiz.

    Each question dict must have:
        - "q": question text (str)
        - "options": list[str]
        - "answer": index of correct option (int, 0-based)
        - "explain": short explanation shown after answering (str)
    """
    st.markdown("### 🧠 חידון – 5 שאלות")
    st.caption("ענה על כל השאלות ולחץ \"בדוק תשובות\". התשובות לא נשמרות בין ביקורים באתר.")

    state_key = f"quiz_state_{module_key}"
    if state_key not in st.session_state:
        st.session_state[state_key] = {"answers": {}, "submitted": False}

    state = st.session_state[state_key]

    for i, q in enumerate(questions):
        st.markdown(f"**שאלה {i + 1}.** {q['q']}")
        key = f"{module_key}_q{i}"
        choice = st.radio(
            label=f"שאלה {i + 1}",
            options=list(range(len(q["options"]))),
            format_func=lambda idx, opts=q["options"]: opts[idx],
            key=key,
            label_visibility="collapsed",
            index=None,
        )
        state["answers"][i] = choice

        if state["submitted"]:
            correct = q["answer"]
            if choice == correct:
                st.markdown(
                    f"<div class='quiz-correct'>✅ נכון. {q['explain']}</div>",
                    unsafe_allow_html=True,
                )
            else:
                correct_text = q["options"][correct]
                st.markdown(
                    f"<div class='quiz-wrong'>❌ לא נכון. התשובה הנכונה: <b>{correct_text}</b>. {q['explain']}</div>",
                    unsafe_allow_html=True,
                )
        st.write("")

    cols = st.columns(2)
    with cols[0]:
        if st.button("בדוק תשובות", key=f"{module_key}_check", use_container_width=True, type="primary"):
            state["submitted"] = True
            st.rerun()
    with cols[1]:
        if st.button("איפוס חידון", key=f"{module_key}_reset", use_container_width=True):
            st.session_state[state_key] = {"answers": {}, "submitted": False}
            for i in range(len(questions)):
                st.session_state.pop(f"{module_key}_q{i}", None)
            st.rerun()

    if state["submitted"]:
        correct_count = sum(
            1 for i, q in enumerate(questions) if state["answers"].get(i) == q["answer"]
        )
        st.markdown(f"#### ציון: **{correct_count} / {len(questions)}**")
        if correct_count == len(questions):
            st.success("🎉 ציון מושלם.")
        elif correct_count >= len(questions) * 0.6:
            st.info("ציון סביר, אבל כדאי לחזור על מה שטעית בו.")
        else:
            st.warning("כדאי לקרוא את המודול שוב לפני המעבר הלאה.")
