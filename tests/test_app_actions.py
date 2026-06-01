"""Tests for app._handle_action — the reopen + interrupt-save dispatch.

These exercise the server-side half of changes #1 and #2 without a browser:
a fake session_state (a plain dict is enough for app's access patterns) and a
fake db_service capture the effects of each action payload.
"""

import pytest

import app


@pytest.fixture
def fake_state(monkeypatch):
    state = {
        "view": "app",
        "rage_level": 1,
        "form_data": {
            "debtor_name": "InProgress", "amount": "10", "time_owed": "1",
            "time_unit": "days", "relationship": "friend",
            "context": "", "payment_handle": "",
        },
        "generated_letter": "an in-progress letter being written",
        "is_streaming": False,
        "letter_instant": False,
        "validation_errors": [],
        "api_error": None,
        "last_action_nonce": None,
        "letters": [
            {"id": 5, "debtor_name": "Dana", "amount": 50.0, "duration": "2 days",
             "relationship": "ex", "rage_level": 4, "letter_text": "pay up dana",
             "created_at": "2026-05-30 09:00:00"},
        ],
    }
    monkeypatch.setattr(app.st, "session_state", state)
    return state


@pytest.fixture
def fake_db(monkeypatch):
    saves = []

    class FakeDB:
        @staticmethod
        def save_letter(form, text):
            saves.append((dict(form), text))
            return 99

        @staticmethod
        def get_all_letters():
            return app.st.session_state["letters"]

        @staticmethod
        def delete_letter(_id):
            pass

    monkeypatch.setattr(app, "db_service", FakeDB)
    return saves


def test_reopen_restores_letter_form_and_rage(fake_state, fake_db):
    app._handle_action({"action": "reopen", "id": 5,
                        "letter": {"id": 5, "letter_text": "pay up dana", "rage_level": 4},
                        "_nonce": "n1"})
    assert fake_state["generated_letter"] == "pay up dana"
    assert fake_state["rage_level"] == 4
    assert fake_state["form_data"]["debtor_name"] == "Dana"
    assert fake_state["form_data"]["time_owed"] == "2"
    assert fake_state["form_data"]["time_unit"] == "days"
    assert fake_state["form_data"]["relationship"] == "ex"
    # Reopened letters render instantly (no typewriter) and are not streaming.
    assert fake_state["letter_instant"] is True
    assert fake_state["is_streaming"] is False
    # No save happened — this was a plain reopen.
    assert fake_db == []


def test_save_and_continue_persists_partial_then_reopens(fake_state, fake_db):
    app._handle_action({
        "action": "reopen", "id": 5,
        "letter": {"id": 5, "letter_text": "pay up dana", "rage_level": 4},
        "save_first": {"form_data": fake_state["form_data"], "rage": 1,
                       "letter_text": "an in-progress letter being written"},
        "_nonce": "n2",
    })
    # The in-progress (partial) letter was saved with ITS form + rage…
    assert len(fake_db) == 1
    saved_form, saved_text = fake_db[0]
    assert saved_text == "an in-progress letter being written"
    assert saved_form["debtor_name"] == "InProgress"
    assert saved_form["rage_level"] == 1
    # …then the selected letter loaded.
    assert fake_state["generated_letter"] == "pay up dana"
    assert fake_state["rage_level"] == 4


def test_discard_and_start_over_saves_nothing_and_clears(fake_state, fake_db):
    app._handle_action({"action": "start_over", "_nonce": "n3"})
    assert fake_db == []
    assert fake_state["generated_letter"] is None
    assert fake_state["form_data"]["debtor_name"] == ""
    assert fake_state["letter_instant"] is True


def test_empty_partial_letter_is_not_saved(fake_state, fake_db):
    # Phase A: streaming started but no letter text yet — save_first is a no-op.
    app._handle_action({
        "action": "start_over",
        "save_first": {"form_data": fake_state["form_data"], "rage": 2, "letter_text": ""},
        "_nonce": "n4",
    })
    assert fake_db == []


def test_reopen_local_entry_recovers_full_row_by_letter_text(fake_state, fake_db):
    # An optimistic 'local-…' id won't match by id, but the letter_text does,
    # so the full DB row (relationship, duration) is recovered, not defaulted.
    app._handle_action({
        "action": "reopen", "id": "local-1717",
        "letter": {"id": "local-1717", "debtor_name": "Dana", "amount": 50,
                   "rage_level": 4, "letter_text": "pay up dana"},
        "_nonce": "n5",
    })
    assert fake_state["form_data"]["relationship"] == "ex"
    assert fake_state["form_data"]["time_owed"] == "2"
    assert fake_state["form_data"]["time_unit"] == "days"
