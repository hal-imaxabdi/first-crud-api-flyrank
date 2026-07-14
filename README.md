# Task API (CRUD)

A small CRUD API for managing an in-memory to-do list, built with FastAPI.
Built for the Backend AI Engineering internship assignment W2·A1.

## Install & run

pip install fastapi uvicorn
uvicorn main:app --reload --port 8000

The server starts at `http://localhost:8000`.

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

## Example: curl -i output

curl.exe --% -i -X PUT http://localhost:8000/tasks/1 -H "Content-Type: application/json" -d "{\"done\":true}"

HTTP/1.1 200 OK
date: Tue, 14 Jul 2026 03:29:44 GMT
server: uvicorn
content-length: 44
content-type: application/json
{"id":1,"title":"Buy groceries","done":true}

## Swagger UI

Interactive docs at `http://localhost:8000/docs`. Screenshot below shows a
successful `POST /tasks` via "Try it out":

![Swagger screenshot](swagger-screenshot.png)

## Notes on in-memory storage

Data lives only in a Python list, so restarting the server resets it back to
the 3 example tasks. I saw this happen firsthand: a task I created got wiped
out the moment `--reload` restarted the server after a code change. This is
expected — a real database is what Week 3 introduces to solve exactly this.