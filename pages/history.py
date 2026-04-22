import streamlit as st

from components.chicken import render_chicken
from core.history_store import get_letters, delete_letter


RAGE_BADGES = {
    1: ("😇 LV1", "rage-badge-1"),
    2: ("😤 LV2", "rage-badge-2"),
    3: ("🔥 LV3", "rage-badge-3"),
    4: ("💀 LV4", "rage-badge-4"),
}


def render_history():
    """Render the history page with saved letters."""
    st.markdown("<h1>Past Letters 📚</h1>", unsafe_allow_html=True)

    letters = get_letters()

    if not letters:
        st.markdown(
            '<div class="empty-state">'
            '<p style="font-size:1.4rem;">No letters yet. Go ruffle some feathers! 🐔</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        render_chicken(1, height=300)
        return

    for entry in letters:
        letter_id = entry["id"]
        debtor = entry["debtor_name"]
        amount = entry["amount"]
        rage = entry["rage_level"]
        created = entry["created_at"]
        edited_letter = entry.get("edited_letter", entry.get("original_letter", ""))

        badge_text, badge_class = RAGE_BADGES.get(rage, ("?", ""))
        preview = edited_letter[:80] + "..." if len(edited_letter) > 80 else edited_letter

        st.markdown(
            f'<div class="history-card">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;">'
            f'<span style="font-family:\'Rock Salt\',cursive;font-size:1.1rem;">{debtor}</span>'
            f'<span class="rage-badge {badge_class}">{badge_text}</span>'
            f'</div>'
            f'<div style="font-family:\'Schoolbell\',cursive;font-size:0.9rem;color:#6B6B6B;margin:0.3rem 0;">'
            f'${amount:.2f} &middot; {created}'
            f'</div>'
            f'<div style="font-family:\'Gaegu\',cursive;font-size:1rem;color:#444;">{preview}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        col_expand, col_delete = st.columns([4, 1])

        with col_expand:
            with st.expander("Read full letter"):
                st.markdown(
                    f'<div style="font-family:\'Gaegu\',cursive;font-size:1.1rem;line-height:1.8;'
                    f'white-space:pre-wrap;">{edited_letter}</div>',
                    unsafe_allow_html=True,
                )

        with col_delete:
            confirm_key = f"confirm_del_{letter_id}"
            if st.session_state.get(confirm_key, False):
                st.markdown(
                    '<span style="font-family:\'Schoolbell\',cursive;font-size:0.9rem;color:#D32F2F;">'
                    'Are you sure?</span>',
                    unsafe_allow_html=True,
                )
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Yes", key=f"yes_del_{letter_id}"):
                        delete_letter(letter_id)
                        st.session_state[confirm_key] = False
                        st.rerun()
                with c2:
                    if st.button("No", key=f"no_del_{letter_id}"):
                        st.session_state[confirm_key] = False
                        st.rerun()
            else:
                if st.button("🗑️", key=f"del_{letter_id}"):
                    st.session_state[confirm_key] = True
                    st.rerun()
