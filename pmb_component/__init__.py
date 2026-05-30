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

import sys
from pathlib import Path

import streamlit.components.v1 as components


_FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"

# Defensive check at import time. If the frontend folder didn't ship with
# the deploy (e.g. cleared by an aggressive .gitignore, missed in a build
# step, or a stale CDN cache), declare_component would still succeed at
# import but every render would silently 404 — the live page just goes
# blank with no traceback. Logging the resolved path here makes the
# next misconfiguration immediately visible in Streamlit Cloud's logs.
if not (_FRONTEND_DIR / "index.html").exists():
    print(
        f"[pmb_component] FATAL: frontend not found at {_FRONTEND_DIR} "
        f"(cwd={Path.cwd()}, __file__={__file__})",
        file=sys.stderr, flush=True,
    )
else:
    print(
        f"[pmb_component] frontend resolved at {_FRONTEND_DIR}",
        file=sys.stderr, flush=True,
    )

_pmb = components.declare_component("pmb_chicken", path=str(_FRONTEND_DIR))


def render(payload_html: str, key: str = "pmb_chicken", default=None):
    """Render the chicken iframe and return any action the inner iframe posted."""
    return _pmb(payload_html=payload_html, key=key, default=default)
