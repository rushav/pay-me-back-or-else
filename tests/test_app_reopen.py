"""Tests for app.build_form_from_saved — the reopen-letter reconstruction.

Change #1 lets the user click a saved grudge to reload it into the worksheet.
build_form_from_saved turns a saved record (a SQLite row dict, or an optimistic
iframe-local entry) back into worksheet form_data so the restored letter has
the right inputs for Regenerate.

Importing `app` is side-effect-free: the module-level `main()` call is guarded
by `if __name__ == "__main__"`, so only the pure helpers run here.
"""

from app import build_form_from_saved


def test_full_db_row_round_trips_all_fields():
    row = {
        "id": 7,
        "debtor_name": "Dana",
        "amount": 50.0,
        "duration": "2 days",        # stored combined; split back out
        "relationship": "ex",
        "rage_level": 4,
        "letter_text": "pay up please",
        "created_at": "2026-05-31 12:00:00",
    }
    form = build_form_from_saved(row)
    assert form["debtor_name"] == "Dana"
    assert form["amount"] == "50"            # whole float -> no ".0"
    assert form["time_owed"] == "2"
    assert form["time_unit"] == "days"
    assert form["relationship"] == "ex"
    # Fields never persisted at save time come back empty.
    assert form["context"] == ""
    assert form["payment_handle"] == ""


def test_fractional_amount_is_preserved():
    form = build_form_from_saved({"amount": 50.5, "duration": "3 weeks"})
    assert form["amount"] == "50.5"
    assert form["time_owed"] == "3"
    assert form["time_unit"] == "weeks"


def test_local_optimistic_entry_falls_back_to_defaults():
    # An optimistic iframe entry has no duration/relationship columns.
    local = {
        "id": "local-1717000000000",
        "debtor_name": "Marcus",
        "amount": 240,
        "rage_level": 2,
        "letter_text": "you know what you did",
    }
    form = build_form_from_saved(local)
    assert form["debtor_name"] == "Marcus"
    assert form["amount"] == "240"
    assert form["time_owed"] == ""           # no duration stored
    assert form["time_unit"] == "weeks"      # safe default
    assert form["relationship"] == "friend"  # safe default


def test_missing_or_garbage_amount_does_not_crash():
    assert build_form_from_saved({})["amount"] == ""
    assert build_form_from_saved({"amount": "abc"})["amount"] == "abc"


def test_duration_with_only_a_number_keeps_default_unit():
    form = build_form_from_saved({"duration": "5"})
    assert form["time_owed"] == "5"
    assert form["time_unit"] == "weeks"
