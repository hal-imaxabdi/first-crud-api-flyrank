from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Task API",
    description="A tiny CRUD API for managing an in-memory to-do list.",
    version="1.0"
)

tasks = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Finish assignment", "done": False},
    {"id": 3, "title": "Read a chapter", "done": True},
]

class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

@app.get("/", description="Basic info about this API")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health", description="Health check - confirms the server is alive")
def health_check():
    return {"status": "ok"}

@app.get("/tasks", description="List all tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{task_id}", description="Get a single task by id")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.post("/tasks", status_code=201, description="Create a new task")
def create_task(new_task: TaskCreate):
    if not new_task.title or not new_task.title.strip():
        raise HTTPException(status_code=400, detail="Title is required and cannot be empty")

    next_id = max((t["id"] for t in tasks), default=0) + 1
    task = {"id": next_id, "title": new_task.title, "done": False}
    tasks.append(task)
    return task

@app.put("/tasks/{task_id}", description="Update a task's title and/or done status")
def update_task(task_id: int, updates: TaskUpdate):
    for task in tasks:
        if task["id"] == task_id:
            if updates.title is not None:
                if not updates.title.strip():
                    raise HTTPException(status_code=400, detail="Title cannot be empty")
                task["title"] = updates.title
            if updates.done is not None:
                task["done"] = updates.done
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.delete("/tasks/{task_id}", status_code=204, description="Delete a task by id")
def delete_task(task_id: int):
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(i)
            return
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")