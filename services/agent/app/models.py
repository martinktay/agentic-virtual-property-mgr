from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field

TaskStatus = Literal["queued", "running", "waiting_approval", "approved", "rejected", "completed", "failed"]
PropertyStatus = Literal["healthy", "attention", "approval_required"]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:12]}"


class Property(BaseModel):
    id: str
    name: str
    address: str
    status: PropertyStatus = "healthy"
    notes: str


class ApprovalRequest(BaseModel):
    id: str
    task_id: str
    action: str
    details: str
    cost_estimate: int | None = None
    risk: str
    decision: Literal["pending", "approved", "rejected"] = "pending"
    created_at: datetime = Field(default_factory=utc_now)


class TaskLog(BaseModel):
    id: str = Field(default_factory=lambda: new_id("log"))
    task_id: str
    property_id: str
    node: str
    agent_name: str
    status: TaskStatus
    message: str
    created_at: datetime = Field(default_factory=utc_now)


class TaskRun(BaseModel):
    id: str
    property_id: str
    task: str
    status: TaskStatus = "queued"
    agent_name: str = "Orchestrator"
    messages: list[str] = Field(default_factory=list)
    approval_required: bool = False
    approval_request: ApprovalRequest | None = None
    final_summary: str | None = None
    error: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class TaskDetail(BaseModel):
    task: TaskRun
    logs: list[TaskLog]

