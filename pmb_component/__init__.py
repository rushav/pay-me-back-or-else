"""Custom Streamlit component for the chicken's iframe.

The previous wiring used ``streamlit.components.v1.html`` for the iframe,
which is render-only — its iframe does NOT listen for the
``streamlit:setComponentValue`` postMessage protocol, so every action the
inner React app dispatched (submit, save, delete, regenerate, …) was
silently dropped on the Python side.

This module registers a real declared component whose minimal frontend
harness wraps a nested iframe via ``srcdoc``. The harness:
  1. Receives the rendered HTML string from Python via component args.
  2. srcdoc's it into an inner iframe (same payload as before).
  3. Forwards any ``isStreamlitMessage`` postMessages from the inner
     iframe up to the Streamlit parent, so setComponentValue round-trips
     and the inner React app's actions actually reach Python.

The Python return value of ``render`` is whatever the inner iframe last
posted via ``streamlit:setComponentValue`` (a dict like
``{"action": "submit", "form_data": {...}, "rage": 3, "_nonce": …}``).
"""

from pathlib import Path

import streamlit.components.v1 as components


_FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"
_pmb = components.declare_component("pmb_chicken", path=str(_FRONTEND_DIR))


def render(payload_html: str, key: str = "pmb_chicken", default=None):
    """Render the chicken iframe and return any action the inner iframe posted."""
    return _pmb(payload_html=payload_html, key=key, default=default)
