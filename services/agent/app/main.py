from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.models import TaskDetail, TaskRun
from app.seed import seed_properties
from app.store.sqlite import SQLiteRepository
from app.workflows.graph import AgentWorkflow

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "agent.sqlite3"

repository = SQLiteRepository(DB_PATH)
repository.initialize()
repository.seed_properties(seed_properties())
workflow = AgentWorkflow(repository)

app = FastAPI(title="Agentic Virtual Property Manager Agent Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CreateTaskRequest(BaseModel):
    property_id: str
    task: str


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "agent"}


@app.get("/properties")
def list_properties():
    return repository.list_properties()


@app.get("/tasks")
def list_tasks():
    return repository.list_tasks()


@app.post("/tasks", response_model=TaskRun, status_code=status.HTTP_201_CREATED)
def create_task(request: CreateTaskRequest):
    property_ids = {item.id for item in repository.list_properties()}
    if request.property_id not in property_ids:
        raise HTTPException(status_code=404, detail="property not found")
    return workflow.start_task(property_id=request.property_id, task=request.task)


@app.get("/tasks/{task_id}", response_model=TaskDetail)
def get_task(task_id: str):
    task = repository.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    return TaskDetail(task=task, logs=repository.list_logs(task_id))


@app.post("/tasks/{task_id}/approve", response_model=TaskRun)
def approve_task(task_id: str):
    try:
        return workflow.approve(task_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="task not found") from None
    except RuntimeError:
        raise HTTPException(status_code=409, detail="task is not waiting for approval") from None


@app.post("/tasks/{task_id}/reject", response_model=TaskRun)
def reject_task(task_id: str):
    try:
        return workflow.reject(task_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="task not found") from None
    except RuntimeError:
        raise HTTPException(status_code=409, detail="task is not waiting for approval") from None

