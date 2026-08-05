"""
database.py
------------
Handles everything related to talking to Postgres:
- opening a connection using DATABASE_URL from .env
- creating the `tasks` table if it doesn't exist
- seeding 3 example tasks the very first time the app runs

This is the ONLY file that should ever contain SQL. main.py should never
know that Postgres exists -- it just calls functions like get_all_tasks().

(Previously this file used sqlite3 / tasks.db -- see git history for W3.A1.
main.py and every route were NOT changed to make this swap.)
"""

import os

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]


def get_connection():
    """
    Open a connection to Postgres.

    cursor_factory=RealDictCursor lets us access columns by name
    (row["title"]) instead of by numeric index, and returns plain dicts --
    the exact same shape the API returned when tasks lived in SQLite / an
    in-memory list.
    """
    return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)


def init_db():
    """
    Create the tasks table if it doesn't exist yet, and insert the 3 example
    tasks ONLY if the table is currently empty. Safe to call every time the
    app starts.

    (In this Postgres setup, init.sql already does this once when the
    database container is first created. init_db() stays here too as a
    safety net -- e.g. if you point the app at a fresh Postgres that wasn't
    bootstrapped with init.sql -- and calling it again is a harmless no-op.)
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id    SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            done  BOOLEAN NOT NULL DEFAULT FALSE
        )
        """
    )

    cur.execute("SELECT COUNT(*) AS count FROM tasks")
    count = cur.fetchone()["count"]

    if count == 0:
        cur.executemany(
            "INSERT INTO tasks (title, done) VALUES (%s, %s)",
            [
                ("Buy groceries", False),
                ("Finish assignment", False),
                ("Read a chapter", True),
            ],
        )

    conn.commit()
    cur.close()
    conn.close()


def _row_to_dict(row) -> dict:
    """RealDictCursor already returns dict-like rows, but we normalize to a
    plain dict with the exact same shape the API has always returned."""
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


def get_all_tasks() -> list[dict]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_task_by_id(task_id: int) -> dict | None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return _row_to_dict(row) if row else None


def insert_task(title: str) -> dict:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id",
        (title, False),
    )
    new_id = cur.fetchone()["id"]
    conn.commit()
    cur.close()
    conn.close()
    return get_task_by_id(new_id)


def update_task(task_id: int, title: str | None, done: bool | None) -> dict | None:
    existing = get_task_by_id(task_id)
    if existing is None:
        return None

    new_title = title if title is not None else existing["title"]
    new_done = done if done is not None else existing["done"]

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE tasks SET title = %s, done = %s WHERE id = %s",
        (new_title, new_done, task_id),
    )
    conn.commit()
    cur.close()
    conn.close()
    return get_task_by_id(task_id)


def delete_task(task_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    deleted = cur.rowcount > 0
    conn.commit()
    cur.close()
    conn.close()
    return deleted
