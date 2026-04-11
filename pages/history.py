"""History page — view, expand, and delete saved letters."""

from datetime import datetime

import streamlit as st

from core import history_store

RAGE_BADGES = {
    1: ("LV 1 \u2764\ufe0f", "#2D6A4F"),
    2: ("LV 2 \U0001f612", "#F9A825"),
    3: ("LV 3 \U0001f525", "#E65100"),
    4: ("LV 4 \U0001f480", "#D32F2F"),
}


def render_history() -> None:
    """Render the history page with saved letters."""
    st.markdown('<h1 class="page-title">Past Letters</h1>', unsafe_allow_html=True)

    letters = history_store.get_letters()

    if not letters:
        _render_empty_state()
        return

    for entry in letters:
        _render_history_card(entry)


def _render_empty_state() -> None:
    """Show the empty state with peaceful Capy."""
    st.markdown('<div class="empty-state">', unsafe_allow_html=True)
    try:
        with open("assets/capy_rage_1.svg", "r") as f:
            svg = f.read()
        st.markdown(
            f'<div class="mascot-container mascot-centered">{svg}</div>',
            unsafe_allow_html=True,
        )
    except FileNotFoundError:
        pass
    st.markdown(
        '<p class="empty-text">No letters yet. Go collect some debts!</p>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


def _render_history_card(entry: dict) -> None:
    """Render a single history card."""
    letter_id = entry["id"]
    debtor = entry["debtor_name"]
    amount = entry["amount"]
    rage = entry["rage_level"]
    letter = entry["letter"]
    created = entry["created_at"]

    # Format date
    try:
        dt = datetime.fromisoformat(created)
        date_str = dt.strftime("%b %d, %Y")
    except (ValueError, TypeError):
        date_str = created

    # Badge
    badge_text, badge_color = RAGE_BADGES.get(rage, ("LV ?", "#6B6B6B"))

    # Preview text
    preview = letter[:80] + "..." if len(letter) > 80 else letter

    # Card header
    st.markdown(
        f'<div class="history-card">'
        f'<div class="history-card-header">'
        f'<span class="history-debtor">{debtor}</span>'
        f'<span class="rage-badge" style="background-color: {badge_color};">'
        f"{badge_text}</span>"
        f"</div>"
        f'<div class="history-meta">'
        f'<span class="history-amount">${amount:.2f}</span>'
        f'<span class="history-date">{date_str}</span>'
        f"</div>"
        f'<p class="history-preview">{preview}</p>'
        f"</div>",
        unsafe_allow_html=True,
    )

    # Expandable full letter
    with st.expander("Read full letter", expanded=False):
        st.markdown(
            f'<div class="history-letter-full">{letter}</div>',
            unsafe_allow_html=True,
        )

        # Delete with confirmation
        delete_key = f"delete_{letter_id}"
        confirm_key = f"confirm_{letter_id}"

        if st.session_state.get(confirm_key, False):
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes, delete", key=f"yes_{letter_id}"):
                    history_store.delete_letter(letter_id)
                    st.session_state.pop(confirm_key, None)
                    st.rerun()
            with col2:
                if st.button("Cancel", key=f"cancel_{letter_id}"):
                    st.session_state.pop(confirm_key, None)
                    st.rerun()
        else:
            if st.button("\U0001f5d1\ufe0f Delete", key=delete_key):
                st.session_state[confirm_key] = True
                st.rerun()
