from fastapi import FastAPI, HTTPException, Header
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
from supabase_client import supabase

app = FastAPI(
    title="Task API",
    description="A tiny CRUD API for managing a to-do list, backed by Postgres, with Supabase auth.",
    version="3.0",
    openapi_tags=[
        {"name": "General", "description": "Basic info and health checks"},
        {"name": "Tasks", "description": "Create, read, update, and delete tasks"},
        {"name": "Auth", "description": "Sign up, log in, and log out"},
    ],
)


@app.on_event("startup")
def on_startup():
    # Creates the tasks table if it doesn't already exist, and seeds 3
    # example tasks the very first time the app runs.
    init_db()
    print("Server running and connected to Supabase")


class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


class AuthCredentials(BaseModel):
    email: str
    password: str


@app.get("/", tags=["General"], summary="API info")
def read_root():
    return {
        "name": "Task API",
        "version": "3.0",
        "endpoints": ["/tasks", "/auth/signup", "/auth/login", "/public/info", "/protected/profile"],
    }


@app.get("/health", tags=["General"], summary="Health check")
def health_check():
    return {"status": "ok"}


# ---------- Auth ----------

@app.post("/auth/signup", status_code=201, tags=["Auth"], summary="Create a new user account")
def signup(credentials: AuthCredentials):
    if not credentials.email.strip() or not credentials.password.strip():
        raise HTTPException(status_code=400, detail="Email and password are required")

    try:
        result = supabase.auth.sign_up(
            {"email": credentials.email, "password": credentials.password}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return result.user.model_dump(mode="json")


@app.post("/auth/login", tags=["Auth"], summary="Authenticate user and return JWT")
def login(credentials: AuthCredentials):
    if not credentials.email.strip() or not credentials.password.strip():
        raise HTTPException(status_code=400, detail="Email and password are required")

    try:
        result = supabase.auth.sign_in_with_password(
            {"email": credentials.email, "password": credentials.password}
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid login credentials")

    return {
        "access_token": result.session.access_token,
        "refresh_token": result.session.refresh_token,
        "user": result.user.model_dump(mode="json"),
    }


@app.get("/public/info", tags=["Auth"], summary="Public, unprotected info")
def public_info():
    return {"message": "Welcome stranger! This info is public."}


@app.get("/protected/profile", tags=["Auth"], summary="Get the logged-in user's profile")
def get_profile(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Access token required")

    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(status_code=401, detail="Access token required")

    try:
        result = supabase.auth.get_user(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if result is None or result.user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = result.user
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at,
    }


# ---------- Tasks ----------

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
