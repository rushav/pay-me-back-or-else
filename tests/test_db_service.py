"""Tests for services/db_service — runs against a temp SQLite file only.

The temp_db fixture repoints db_service.DB_PATH at a pytest tmp_path file, so
no test ever touches the real db/history.db.
"""

import sqlite3

import pytest

from services import db_service


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    db_file = tmp_path / "test_history.db"
    monkeypatch.setattr(db_service, "DB_PATH", db_file)
    db_service._init()
    return db_file


def _form(**overrides) -> dict:
    form = {
        "debtor_name": "Marcus",
        "amount": "240",
        "time_owed": "3",
        "time_unit": "weeks",
        "relationship": "friend",
        "rage_level": 3,
    }
    form.update(overrides)
    return form


def test_save_then_get_returns_letter(temp_db):
    db_service.save_letter(_form(), "you owe me money")
    rows = db_service.get_all_letters()
    assert len(rows) == 1
    assert rows[0]["debtor_name"] == "Marcus"


def test_saved_fields_round_trip(temp_db):
    db_service.save_letter(
        _form(debtor_name="Dana", amount="$50", time_owed="2",
              time_unit="days", relationship="ex", rage_level=4),
        "pay up please",
    )
    row = db_service.get_all_letters()[0]
    assert row["debtor_name"] == "Dana"
    assert row["amount"] == 50.0           # "$50" -> stripped -> float
    assert row["duration"] == "2 days"     # time_owed + time_unit
    assert row["relationship"] == "ex"
    assert row["rage_level"] == 4
    assert row["letter_text"] == "pay up please"


def test_delete_removes_entry(temp_db):
    new_id = db_service.save_letter(_form(), "temporary grudge")
    assert len(db_service.get_all_letters()) == 1
    db_service.delete_letter(new_id)
    assert db_service.get_all_letters() == []


def test_get_all_letters_newest_first(temp_db):
    db_service.save_letter(_form(debtor_name="Older"), "first")
    # Backdate the first row so created_at ordering is deterministic.
    conn = sqlite3.connect(temp_db)
    conn.execute("UPDATE letters SET created_at = '2000-01-01 00:00:00'")
    conn.commit()
    conn.close()
    db_service.save_letter(_form(debtor_name="Newer"), "second")

    order = [r["debtor_name"] for r in db_service.get_all_letters()]
    assert order == ["Newer", "Older"]
