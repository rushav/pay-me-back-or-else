"""History storage interface using Streamlit session state.

Designed as a swappable backend — callers use save_letter(), get_letters(),
and delete_letter() without knowing the storage implementation.
"""

from datetime import datetime
import uuid

import streamlit as st


def _ensure_history() -> list:
    """Ensure letter_history exists in session state."""
    if "letter_history" not in st.session_state:
        st.session_state.letter_history = []
    return st.session_state.letter_history


def save_letter(form_data: dict, letter: str, rage_level: int) -> str:
    """Save a letter to history. Returns the letter ID."""
    history = _ensure_history()
    letter_id = str(uuid.uuid4())
    entry = {
        "id": letter_id,
        "debtor_name": form_data["debtor_name"],
        "amount": form_data["amount"],
        "rage_level": rage_level,
        "letter": letter,
        "created_at": datetime.now().isoformat(),
        "form_data": form_data,
    }
    history.insert(0, entry)
    return letter_id


def get_letters() -> list[dict]:
    """Return all saved letters, newest first."""
    return list(_ensure_history())


def delete_letter(letter_id: str) -> bool:
    """Delete a letter by ID. Return True if found and deleted."""
    history = _ensure_history()
    for i, entry in enumerate(history):
        if entry["id"] == letter_id:
            history.pop(i)
            return True
    return False
