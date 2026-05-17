"""SQLite persistence for saved letters (the hall of grudges)."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "db" / "history.db"


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _init() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS letters (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                debtor_name  TEXT NOT NULL,
                amount       REAL NOT NULL,
                duration     TEXT NOT NULL,
                relationship TEXT NOT NULL,
                rage_level   INTEGER NOT NULL,
                letter_text  TEXT NOT NULL,
                created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def save_letter(form_data: dict, letter_text: str) -> int:
    duration = f"{form_data.get('time_owed', '')} {form_data.get('time_unit', '')}".strip()
    raw_amount = str(form_data.get("amount", "0")).strip().lstrip("$") or "0"
    amount = float(raw_amount)

    with _connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO letters
                (debtor_name, amount, duration, relationship, rage_level, letter_text)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                form_data.get("debtor_name", ""),
                amount,
                duration,
                form_data.get("relationship", ""),
                int(form_data.get("rage_level", 1)),
                letter_text,
            ),
        )
        conn.commit()
        return int(cur.lastrowid)


def get_all_letters() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM letters ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def delete_letter(letter_id: int) -> None:
    with _connect() as conn:
        conn.execute("DELETE FROM letters WHERE id = ?", (letter_id,))
        conn.commit()


_init()
