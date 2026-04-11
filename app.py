"""Pay Me Back or Else — AI-powered humorous debt collection letter generator."""

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Pay Me Back or Else",
    page_icon="\U0001f4b8",
    layout="centered",
)

# Load Google Fonts
st.markdown(
    '<link href="https://fonts.googleapis.com/css2?family=Permanent+Marker'
    "&family=Special+Elite&family=Patrick+Hand&family=Caveat:wght@400;500"
    '&display=swap" rel="stylesheet">',
    unsafe_allow_html=True,
)

# Load theme CSS
with open("styles/theme.css", "r") as f:
    css = f.read()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Initialize session state
if "current_page" not in st.session_state:
    st.session_state.current_page = "form"
if "rage_level" not in st.session_state:
    st.session_state.rage_level = 1
if "form_data" not in st.session_state:
    st.session_state.form_data = None
if "generated_letter" not in st.session_state:
    st.session_state.generated_letter = None
if "letter_history" not in st.session_state:
    st.session_state.letter_history = []

rage_level = st.session_state.rage_level
current_page = st.session_state.current_page

# Navigation tabs
nav_tabs = {
    "form": ("\u270f\ufe0f", "Write a Letter"),
    "results": ("\U0001f4e8", "Your Letter"),
    "history": ("\U0001f4da", "Past Letters"),
}

nav_html = '<div class="nav-bar">'
for page_key, (icon, label) in nav_tabs.items():
    active_class = "nav-tab-active" if page_key == current_page else "nav-tab-inactive"
    nav_html += (
        f'<button class="nav-tab {active_class}" '
        f'id="nav-{page_key}">{icon} {label}</button>'
    )
nav_html += "</div>"
st.markdown(nav_html, unsafe_allow_html=True)

# Navigation using Streamlit buttons (since HTML buttons can't set session state)
nav_cols = st.columns(3)
with nav_cols[0]:
    if st.button("Write a Letter", key="nav_form", use_container_width=True):
        st.session_state.current_page = "form"
        st.rerun()
with nav_cols[1]:
    if st.button("Your Letter", key="nav_results", use_container_width=True):
        st.session_state.current_page = "results"
        st.rerun()
with nav_cols[2]:
    if st.button("Past Letters", key="nav_history", use_container_width=True):
        st.session_state.current_page = "history"
        st.rerun()

# Rage-level wrapper
st.markdown(f'<div class="rage-{rage_level}">', unsafe_allow_html=True)

# Route to the correct page
if current_page == "form":
    from pages.form import render_form
    render_form()
elif current_page == "results":
    from pages.results import render_results
    render_results()
elif current_page == "history":
    from pages.history import render_history
    render_history()

st.markdown("</div>", unsafe_allow_html=True)
