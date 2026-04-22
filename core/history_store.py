import uuid
from datetime import datetime

import streamlit as st


def _ensure_history() -> list[dict]:
    if "letter_history" not in st.session_state:
        st.session_state["letter_history"] = []
    return st.session_state["letter_history"]


def save_letter(
    form_data: dict,
    letter: str,
    edited_letter: str,
    rage_level: int,
) -> str:
    """Save a letter to history. Returns the letter ID."""
    history = _ensure_history()
    letter_id = str(uuid.uuid4())[:8]
    history.insert(0, {
        "id": letter_id,
        "debtor_name": form_data.get("name", "Unknown"),
        "amount": form_data.get("amount", 0),
        "relationship": form_data.get("relationship", ""),
        "rage_level": rage_level,
        "original_letter": letter,
        "edited_letter": edited_letter,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    return letter_id


def get_letters() -> list[dict]:
    """Return all saved letters, newest first."""
    return _ensure_history()


def delete_letter(letter_id: str) -> bool:
    """Delete a letter by ID. Returns True if found and deleted."""
    history = _ensure_history()
    for i, entry in enumerate(history):
        if entry["id"] == letter_id:
            history.pop(i)
            return True
    return False
