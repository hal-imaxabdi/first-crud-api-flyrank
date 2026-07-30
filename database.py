"""
database.py
------------
Handles everything related to talking to SQLite:
- opening a connection to tasks.db
- creating the `tasks` table if it doesn't exist
- seeding 3 example tasks the very first time the app runs

This is the ONLY file that should ever contain SQL. main.py should never
know that SQLite exists — it just calls functions like get_all_tasks().
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "tasks.db"


def get_connection():
    """
    Open a connection to tasks.db.

    row_factory = sqlite3.Row lets us access columns by name (row["title"])
    instead of by numeric index (row[1]), which keeps the rest of the code
    readable.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Create the tasks table if it doesn't exist yet, and insert the 3 example
    tasks ONLY if the table is currently empty. Safe to call every time the
    app starts.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done  BOOLEAN NOT NULL DEFAULT 0
        )
        """
    )

    cur.execute("SELECT COUNT(*) FROM tasks")
    count = cur.fetchone()[0]

    if count == 0:
        cur.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            [
                ("Buy groceries", False),
                ("Finish assignment", False),
                ("Read a chapter", True),
            ],
        )

    conn.commit()
    conn.close()


def _row_to_dict(row: sqlite3.Row) -> dict:
    """Convert a sqlite3.Row into the same plain dict shape the API used to
    return when tasks lived in an in-memory list, so responses look
    identical to Assignment 1."""
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


def get_all_tasks() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tasks ORDER BY id").fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_task_by_id(task_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return _row_to_dict(row) if row else None


def insert_task(title: str) -> dict:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)", (title, False)
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return get_task_by_id(new_id)


def update_task(task_id: int, title: str | None, done: bool | None) -> dict | None:
    existing = get_task_by_id(task_id)
    if existing is None:
        return None

    new_title = title if title is not None else existing["title"]
    new_done = done if done is not None else existing["done"]

    conn = get_connection()
    conn.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (new_title, new_done, task_id),
    )
    conn.commit()
    conn.close()
    return get_task_by_id(task_id)


def delete_task(task_id: int) -> bool:
    conn = get_connection()
    cur = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    return deleted
