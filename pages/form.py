import streamlit as st
from components.chicken import render_chicken


RAGE_LABELS = {
    1: ("Heaven", "Sweet and angelic", "#2D6A4F"),
    2: ("Purgatory", "Passive aggressive shade", "#F9A825"),
    3: ("Inferno", "Fed up and furious", "#E65100"),
    4: ("HELL", "Full demonic rage", "#D32F2F"),
}

RAGE_EMOJIS = {1: "😇", 2: "😤", 3: "🔥", 4: "💀"}

SUBMIT_LABELS = {
    1: "Write My Letter ✉️",
    2: "Draft the Shade 😤",
    3: "Let Them Have It 🔥",
    4: "UNLEASH HELL 💀",
}

RELATIONSHIPS = [
    "Best Friend", "Roommate", "Family", "Co-worker",
    "Ex-Boyfriend", "Ex-Girlfriend", "Acquaintance", "Frenemy",
]


def render_form():
    """Render the input form page with chicken mascot on the right."""
    col_form, col_chicken = st.columns([2, 1])

    with col_form:
        st.markdown("<h1>Pay Me Back or Else 🐔</h1>", unsafe_allow_html=True)
        st.markdown("Generate an AI-powered, hilariously unhinged debt collection letter.")

        st.markdown('<div class="scratchy-card">', unsafe_allow_html=True)

        name = st.text_input("Their Name", key="debtor_name", placeholder="e.g. Jake")

        amount = st.number_input(
            "Amount Owed ($)", min_value=0.01, step=0.01, format="%.2f", key="amount_owed"
        )

        duration_str = st.text_input(
            "How Long They've Owed You", key="duration_str",
            placeholder="e.g. 3 months, since last summer"
        )

        relationship = st.selectbox("Your Relationship", RELATIONSHIPS, key="relationship")

        context = st.text_area(
            "What Happened (optional)", key="context",
            max_chars=300, height=80, placeholder="e.g. Lent them money for concert tickets..."
        )

        debtor_email = st.text_input(
            "Their Email Address (optional)", key="debtor_email",
            placeholder="e.g. jake@example.com"
        )

        payment_handle = st.text_input(
            "Your Venmo/Zelle Handle (optional)", key="payment_handle",
            placeholder="e.g. @yourname"
        )

        rage_level = st.slider("Rage Level", min_value=1, max_value=4, value=1, key="rage_level")

        emoji = RAGE_EMOJIS[rage_level]
        label_name, label_desc, label_color = RAGE_LABELS[rage_level]
        st.markdown(
            f'<div style="font-family:\'Rock Salt\',cursive;font-size:1rem;color:{label_color};'
            f'margin-top:-0.5rem;margin-bottom:1rem;">'
            f'{emoji} {label_name} — {label_desc}</div>',
            unsafe_allow_html=True,
        )

        family_friendly = st.checkbox(
            "Keep it family friendly (no profanity)", value=True, key="family_friendly"
        )

        st.markdown('</div>', unsafe_allow_html=True)

        can_submit = bool(name and name.strip()) and amount > 0 and bool(duration_str and duration_str.strip())

        st.markdown(f'<div class="submit-btn-rage-{rage_level}">', unsafe_allow_html=True)
        if st.button(
            SUBMIT_LABELS[rage_level],
            disabled=not can_submit,
            use_container_width=True,
            key="submit_btn",
        ):
            st.session_state["form_data"] = {
                "name": name.strip(),
                "amount": amount,
                "duration_str": duration_str.strip(),
                "relationship": relationship,
                "context": context.strip() if context else "",
                "debtor_email": debtor_email.strip() if debtor_email else "",
                "payment_handle": payment_handle.strip() if payment_handle else "",
            }
            st.session_state["generated_letter"] = None
            st.session_state["edited_letter"] = None
            st.session_state["family_friendly"] = family_friendly
            st.session_state["needs_generation"] = True
            st.session_state["current_page"] = "results"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_chicken:
        render_chicken(rage_level)
