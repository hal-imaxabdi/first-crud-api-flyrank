from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# our "database" - just a list in memory
tasks = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Finish assignment", "done": False},
    {"id": 3, "title": "Read a chapter", "done": True},
]

# describes the shape of data a client sends when creating a task
class TaskCreate(BaseModel):
    title: str

@app.get("/")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.post("/tasks", status_code=201)
def create_task(new_task: TaskCreate):
    if not new_task.title or not new_task.title.strip():
        raise HTTPException(status_code=400, detail="Title is required and cannot be empty")

    next_id = max((t["id"] for t in tasks), default=0) + 1
    task = {"id": next_id, "title": new_task.title, "done": False}
    tasks.append(task)
    return task