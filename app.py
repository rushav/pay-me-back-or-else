import streamlit as st

st.set_page_config(
    page_title="Pay Me Back or Else",
    page_icon="🐔",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- Google Fonts + Theme CSS ---
st.markdown(
    '<link href="https://fonts.googleapis.com/css2?family=Coming+Soon&family=Gaegu:wght@300;400;700'
    '&family=Rock+Salt&family=Schoolbell&display=swap" rel="stylesheet">',
    unsafe_allow_html=True,
)

with open("styles/theme.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Session State Defaults ---
defaults = {
    "current_page": "form",
    "form_data": None,
    "generated_letter": None,
    "edited_letter": None,
    "letter_history": [],
    "family_friendly": True,
    "needs_generation": False,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

rage_level = st.session_state.get("rage_level", 1)

# --- Rage-level background wrapper ---
st.markdown(f'<div class="rage-{rage_level}">', unsafe_allow_html=True)

# --- Hide sidebar ---
st.markdown(
    "<style>[data-testid='stSidebar']{display:none;}</style>",
    unsafe_allow_html=True,
)

# --- Navigation Tabs ---
current_page = st.session_state.get("current_page", "form")

nav_html = '<div class="nav-tabs-container">'
tabs = [
    ("form", "✏️ Write a Letter"),
    ("results", "📨 Your Letter"),
    ("history", "📚 Past Letters"),
]
for page_key, label in tabs:
    active = "active" if current_page == page_key else ""
    nav_html += f'<span class="nav-tab {active}" id="nav-{page_key}">{label}</span>'
nav_html += '</div>'
st.markdown(nav_html, unsafe_allow_html=True)

nav_cols = st.columns(3)
with nav_cols[0]:
    if st.button("✏️ Write", key="nav_form", use_container_width=True):
        st.session_state["current_page"] = "form"
        st.rerun()
with nav_cols[1]:
    if st.button("📨 Letter", key="nav_results", use_container_width=True):
        st.session_state["current_page"] = "results"
        st.rerun()
with nav_cols[2]:
    if st.button("📚 History", key="nav_history", use_container_width=True):
        st.session_state["current_page"] = "history"
        st.rerun()

st.markdown('<div class="page-fade-in">', unsafe_allow_html=True)

# --- Page Routing ---
if current_page == "form":
    from pages.form import render_form
    render_form()
elif current_page == "results":
    from pages.results import render_results
    render_results()
elif current_page == "history":
    from pages.history import render_history
    render_history()

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
