"""Results page — displays the generated letter with action buttons."""

from urllib.parse import quote

import streamlit as st

from core.generator import generate_letter
from core import history_store



def render_results() -> None:
    """Render the results page with the generated letter and action buttons."""
    letter = st.session_state.get("generated_letter")
    rage_level = st.session_state.get("rage_level", 1)

    if not letter:
        st.markdown(
            '<div class="empty-state">'
            '<p class="empty-text">No letter generated yet.</p>'
            "</div>",
            unsafe_allow_html=True,
        )
        if st.button("Go Write a Letter \u270f\ufe0f", key="go_back_btn"):
            st.session_state.current_page = "form"
            st.rerun()
        return

    # Mascot + title
    col_title, col_mascot = st.columns([3, 1])
    with col_title:
        st.markdown('<h1 class="page-title">Your Letter</h1>', unsafe_allow_html=True)
    with col_mascot:
        _show_mascot(rage_level)

    # Letter box
    rage_class = f"rage-{rage_level}-letter"
    st.markdown(
        f'<div class="letter-box {rage_class}">'
        f'<div id="letter-text" class="letter-text">{_format_letter(letter)}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    # Copy JS injection — pass letter text as a JS variable to avoid encoding issues
    escaped_for_js = letter.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
    copy_html = """
    <script>
    const letterContent = `""" + escaped_for_js + """`;
    function copyLetter() {
        navigator.clipboard.writeText(letterContent).then(function() {
            const btn = document.getElementById('copy-btn-feedback');
            btn.innerText = 'Copied! \u2713';
            btn.style.borderColor = '#2D6A4F';
            btn.style.color = '#2D6A4F';
            setTimeout(function() {
                btn.innerText = '\U0001f4cb Copy';
                btn.style.borderColor = '#1A1A1A';
                btn.style.color = '#1A1A1A';
            }, 2000);
        });
    }
    </script>
    <button id="copy-btn-feedback" onclick="copyLetter()"
            style="font-family: 'Patrick Hand', cursive; font-size: 1rem;
                   padding: 8px 20px; border: 2px solid #1A1A1A;
                   border-radius: 4px; background: transparent;
                   cursor: pointer; color: #1A1A1A;">
        \U0001f4cb Copy
    </button>
    """
    st.components.v1.html(copy_html, height=50)

    # Action buttons row
    btn_cols = st.columns([1, 1, 1, 1])

    with btn_cols[0]:
        if st.button("\U0001f504 Regenerate", key="regenerate_btn", use_container_width=True):
            form_data = st.session_state.get("form_data", {})
            with st.spinner("Writing a fresh version..."):
                new_letter = generate_letter(form_data, rage_level, regenerate=True)
                st.session_state.generated_letter = new_letter
                st.rerun()

    with btn_cols[1]:
        if st.button("\U0001f4be Save to History", key="save_btn", use_container_width=True):
            form_data = st.session_state.get("form_data", {})
            history_store.save_letter(form_data, letter, rage_level)
            st.success("Saved to history!")

    with btn_cols[2]:
        if st.button("\u21a9\ufe0f Start Over", key="startover_btn", use_container_width=True):
            st.session_state.form_data = None
            st.session_state.generated_letter = None
            st.session_state.current_page = "form"
            st.rerun()

    with btn_cols[3]:
        # mailto link
        mailto_body = quote(letter, safe="")
        debtor = st.session_state.get("form_data", {}).get("debtor_name", "")
        subject = quote(f"About that money you owe me, {debtor}", safe="")
        st.markdown(
            f'<a href="mailto:?subject={subject}&body={mailto_body}" '
            f'target="_blank" class="email-btn">'
            f'\u2709\ufe0f Send Email</a>',
            unsafe_allow_html=True,
        )


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


def _format_letter(letter: str) -> str:
    """Convert letter text to HTML paragraphs."""
    paragraphs = letter.strip().split("\n\n")
    html_parts = []
    for p in paragraphs:
        lines = p.strip().replace("\n", "<br>")
        html_parts.append(f"<p>{lines}</p>")
    return "".join(html_parts)


def _escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )
