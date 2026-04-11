"""Input form page for debt collection letter generator."""

import streamlit as st

from core.prompts import RAGE_LABELS
from core.generator import generate_letter

SUBMIT_LABELS = {
    1: "Write My Letter \u2709\ufe0f",
    2: "Draft the Message \U0001f624",
    3: "Let Them Have It \U0001f525",
    4: "UNLEASH THE LETTER \U0001f480",
}


def render_form() -> None:
    """Render the debt collection letter input form."""
    rage_level = st.session_state.get("rage_level", 1)

    # Mascot in top-right area
    col_title, col_mascot = st.columns([3, 1])
    with col_title:
        st.markdown('<h1 class="page-title">Write Your Letter</h1>', unsafe_allow_html=True)
        st.markdown(
            '<p class="page-subtitle">Fill in the details below and let the capybara do the rest.</p>',
            unsafe_allow_html=True,
        )
    with col_mascot:
        _show_mascot(rage_level)

    # Form card
    st.markdown('<div class="card form-card">', unsafe_allow_html=True)

    debtor_name = st.text_input(
        "Debtor Name *",
        placeholder="Who owes you money?",
        key="debtor_name_input",
    )

    amount = st.number_input(
        "Amount Owed ($) *",
        min_value=0.01,
        step=0.01,
        value=None,
        format="%.2f",
        key="amount_input",
        placeholder="0.00",
    )

    duration = st.text_input(
        "How Long They've Owed You *",
        placeholder="e.g. 3 months, since last summer",
        key="duration_input",
    )

    relationship = st.selectbox(
        "Relationship *",
        options=["Friend", "Roommate", "Family", "Co-worker", "Ex", "Acquaintance"],
        key="relationship_input",
    )

    context = st.text_area(
        "Context / What Happened (optional)",
        placeholder="They said they'd pay me back after brunch...",
        max_chars=300,
        key="context_input",
    )

    venmo_handle = st.text_input(
        "Your Venmo/Zelle Handle (optional)",
        placeholder="@yourhandle",
        key="venmo_input",
    )

    # Rage slider
    rage_level = st.slider(
        "Rage Level",
        min_value=1,
        max_value=4,
        value=st.session_state.get("rage_level", 1),
        step=1,
        key="rage_slider",
    )
    st.session_state.rage_level = rage_level

    # Rage label display
    label, description = RAGE_LABELS[rage_level]
    rage_colors = {1: "#2D6A4F", 2: "#F9A825", 3: "#E65100", 4: "#D32F2F"}
    st.markdown(
        f'<p class="rage-label" style="color: {rage_colors[rage_level]}; '
        f'font-family: \'Permanent Marker\', cursive;">'
        f'{rage_level} &mdash; {label}</p>'
        f'<p class="rage-description">{description}</p>',
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # Validation
    can_submit = bool(debtor_name and amount and amount > 0 and duration and relationship)

    # Submit button
    submit_label = SUBMIT_LABELS[rage_level]
    if st.button(submit_label, disabled=not can_submit, use_container_width=True, key="submit_btn"):
        form_data = {
            "debtor_name": debtor_name,
            "amount": amount,
            "duration": duration,
            "relationship": relationship,
            "context": context or "",
            "venmo_handle": venmo_handle or "",
        }
        st.session_state.form_data = form_data

        with st.spinner("The capybara is writing your letter..."):
            letter = generate_letter(form_data, rage_level)
            st.session_state.generated_letter = letter
            st.session_state.current_page = "results"
            st.rerun()


def _show_mascot(rage_level: int) -> None:
    """Display the mascot SVG for the given rage level."""
    try:
        with open(f"assets/capy_rage_{rage_level}.svg", "r") as f:
            svg = f.read()
        st.markdown(
            f'<div class="mascot-container">{svg}</div>',
            unsafe_allow_html=True,
        )
    except FileNotFoundError:
        pass
