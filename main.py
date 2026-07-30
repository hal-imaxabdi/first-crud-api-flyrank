from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from database import (
    init_db,
    get_all_tasks,
    get_task_by_id,
    insert_task,
    update_task,
    delete_task,
)

app = FastAPI(
    title="Task API",
    description="A tiny CRUD API for managing a to-do list, backed by SQLite.",
    version="2.0",
    openapi_tags=[
        {"name": "General", "description": "Basic info and health checks"},
        {"name": "Tasks", "description": "Create, read, update, and delete tasks"},
    ],
)


@app.on_event("startup")
def on_startup():
    # Creates tasks.db and the tasks table if they don't already exist,
    # and seeds 3 example tasks the very first time the app runs.
    init_db()


class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


@app.get("/", tags=["General"], summary="API info")
def read_root():
    return {
        "name": "Task API",
        "version": "2.0",
        "endpoints": ["/tasks"],
    }


@app.get("/health", tags=["General"], summary="Health check")
def health_check():
    return {"status": "ok"}


@app.get("/tasks", tags=["Tasks"], summary="List all tasks")
def get_tasks():
    return get_all_tasks()


@app.get("/tasks/{task_id}", tags=["Tasks"], summary="Get one task")
def get_task(task_id: int):
    task = get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


@app.post("/tasks", status_code=201, tags=["Tasks"], summary="Create a task")
def create_task(new_task: TaskCreate):
    if not new_task.title or not new_task.title.strip():
        raise HTTPException(status_code=400, detail="Title is required and cannot be empty")
    return insert_task(new_task.title)


@app.put("/tasks/{task_id}", tags=["Tasks"], summary="Update a task")
def put_task(task_id: int, updates: TaskUpdate):
    if updates.title is not None and not updates.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    task = update_task(task_id, updates.title, updates.done)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


@app.delete("/tasks/{task_id}", status_code=204, tags=["Tasks"], summary="Delete a task")
def remove_task(task_id: int):
    deleted = delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return None