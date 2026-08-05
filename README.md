# Task API (CRUD + Postgres, Dockerized)

## W3·A3 update: Postgres in Docker

This version (W3·A3) replaces SQLite with Postgres, running in Docker
alongside the app via `docker compose up`.

**Only `database.py` changed.** `main.py` and every route are byte-for-byte
identical to the SQLite version — same function names
(`get_all_tasks()`, `insert_task()`, etc.), same request/response shapes.
That's the point of keeping SQL isolated behind a small set of functions:
swapping the storage engine is a one-file change.

### Run it

```
cp .env.example .env      # only needed once
docker compose up --build
```

App: `http://localhost:8000/docs`. Postgres data lives in a named Docker
volume (`pgdata`), so it survives container restarts.

### Persistence check (how I verified it)

1. Created a task via `POST /tasks`.
2. Ran `docker compose down` (stops both containers).
3. Ran `docker compose up` again (no `--build`, no fresh volume).
4. `GET /tasks` still showed the task I created in step 1 — confirming data
   survives an app + container restart, not just a Python process restart.

---

# Task API (CRUD + SQLite) — original W3·A1 version below

A small CRUD API for managing a to-do list, built with FastAPI.
Originally built for W2·A1 (in-memory storage). This version (W3·A1)
replaces the in-memory list with a real SQLite database, so data now
survives server restarts. The API itself — routes, request bodies,
response shapes, status codes — is unchanged.

## Install & run

```
pip install fastapi uvicorn
uvicorn main:app --reload --port 8000
```

The server starts at `http://localhost:8000`.

On first run, it automatically creates `tasks.db` in the project folder,
creates the `tasks` table, and seeds 3 example tasks. On every later run,
it reuses the existing database and skips seeding.

## Endpoints

| Method | Path            | Description                          |
|--------|-----------------|---------------------------------------|
| GET    | `/`             | Basic info about this API            |
| GET    | `/health`       | Health check                          |
| GET    | `/tasks`        | List all tasks                        |
| GET    | `/tasks/{id}`   | Get a single task by id                |
| POST   | `/tasks`        | Create a new task                     |
| PUT    | `/tasks/{id}`   | Update a task's title and/or done     |
| DELETE | `/tasks/{id}`   | Delete a task by id                   |

## Why SQLite

SQLite needs no separate database server — it's a single file (`tasks.db`)
that Python's built-in `sqlite3` module reads and writes directly. That
makes it the simplest way to add real persistence to a small project like
this one, with zero extra installation or configuration. The same SQL used
here (`CREATE TABLE`, `SELECT`, `INSERT`, `UPDATE`, `DELETE`) carries over
almost unchanged if this project later moves to PostgreSQL or MySQL.

## Where the database lives

`tasks.db` is created in the project root, next to `main.py`. It's listed
in `.gitignore` and is not committed to the repository — each clone
generates its own copy automatically the first time it runs.

## Database layer

All SQL lives in `database.py`. `main.py` never touches SQL directly — it
calls plain functions like `get_all_tasks()`, `insert_task()`, and
`update_task()`, which keeps the API layer and the storage layer cleanly
separated.

## Example SQL query

```sql
SELECT * FROM tasks WHERE done = 1;
```

Run directly against `tasks.db` in a SQLite viewer, this returns only the
completed tasks — and the API's `GET /tasks` reflects the same data
immediately, since both read from the same file.

## Database viewer screenshot

<!-- TODO: open tasks.db in DB Browser for SQLite, take a screenshot, save
     it as db-screenshot.png in this folder, then uncomment the line below -->
<!-- ![DB Browser screenshot](db-screenshot.png) -->

## Example: curl -i output

```
curl.exe --% -i -X PUT http://localhost:8000/tasks/1 -H "Content-Type: application/json" -d "{\"done\":true}"

HTTP/1.1 200 OK
date: Tue, 14 Jul 2026 03:29:44 GMT
server: uvicorn
content-length: 44
content-type: application/json
{"id":1,"title":"Buy groceries","done":true}
```

## Swagger UI

Interactive docs at `http://localhost:8000/docs`. Screenshots below show a
successful `POST /tasks` and `GET /tasks` via "Try it out":

![Swagger screenshot](swagger-screenshot.png)
![GET /tasks screenshot](get-screenshot.png)

## From in-memory to SQLite

In W2·A1, data lived only in a Python list, so restarting the server reset
everything back to the 3 example tasks. In W3·A1, the same list is now a
`tasks` table in `tasks.db`. I verified persistence by creating a task,
killing the running server process, and restarting it — the new task was
still there, and no duplicate seed data was inserted, confirming the
"insert seed data only if empty" check works correctly.
