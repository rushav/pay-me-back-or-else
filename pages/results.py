import streamlit as st
import streamlit.components.v1 as stc

from components.chicken import render_chicken
from components.loading import render_loading
from components.letter_box import render_letter_box
from core.generator import generate_letter
from core.history_store import save_letter
from core.email_sender import send_letter_email, get_mailto_link


def _do_generate(form_data: dict, rage_level: int, family_friendly: bool, regenerate: bool = False):
    """Generate the letter and store in session state."""
    letter = generate_letter(form_data, rage_level, family_friendly, regenerate)
    st.session_state["generated_letter"] = letter
    st.session_state["edited_letter"] = letter


def render_results():
    """Render the results page with letter display, edit area, and action buttons."""
    form_data = st.session_state.get("form_data")
    rage_level = st.session_state.get("rage_level", 1)
    family_friendly = st.session_state.get("family_friendly", True)

    if not form_data:
        st.markdown("<h1>Your Letter 📨</h1>", unsafe_allow_html=True)
        st.markdown("No letter yet! Fill out the form first.")
        if st.button("Go to Form ✏️"):
            st.session_state["current_page"] = "form"
            st.rerun()
        return

    if st.session_state.get("needs_generation", False):
        st.session_state["needs_generation"] = False
        col_load, col_chick = st.columns([2, 1])
        with col_load:
            st.markdown("<h1>Your Letter 📨</h1>", unsafe_allow_html=True)
            placeholder = st.empty()
            with placeholder:
                render_loading(rage_level)
        with col_chick:
            render_chicken(rage_level)

        _do_generate(form_data, rage_level, family_friendly, regenerate=False)
        st.rerun()

    letter = st.session_state.get("generated_letter", "")
    debtor_name = form_data.get("name", "Friend")

    col_content, col_chicken = st.columns([2, 1])

    with col_content:
        st.markdown("<h1>Your Letter 📨</h1>", unsafe_allow_html=True)

        if letter and not letter.startswith("ERROR:"):
            render_letter_box(letter, debtor_name, rage_level)

            st.markdown(
                '<p style="font-family:\'Schoolbell\',cursive;font-size:1.1rem;">'
                '✏️ Edit your letter before sending:</p>',
                unsafe_allow_html=True,
            )
            edited = st.text_area(
                "Edit letter",
                value=st.session_state.get("edited_letter", letter),
                height=250,
                key="letter_edit_area",
                label_visibility="collapsed",
            )
            st.session_state["edited_letter"] = edited

            btn_cols = st.columns(5)

            with btn_cols[0]:
                copy_js = f"""
                <textarea id="copy-src" style="position:absolute;left:-9999px">{edited.replace(chr(10), chr(10)).replace('"', '&quot;')}</textarea>
                <button onclick="
                    navigator.clipboard.writeText(document.getElementById('copy-src').value)
                    .then(()=>{{
                        const b=this;b.textContent='Copied! ✓';b.style.borderColor='#2D6A4F';
                        setTimeout(()=>{{b.textContent='📋 Copy';b.style.borderColor='#1A1A1A';}},2000);
                    }});
                " style="font-family:'Schoolbell',cursive;font-size:1rem;padding:0.4rem 0.8rem;
                background:white;border:2px dashed #1A1A1A;border-radius:3px;cursor:pointer;
                box-shadow:3px 3px 0px #1A1A1A;transform:rotate(-0.5deg);width:100%;">
                📋 Copy</button>
                """
                stc.html(copy_js, height=50)

            with btn_cols[1]:
                if st.button("🔄 New One", key="regen_btn", use_container_width=True):
                    placeholder = st.empty()
                    with placeholder:
                        render_loading(rage_level)
                    _do_generate(form_data, rage_level, family_friendly, regenerate=True)
                    st.rerun()

            with btn_cols[2]:
                if st.button("💾 Save", key="save_btn", use_container_width=True):
                    save_letter(form_data, letter, edited, rage_level)
                    st.toast("Saved to history! 💾")

            with btn_cols[3]:
                debtor_email = form_data.get("debtor_email", "")
                if st.button("✉️ Send", key="send_btn", use_container_width=True):
                    if debtor_email:
                        success, msg = send_letter_email(debtor_email, debtor_name, edited)
                        if success:
                            st.toast(msg)
                        elif msg == "mailto":
                            mailto = get_mailto_link(debtor_email, debtor_name, edited)
                            st.markdown(
                                f'<a href="{mailto}" target="_blank" '
                                f'style="font-family:\'Schoolbell\',cursive;">Open in email app</a>',
                                unsafe_allow_html=True,
                            )
                        else:
                            st.error(msg)
                    else:
                        st.warning("No email address provided. Add one on the form page!")

            with btn_cols[4]:
                if st.button("↩️ Start Over", key="startover_btn", use_container_width=True):
                    st.session_state["form_data"] = None
                    st.session_state["generated_letter"] = None
                    st.session_state["edited_letter"] = None
                    st.session_state["current_page"] = "form"
                    st.rerun()

        elif letter and letter.startswith("ERROR:"):
            st.error(letter.replace("ERROR: ", ""))
            if st.button("🔄 Try Again", use_container_width=True):
                st.session_state["needs_generation"] = True
                st.rerun()
        else:
            st.info("No letter generated yet.")
            if st.button("🔄 Generate", use_container_width=True):
                st.session_state["needs_generation"] = True
                st.rerun()

    with col_chicken:
        render_chicken(rage_level)
