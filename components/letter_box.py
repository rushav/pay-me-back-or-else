import streamlit as st


def render_letter_box(letter_text: str, debtor_name: str, rage_level: int):
    """Render the letter in a realistic physical letter style."""
    rage_class = "rage-4-letter" if rage_level == 4 else ""
    glow_class = "rage-4-glow" if rage_level == 4 else ""

    escaped = letter_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")

    html = f"""
    <div class="letter-paper {rage_class} {glow_class}">
        <div class="letter-stamp">&#x1F414;</div>
        <div class="letter-to">TO: {debtor_name}</div>
        <div style="position:relative;z-index:2;">
            {escaped}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
