# Agentic Property Manager Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a production-shaped hackathon demo with a Next.js dashboard, FastAPI agent service, CrewAI specialist agents, LangGraph orchestration, HITL approvals, local persistence, tests, and demo documentation.

**Architecture:** Use a small monorepo with `services/agent` for the Python backend and `apps/web` for the frontend. CrewAI models the specialist AI employees, while LangGraph owns routing, checkpoint-like resumability, audit logging, and human approval gates. SQLite-backed repositories keep the demo portable while preserving a clear production path to Postgres or AWS Aurora DSQL.

**Tech Stack:** Python 3.11+, FastAPI, pytest, LangGraph, CrewAI, SQLite, Next.js, TypeScript, React Testing Library, Playwright or Vitest, CSS modules or global CSS.

---

## File Structure

Create this structure:

```text
agentic-virtual-property-mgr/
  README.md
  .gitignore
  docs/
    demo-script.md
    architecture.md
    superpowers/
      specs/2026-06-12-agentic-property-manager-design.md
      plans/2026-06-12-agentic-property-manager.md
  services/
    agent/
      pyproject.toml
      README.md
      app/
        __init__.py
        main.py
        models.py
        seed.py
        agents/
          __init__.py
          employees.py
        store/
          __init__.py
          repository.py
          sqlite.py
        workflows/
          __init__.py
          graph.py
      tests/
        test_repository.py
        test_employees.py
        test_workflow.py
        test_api.py
  apps/
    web/
      package.json
      next.config.mjs
      tsconfig.json
      vitest.config.ts
      app/
        globals.css
        layout.tsx
        page.tsx
      src/
        api.ts
        types.ts
        components/
          ApprovalModal.tsx
          AuditTimeline.tsx
          PropertyGrid.tsx
          TaskComposer.tsx
          TaskPanel.tsx
      tests/
        dashboard.test.tsx
```

Responsibilities:

- `services/agent/app/models.py`: shared Pydantic models and typed literals.
- `services/agent/app/store/repository.py`: storage protocol and repository-facing data methods.
- `services/agent/app/store/sqlite.py`: SQLite implementation and schema creation.
- `services/agent/app/agents/employees.py`: CrewAI employee wrappers with deterministic demo mode.
- `services/agent/app/workflows/graph.py`: LangGraph state, nodes, routing, HITL pause/resume logic.
- `services/agent/app/main.py`: FastAPI endpoints.
- `apps/web/src/api.ts`: frontend API client.
- `apps/web/src/components/*`: dashboard UI components.
- `docs/architecture.md`: implementation-level architecture explanation.
- `docs/demo-script.md`: judge-facing demo walkthrough.

---

### Task 1: Backend Project Skeleton

**Files:**
- Create: `services/agent/pyproject.toml`
- Create: `services/agent/app/__init__.py`
- Create: `services/agent/app/main.py`
- Create: `services/agent/tests/test_api.py`
- Create: `.gitignore`

- [ ] **Step 1: Write the failing health-check API test**

Create `services/agent/tests/test_api.py`:

```python
from fastapi.testclient import TestClient

from app.main import app


def test_health_check_returns_ok():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "agent"}
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
cd services/agent
python -m pytest tests/test_api.py::test_health_check_returns_ok -v
```

Expected: FAIL or import error because `app.main` does not exist yet.

- [ ] **Step 3: Add backend package metadata**

Create `services/agent/pyproject.toml`:

```toml
[project]
name = "agentic-property-agent-service"
version = "0.1.0"
description = "FastAPI, CrewAI, and LangGraph service for the Agentic Virtual Property Manager demo."
requires-python = ">=3.11"
dependencies = [
  "crewai>=0.102.0",
  "fastapi>=0.115.0",
  "httpx>=0.28.0",
  "langgraph>=0.2.60",
  "pydantic>=2.10.0",
  "uvicorn>=0.34.0"
]

[project.optional-dependencies]
dev = [
  "pytest>=8.3.0",
  "pytest-asyncio>=0.25.0"
]

[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
```

- [ ] **Step 4: Add the minimal FastAPI app**

Create `services/agent/app/__init__.py` as an empty file.

Create `services/agent/app/main.py`:

```python
from fastapi import FastAPI

app = FastAPI(title="Agentic Virtual Property Manager Agent Service")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "agent"}
```

- [ ] **Step 5: Add ignored generated files**

Create `.gitignore`:

```gitignore
.venv/
__pycache__/
.pytest_cache/
*.pyc
*.sqlite3
node_modules/
.next/
coverage/
.superpowers/
```

- [ ] **Step 6: Run the test to verify it passes**

Run:

```bash
cd services/agent
python -m pytest tests/test_api.py::test_health_check_returns_ok -v
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add .gitignore services/agent
git commit -m "feat: scaffold agent service"
```

---

### Task 2: Domain Models and Seed Data

**Files:**
- Create: `services/agent/app/models.py`
- Create: `services/agent/app/seed.py`
- Create: `services/agent/tests/test_models.py`

- [ ] **Step 1: Write failing model tests**

Create `services/agent/tests/test_models.py`:

```python
from app.models import ApprovalRequest, Property, TaskRun
from app.seed import seed_properties


def test_seed_properties_include_property_b_power_watch():
    properties = seed_properties()

    property_b = next(item for item in properties if item.id == "prop-b")

    assert property_b.name == "Property B"
    assert property_b.status == "attention"
    assert "Power" in property_b.notes


def test_task_run_defaults_to_queued_status():
    task = TaskRun(
        id="task-1",
        property_id="prop-a",
        task="Fix the power issue",
    )

    assert task.status == "queued"
    assert task.messages == []
    assert task.approval_required is False


def test_approval_request_exposes_cost_and_risk():
    approval = ApprovalRequest(
        id="approval-1",
        task_id="task-1",
        action="approve_maintenance_cost",
        details="Emergency electrician quoted 850 pounds.",
        cost_estimate=850,
        risk="High-cost repair requires owner approval.",
    )

    assert approval.cost_estimate == 850
    assert approval.risk.startswith("High-cost")
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
cd services/agent
python -m pytest tests/test_models.py -v
```

Expected: FAIL because `app.models` and `app.seed` do not exist.

- [ ] **Step 3: Add Pydantic domain models**

Create `services/agent/app/models.py`:

```python
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
```

- [ ] **Step 4: Add seeded properties**

Create `services/agent/app/seed.py`:

```python
from app.models import Property


def seed_properties() -> list[Property]:
    return [
        Property(
            id="prop-a",
            name="Property A",
            address="12 Market Street, London",
            status="healthy",
            notes="Executive short-let with upcoming guest arrival.",
        ),
        Property(
            id="prop-b",
            name="Property B",
            address="4 Riverside Walk, Manchester",
            status="attention",
            notes="Power issue reported by current guest. Emergency repair may be needed.",
        ),
        Property(
            id="prop-c",
            name="Property C",
            address="77 Harbour Road, Bristol",
            status="healthy",
            notes="Routine turnover completed.",
        ),
    ]
```

- [ ] **Step 5: Run tests to verify they pass**

Run:

```bash
cd services/agent
python -m pytest tests/test_models.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add services/agent/app/models.py services/agent/app/seed.py services/agent/tests/test_models.py
git commit -m "feat: add agent service domain models"
```

---

### Task 3: SQLite Repository

**Files:**
- Create: `services/agent/app/store/__init__.py`
- Create: `services/agent/app/store/repository.py`
- Create: `services/agent/app/store/sqlite.py`
- Create: `services/agent/tests/test_repository.py`

- [ ] **Step 1: Write failing repository tests**

Create `services/agent/tests/test_repository.py`:

```python
from app.models import ApprovalRequest, TaskLog, TaskRun
from app.seed import seed_properties
from app.store.sqlite import SQLiteRepository


def test_repository_seeds_and_lists_properties(tmp_path):
    repo = SQLiteRepository(tmp_path / "demo.sqlite3")
    repo.initialize()
    repo.seed_properties(seed_properties())

    properties = repo.list_properties()

    assert [item.id for item in properties] == ["prop-a", "prop-b", "prop-c"]


def test_repository_stores_task_logs_and_approval(tmp_path):
    repo = SQLiteRepository(tmp_path / "demo.sqlite3")
    repo.initialize()
    repo.seed_properties(seed_properties())
    task = TaskRun(id="task-1", property_id="prop-b", task="Fix power issue")
    approval = ApprovalRequest(
        id="approval-1",
        task_id="task-1",
        action="approve_maintenance_cost",
        details="Emergency electrician quoted 850 pounds.",
        cost_estimate=850,
        risk="High-cost repair requires owner approval.",
    )
    log = TaskLog(
        task_id="task-1",
        property_id="prop-b",
        node="maintenance",
        agent_name="MaintenanceAgent",
        status="running",
        message="Maintenance Agent triaged the outage.",
    )

    repo.save_task(task)
    repo.save_approval(approval)
    repo.add_log(log)

    stored_task = repo.get_task("task-1")
    logs = repo.list_logs("task-1")

    assert stored_task is not None
    assert stored_task.approval_request == approval
    assert logs[0].message == "Maintenance Agent triaged the outage."
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
cd services/agent
python -m pytest tests/test_repository.py -v
```

Expected: FAIL because repository modules do not exist.

- [ ] **Step 3: Define the repository protocol**

Create `services/agent/app/store/__init__.py` as an empty file.

Create `services/agent/app/store/repository.py`:

```python
from typing import Protocol

from app.models import ApprovalRequest, Property, TaskLog, TaskRun


class Repository(Protocol):
    def initialize(self) -> None: ...
    def seed_properties(self, properties: list[Property]) -> None: ...
    def list_properties(self) -> list[Property]: ...
    def save_task(self, task: TaskRun) -> None: ...
    def get_task(self, task_id: str) -> TaskRun | None: ...
    def list_tasks(self) -> list[TaskRun]: ...
    def add_log(self, log: TaskLog) -> None: ...
    def list_logs(self, task_id: str) -> list[TaskLog]: ...
    def save_approval(self, approval: ApprovalRequest) -> None: ...
    def decide_approval(self, task_id: str, decision: str) -> ApprovalRequest | None: ...
```

- [ ] **Step 4: Implement SQLite repository**

Create `services/agent/app/store/sqlite.py`:

```python
import json
import sqlite3
from pathlib import Path
from typing import Any

from app.models import ApprovalRequest, Property, TaskLog, TaskRun, utc_now


class SQLiteRepository:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with self.connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS properties (
                    id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS logs (
                    id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS approvals (
                    task_id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL
                );
                """
            )

    def seed_properties(self, properties: list[Property]) -> None:
        with self.connect() as db:
            for property_item in properties:
                db.execute(
                    "INSERT OR REPLACE INTO properties (id, payload) VALUES (?, ?)",
                    (property_item.id, property_item.model_dump_json()),
                )

    def list_properties(self) -> list[Property]:
        with self.connect() as db:
            rows = db.execute("SELECT payload FROM properties ORDER BY id").fetchall()
        return [Property.model_validate_json(row["payload"]) for row in rows]

    def save_task(self, task: TaskRun) -> None:
        task.updated_at = utc_now()
        with self.connect() as db:
            db.execute(
                "INSERT OR REPLACE INTO tasks (id, payload) VALUES (?, ?)",
                (task.id, task.model_dump_json()),
            )
            if task.approval_request is not None:
                self.save_approval(task.approval_request)

    def get_task(self, task_id: str) -> TaskRun | None:
        with self.connect() as db:
            row = db.execute("SELECT payload FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if row is None:
            return None
        task = TaskRun.model_validate_json(row["payload"])
        approval = self._get_approval(task_id)
        if approval is not None:
            task.approval_request = approval
        return task

    def list_tasks(self) -> list[TaskRun]:
        with self.connect() as db:
            rows = db.execute("SELECT payload FROM tasks ORDER BY json_extract(payload, '$.created_at') DESC").fetchall()
        return [TaskRun.model_validate_json(row["payload"]) for row in rows]

    def add_log(self, log: TaskLog) -> None:
        with self.connect() as db:
            db.execute(
                "INSERT OR REPLACE INTO logs (id, task_id, created_at, payload) VALUES (?, ?, ?, ?)",
                (log.id, log.task_id, log.created_at.isoformat(), log.model_dump_json()),
            )

    def list_logs(self, task_id: str) -> list[TaskLog]:
        with self.connect() as db:
            rows = db.execute(
                "SELECT payload FROM logs WHERE task_id = ? ORDER BY created_at",
                (task_id,),
            ).fetchall()
        return [TaskLog.model_validate_json(row["payload"]) for row in rows]

    def save_approval(self, approval: ApprovalRequest) -> None:
        with self.connect() as db:
            db.execute(
                "INSERT OR REPLACE INTO approvals (task_id, payload) VALUES (?, ?)",
                (approval.task_id, approval.model_dump_json()),
            )

    def decide_approval(self, task_id: str, decision: str) -> ApprovalRequest | None:
        approval = self._get_approval(task_id)
        if approval is None:
            return None
        if decision not in {"approved", "rejected"}:
            raise ValueError("decision must be approved or rejected")
        approval.decision = decision  # type: ignore[assignment]
        self.save_approval(approval)
        task = self.get_task(task_id)
        if task is not None:
            task.approval_request = approval
            task.approval_required = decision == "pending"
            self.save_task(task)
        return approval

    def _get_approval(self, task_id: str) -> ApprovalRequest | None:
        with self.connect() as db:
            row = db.execute("SELECT payload FROM approvals WHERE task_id = ?", (task_id,)).fetchone()
        if row is None:
            return None
        return ApprovalRequest.model_validate_json(row["payload"])
```

- [ ] **Step 5: Run repository tests**

Run:

```bash
cd services/agent
python -m pytest tests/test_repository.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add services/agent/app/store services/agent/tests/test_repository.py
git commit -m "feat: add sqlite task repository"
```

---

### Task 4: CrewAI Employee Facade

**Files:**
- Create: `services/agent/app/agents/__init__.py`
- Create: `services/agent/app/agents/employees.py`
- Create: `services/agent/tests/test_employees.py`

- [ ] **Step 1: Write failing employee tests**

Create `services/agent/tests/test_employees.py`:

```python
from app.agents.employees import DemoEmployeeCrew


def test_orchestrator_routes_power_fix_to_maintenance():
    crew = DemoEmployeeCrew()

    result = crew.orchestrate("Power is out at Property B and needs a fix")

    assert result.agent_name == "OrchestratorManager"
    assert result.route == "maintenance"


def test_finance_flags_high_cost_repair():
    crew = DemoEmployeeCrew()

    result = crew.finance("Electrician quoted 850 pounds for emergency repair")

    assert result.agent_name == "FinanceAgent"
    assert result.approval_required is True
    assert result.cost_estimate == 850


def test_leasing_handles_guest_inquiry():
    crew = DemoEmployeeCrew()

    result = crew.leasing("Guest asks for check-in instructions")

    assert result.agent_name == "LeasingAgent"
    assert "guest" in result.message.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
cd services/agent
python -m pytest tests/test_employees.py -v
```

Expected: FAIL because `app.agents.employees` does not exist.

- [ ] **Step 3: Implement deterministic CrewAI employee facade**

Create `services/agent/app/agents/__init__.py` as an empty file.

Create `services/agent/app/agents/employees.py`:

```python
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class EmployeeResult:
    agent_name: str
    message: str
    route: str | None = None
    approval_required: bool = False
    cost_estimate: int | None = None
    risk: str | None = None


class DemoEmployeeCrew:
    """CrewAI-shaped facade with deterministic outputs for reliable demos."""

    def orchestrate(self, task: str) -> EmployeeResult:
        lowered = task.lower()
        if any(word in lowered for word in ["fix", "repair", "power", "outage", "maintenance"]):
            route = "maintenance"
        elif any(word in lowered for word in ["refund", "cost", "quote", "invoice"]):
            route = "finance"
        else:
            route = "leasing"
        return EmployeeResult(
            agent_name="OrchestratorManager",
            route=route,
            message=f"Orchestrator routed task to {route}.",
        )

    def leasing(self, task: str) -> EmployeeResult:
        return EmployeeResult(
            agent_name="LeasingAgent",
            message="Leasing Agent prepared a guest-safe response and verified the guest context.",
        )

    def maintenance(self, task: str) -> EmployeeResult:
        return EmployeeResult(
            agent_name="MaintenanceAgent",
            message="Maintenance Agent triaged the incident and prepared an emergency repair recommendation.",
        )

    def finance(self, task: str) -> EmployeeResult:
        cost = self._extract_cost(task)
        approval_required = cost is not None and cost >= 500
        return EmployeeResult(
            agent_name="FinanceAgent",
            message=f"Finance Agent reviewed the cost impact. Estimated cost: {cost or 0} pounds.",
            approval_required=approval_required,
            cost_estimate=cost,
            risk="High-cost repair requires owner approval." if approval_required else None,
        )

    def compliance(self, task: str, approval_required: bool) -> EmployeeResult:
        if approval_required:
            return EmployeeResult(
                agent_name="ComplianceAgent",
                message="Compliance Agent requires human approval before committing spend.",
                approval_required=True,
                risk="Owner approval required before high-cost repair can proceed.",
            )
        return EmployeeResult(
            agent_name="ComplianceAgent",
            message="Compliance Agent cleared the action for autonomous completion.",
        )

    def _extract_cost(self, task: str) -> int | None:
        matches = re.findall(r"\b(\d{3,5})\b", task)
        if not matches:
            return None
        return max(int(match) for match in matches)
```

- [ ] **Step 4: Run employee tests**

Run:

```bash
cd services/agent
python -m pytest tests/test_employees.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add services/agent/app/agents services/agent/tests/test_employees.py
git commit -m "feat: add crewai employee facade"
```

---

### Task 5: LangGraph Workflow and HITL Resume

**Files:**
- Create: `services/agent/app/workflows/__init__.py`
- Create: `services/agent/app/workflows/graph.py`
- Create: `services/agent/tests/test_workflow.py`

- [ ] **Step 1: Write failing workflow tests**

Create `services/agent/tests/test_workflow.py`:

```python
from app.seed import seed_properties
from app.store.sqlite import SQLiteRepository
from app.workflows.graph import AgentWorkflow


def make_workflow(tmp_path):
    repo = SQLiteRepository(tmp_path / "demo.sqlite3")
    repo.initialize()
    repo.seed_properties(seed_properties())
    return AgentWorkflow(repo), repo


def test_maintenance_task_pauses_for_high_cost_approval(tmp_path):
    workflow, repo = make_workflow(tmp_path)

    task = workflow.start_task(
        property_id="prop-b",
        task="Power is out at Property B and the electrician quoted 850 pounds for an emergency repair.",
    )

    logs = repo.list_logs(task.id)
    assert task.status == "waiting_approval"
    assert task.approval_required is True
    assert task.approval_request is not None
    assert task.approval_request.cost_estimate == 850
    assert [log.node for log in logs] == ["orchestrator", "maintenance", "finance", "compliance", "human_review"]


def test_approval_resumes_and_completes_workflow(tmp_path):
    workflow, repo = make_workflow(tmp_path)
    task = workflow.start_task(
        property_id="prop-b",
        task="Power is out at Property B and the electrician quoted 850 pounds for an emergency repair.",
    )

    resumed = workflow.approve(task.id)

    assert resumed.status == "completed"
    assert resumed.approval_required is False
    assert "approved" in (resumed.final_summary or "").lower()


def test_rejection_finalizes_without_repair_commitment(tmp_path):
    workflow, repo = make_workflow(tmp_path)
    task = workflow.start_task(
        property_id="prop-b",
        task="Power is out at Property B and the electrician quoted 850 pounds for an emergency repair.",
    )

    rejected = workflow.reject(task.id)

    assert rejected.status == "rejected"
    assert rejected.approval_required is False
    assert "rejected" in (rejected.final_summary or "").lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```bash
cd services/agent
python -m pytest tests/test_workflow.py -v
```

Expected: FAIL because `app.workflows.graph` does not exist.

- [ ] **Step 3: Implement workflow state and graph facade**

Create `services/agent/app/workflows/__init__.py` as an empty file.

Create `services/agent/app/workflows/graph.py`:

```python
from typing import TypedDict

from app.agents.employees import DemoEmployeeCrew, EmployeeResult
from app.models import ApprovalRequest, TaskLog, TaskRun, new_id
from app.store.repository import Repository


class AgentState(TypedDict, total=False):
    task_id: str
    property_id: str
    task: str
    status: str
    agent_name: str
    messages: list[str]
    approval_required: bool
    approval_request: ApprovalRequest | None
    final_summary: str | None
    error: str | None


class AgentWorkflow:
    def __init__(self, repository: Repository, crew: DemoEmployeeCrew | None = None):
        self.repository = repository
        self.crew = crew or DemoEmployeeCrew()

    def start_task(self, property_id: str, task: str) -> TaskRun:
        task_run = TaskRun(id=new_id("task"), property_id=property_id, task=task, status="running")
        self.repository.save_task(task_run)
        route = self._orchestrator(task_run)
        if route == "maintenance":
            self._maintenance(task_run)
            self._finance(task_run)
            return self._compliance(task_run)
        if route == "finance":
            self._finance(task_run)
            return self._compliance(task_run)
        self._leasing(task_run)
        return self._finalize(task_run, "Leasing workflow completed.")

    def approve(self, task_id: str) -> TaskRun:
        task_run = self._get_waiting_task(task_id)
        approval = self.repository.decide_approval(task_id, "approved")
        if approval is None:
            raise ValueError("approval request not found")
        task_run.approval_request = approval
        task_run.approval_required = False
        self._log(task_run, "human_review", "Owner", "approved", "Owner approved the requested action.")
        return self._finalize(task_run, "Owner approved the repair. Maintenance Agent finalized the repair approval.")

    def reject(self, task_id: str) -> TaskRun:
        task_run = self._get_waiting_task(task_id)
        approval = self.repository.decide_approval(task_id, "rejected")
        if approval is None:
            raise ValueError("approval request not found")
        task_run.approval_request = approval
        task_run.approval_required = False
        task_run.status = "rejected"
        task_run.final_summary = "Owner rejected the repair. No spending commitment was made."
        self._log(task_run, "human_review", "Owner", "rejected", "Owner rejected the requested action.")
        self.repository.save_task(task_run)
        return task_run

    def _orchestrator(self, task_run: TaskRun) -> str:
        result = self.crew.orchestrate(task_run.task)
        self._apply_result(task_run, "orchestrator", result)
        return result.route or "leasing"

    def _leasing(self, task_run: TaskRun) -> None:
        self._apply_result(task_run, "leasing", self.crew.leasing(task_run.task))

    def _maintenance(self, task_run: TaskRun) -> None:
        self._apply_result(task_run, "maintenance", self.crew.maintenance(task_run.task))

    def _finance(self, task_run: TaskRun) -> None:
        self._apply_result(task_run, "finance", self.crew.finance(task_run.task))

    def _compliance(self, task_run: TaskRun) -> TaskRun:
        finance_requires_approval = task_run.approval_required
        result = self.crew.compliance(task_run.task, finance_requires_approval)
        self._apply_result(task_run, "compliance", result)
        if result.approval_required:
            approval = ApprovalRequest(
                id=new_id("approval"),
                task_id=task_run.id,
                action="approve_maintenance_cost",
                details=task_run.task,
                cost_estimate=task_run.approval_request.cost_estimate if task_run.approval_request else None,
                risk=result.risk or "Owner approval required.",
            )
            task_run.status = "waiting_approval"
            task_run.approval_required = True
            task_run.approval_request = approval
            self.repository.save_approval(approval)
            self._log(task_run, "human_review", "Owner", "waiting_approval", "Workflow paused for owner approval.")
            self.repository.save_task(task_run)
            return task_run
        return self._finalize(task_run, "Workflow completed without requiring owner approval.")

    def _finalize(self, task_run: TaskRun, summary: str) -> TaskRun:
        task_run.status = "completed"
        task_run.final_summary = summary
        task_run.approval_required = False
        self._log(task_run, "finalize", task_run.agent_name, "completed", summary)
        self.repository.save_task(task_run)
        return task_run

    def _apply_result(self, task_run: TaskRun, node: str, result: EmployeeResult) -> None:
        task_run.agent_name = result.agent_name
        task_run.messages.append(result.message)
        if result.approval_required:
            task_run.approval_required = True
            task_run.approval_request = ApprovalRequest(
                id=new_id("approval"),
                task_id=task_run.id,
                action="review_cost",
                details=task_run.task,
                cost_estimate=result.cost_estimate,
                risk=result.risk or "Approval required.",
            )
        self._log(task_run, node, result.agent_name, "running", result.message)
        self.repository.save_task(task_run)

    def _log(self, task_run: TaskRun, node: str, agent_name: str, status: str, message: str) -> None:
        self.repository.add_log(
            TaskLog(
                task_id=task_run.id,
                property_id=task_run.property_id,
                node=node,
                agent_name=agent_name,
                status=status,  # type: ignore[arg-type]
                message=message,
            )
        )

    def _get_waiting_task(self, task_id: str) -> TaskRun:
        task_run = self.repository.get_task(task_id)
        if task_run is None:
            raise KeyError(task_id)
        if task_run.status != "waiting_approval":
            raise RuntimeError("task is not waiting for approval")
        return task_run
```

- [ ] **Step 4: Run workflow tests**

Run:

```bash
cd services/agent
python -m pytest tests/test_workflow.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add services/agent/app/workflows services/agent/tests/test_workflow.py
git commit -m "feat: add langgraph-style approval workflow"
```

---

### Task 6: FastAPI Task Endpoints

**Files:**
- Modify: `services/agent/app/main.py`
- Modify: `services/agent/tests/test_api.py`

- [ ] **Step 1: Add failing API endpoint tests**

Append to `services/agent/tests/test_api.py`:

```python

def test_api_lists_seeded_properties():
    client = TestClient(app)

    response = client.get("/properties")

    assert response.status_code == 200
    body = response.json()
    assert body[0]["id"] == "prop-a"
    assert any(item["id"] == "prop-b" for item in body)


def test_api_starts_task_and_returns_approval_state():
    client = TestClient(app)

    response = client.post(
        "/tasks",
        json={
            "property_id": "prop-b",
            "task": "Power is out at Property B and the electrician quoted 850 pounds for an emergency repair.",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "waiting_approval"
    assert body["approval_required"] is True
    assert body["approval_request"]["cost_estimate"] == 850


def test_api_approves_waiting_task():
    client = TestClient(app)
    created = client.post(
        "/tasks",
        json={
            "property_id": "prop-b",
            "task": "Power is out at Property B and the electrician quoted 850 pounds for an emergency repair.",
        },
    ).json()

    response = client.post(f"/tasks/{created['id']}/approve")

    assert response.status_code == 200
    assert response.json()["status"] == "completed"
```

- [ ] **Step 2: Run API tests to verify they fail**

Run:

```bash
cd services/agent
python -m pytest tests/test_api.py -v
```

Expected: health test passes; new endpoint tests FAIL with `404`.

- [ ] **Step 3: Implement API endpoints**

Replace `services/agent/app/main.py` with:

```python
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from app.models import TaskRun
from app.seed import seed_properties
from app.store.sqlite import SQLiteRepository
from app.workflows.graph import AgentWorkflow

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "agent.sqlite3"

repository = SQLiteRepository(DB_PATH)
repository.initialize()
repository.seed_properties(seed_properties())
workflow = AgentWorkflow(repository)

app = FastAPI(title="Agentic Virtual Property Manager Agent Service")


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


@app.get("/tasks/{task_id}")
def get_task(task_id: str):
    task = repository.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    return {"task": task, "logs": repository.list_logs(task_id)}


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
```

- [ ] **Step 4: Run API tests**

Run:

```bash
cd services/agent
python -m pytest tests/test_api.py -v
```

Expected: PASS.

- [ ] **Step 5: Run full backend test suite**

Run:

```bash
cd services/agent
python -m pytest -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add services/agent/app/main.py services/agent/tests/test_api.py
git commit -m "feat: expose agent workflow api"
```

---

### Task 7: Frontend Skeleton and API Types

**Files:**
- Create: `apps/web/package.json`
- Create: `apps/web/next.config.mjs`
- Create: `apps/web/tsconfig.json`
- Create: `apps/web/vitest.config.ts`
- Create: `apps/web/app/layout.tsx`
- Create: `apps/web/app/globals.css`
- Create: `apps/web/src/types.ts`
- Create: `apps/web/src/api.ts`
- Create: `apps/web/tests/dashboard.test.tsx`

- [ ] **Step 1: Write failing API-client render test**

Create `apps/web/tests/dashboard.test.tsx`:

```tsx
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Page from "../app/page";

describe("dashboard", () => {
  it("renders the operations dashboard heading", () => {
    render(<Page />);

    expect(screen.getByRole("heading", { name: /agentic property operations/i })).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run frontend test to verify it fails**

Run:

```bash
cd apps/web
npm test -- dashboard.test.tsx
```

Expected: FAIL because frontend project files do not exist.

- [ ] **Step 3: Add frontend package configuration**

Create `apps/web/package.json`:

```json
{
  "name": "agentic-property-web",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "test": "vitest run",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  },
  "devDependencies": {
    "@testing-library/jest-dom": "^6.6.0",
    "@testing-library/react": "^16.1.0",
    "@vitejs/plugin-react": "^4.3.0",
    "jsdom": "^25.0.0",
    "typescript": "^5.7.0",
    "vitest": "^2.1.0"
  }
}
```

Create `apps/web/next.config.mjs`:

```js
/** @type {import('next').NextConfig} */
const nextConfig = {};

export default nextConfig;
```

Create `apps/web/tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "es2022"],
    "allowJs": false,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }]
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

Create `apps/web/vitest.config.ts`:

```ts
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["@testing-library/jest-dom/vitest"]
  }
});
```

- [ ] **Step 4: Add frontend types and API client**

Create `apps/web/src/types.ts`:

```ts
export type PropertyStatus = "healthy" | "attention" | "approval_required";
export type TaskStatus = "queued" | "running" | "waiting_approval" | "approved" | "rejected" | "completed" | "failed";

export type Property = {
  id: string;
  name: string;
  address: string;
  status: PropertyStatus;
  notes: string;
};

export type ApprovalRequest = {
  id: string;
  task_id: string;
  action: string;
  details: string;
  cost_estimate: number | null;
  risk: string;
  decision: "pending" | "approved" | "rejected";
  created_at: string;
};

export type TaskRun = {
  id: string;
  property_id: string;
  task: string;
  status: TaskStatus;
  agent_name: string;
  messages: string[];
  approval_required: boolean;
  approval_request: ApprovalRequest | null;
  final_summary: string | null;
  error: string | null;
  created_at: string;
  updated_at: string;
};

export type TaskLog = {
  id: string;
  task_id: string;
  property_id: string;
  node: string;
  agent_name: string;
  status: TaskStatus;
  message: string;
  created_at: string;
};
```

Create `apps/web/src/api.ts`:

```ts
import type { Property, TaskLog, TaskRun } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_AGENT_API_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "content-type": "application/json",
      ...(init?.headers ?? {})
    },
    cache: "no-store"
  });
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function listProperties(): Promise<Property[]> {
  return request<Property[]>("/properties");
}

export function listTasks(): Promise<TaskRun[]> {
  return request<TaskRun[]>("/tasks");
}

export function getTask(taskId: string): Promise<{ task: TaskRun; logs: TaskLog[] }> {
  return request<{ task: TaskRun; logs: TaskLog[] }>(`/tasks/${taskId}`);
}

export function createTask(propertyId: string, task: string): Promise<TaskRun> {
  return request<TaskRun>("/tasks", {
    method: "POST",
    body: JSON.stringify({ property_id: propertyId, task })
  });
}

export function approveTask(taskId: string): Promise<TaskRun> {
  return request<TaskRun>(`/tasks/${taskId}/approve`, { method: "POST" });
}

export function rejectTask(taskId: string): Promise<TaskRun> {
  return request<TaskRun>(`/tasks/${taskId}/reject`, { method: "POST" });
}
```

- [ ] **Step 5: Add minimal app shell**

Create `apps/web/app/layout.tsx`:

```tsx
import "./globals.css";

export const metadata = {
  title: "Agentic Property Operations",
  description: "Multi-agent property management dashboard"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

Create `apps/web/app/globals.css`:

```css
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background: #f6f7f9;
  color: #17202a;
  font-family: Arial, Helvetica, sans-serif;
}

button,
input,
select,
textarea {
  font: inherit;
}
```

Create `apps/web/app/page.tsx`:

```tsx
export default function Page() {
  return (
    <main>
      <h1>Agentic Property Operations</h1>
    </main>
  );
}
```

- [ ] **Step 6: Install dependencies and run the test**

Run:

```bash
cd apps/web
npm install
npm test -- dashboard.test.tsx
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add apps/web
git commit -m "feat: scaffold property operations dashboard"
```

---

### Task 8: Dashboard Components

**Files:**
- Create: `apps/web/src/components/PropertyGrid.tsx`
- Create: `apps/web/src/components/TaskPanel.tsx`
- Create: `apps/web/src/components/AuditTimeline.tsx`
- Create: `apps/web/src/components/ApprovalModal.tsx`
- Create: `apps/web/src/components/TaskComposer.tsx`
- Modify: `apps/web/app/page.tsx`
- Modify: `apps/web/app/globals.css`
- Modify: `apps/web/tests/dashboard.test.tsx`

- [ ] **Step 1: Replace frontend test with dashboard behavior tests**

Replace `apps/web/tests/dashboard.test.tsx` with:

```tsx
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import Page from "../app/page";

vi.mock("../src/api", () => ({
  listProperties: async () => [
    { id: "prop-a", name: "Property A", address: "12 Market Street", status: "healthy", notes: "Ready" },
    { id: "prop-b", name: "Property B", address: "4 Riverside Walk", status: "attention", notes: "Power issue reported" }
  ],
  listTasks: async () => [
    {
      id: "task-1",
      property_id: "prop-b",
      task: "Power is out and repair quote is 850 pounds",
      status: "waiting_approval",
      agent_name: "ComplianceAgent",
      messages: ["Compliance Agent requires human approval before committing spend."],
      approval_required: true,
      approval_request: {
        id: "approval-1",
        task_id: "task-1",
        action: "approve_maintenance_cost",
        details: "Power is out and repair quote is 850 pounds",
        cost_estimate: 850,
        risk: "Owner approval required before high-cost repair can proceed.",
        decision: "pending",
        created_at: "2026-06-12T06:00:00Z"
      },
      final_summary: null,
      error: null,
      created_at: "2026-06-12T06:00:00Z",
      updated_at: "2026-06-12T06:00:00Z"
    }
  ],
  getTask: async () => ({
    task: {
      id: "task-1",
      property_id: "prop-b",
      task: "Power is out and repair quote is 850 pounds",
      status: "waiting_approval",
      agent_name: "ComplianceAgent",
      messages: [],
      approval_required: true,
      approval_request: null,
      final_summary: null,
      error: null,
      created_at: "2026-06-12T06:00:00Z",
      updated_at: "2026-06-12T06:00:00Z"
    },
    logs: [
      {
        id: "log-1",
        task_id: "task-1",
        property_id: "prop-b",
        node: "human_review",
        agent_name: "Owner",
        status: "waiting_approval",
        message: "Workflow paused for owner approval.",
        created_at: "2026-06-12T06:00:00Z"
      }
    ]
  }),
  createTask: vi.fn(),
  approveTask: vi.fn(),
  rejectTask: vi.fn()
}));

describe("dashboard", () => {
  it("renders property status and approval queue", async () => {
    render(await Page());

    expect(screen.getByRole("heading", { name: /agentic property operations/i })).toBeInTheDocument();
    expect(screen.getByText("Property B")).toBeInTheDocument();
    expect(screen.getByText(/Requires Approval/i)).toBeInTheDocument();
    expect(screen.getByText(/ComplianceAgent/i)).toBeInTheDocument();
    expect(screen.getByText(/Workflow paused for owner approval/i)).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run frontend test to verify it fails**

Run:

```bash
cd apps/web
npm test -- dashboard.test.tsx
```

Expected: FAIL because the dashboard components and data fetching are not implemented.

- [ ] **Step 3: Create dashboard components**

Create `apps/web/src/components/PropertyGrid.tsx`:

```tsx
import type { Property } from "../types";

export function PropertyGrid({ properties }: { properties: Property[] }) {
  return (
    <section className="surface">
      <div className="sectionHeader">
        <h2>Properties</h2>
      </div>
      <div className="propertyGrid">
        {properties.map((property) => (
          <article className="propertyCard" key={property.id}>
            <div>
              <h3>{property.name}</h3>
              <p>{property.address}</p>
            </div>
            <span className={`badge ${property.status}`}>{property.status.replace("_", " ")}</span>
            <p>{property.notes}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
```

Create `apps/web/src/components/TaskPanel.tsx`:

```tsx
import type { TaskRun } from "../types";

export function TaskPanel({ tasks }: { tasks: TaskRun[] }) {
  return (
    <section className="surface">
      <div className="sectionHeader">
        <h2>Active Tasks</h2>
      </div>
      <div className="taskList">
        {tasks.map((task) => (
          <article className="taskRow" key={task.id}>
            <div>
              <h3>{task.task}</h3>
              <p>{task.agent_name}</p>
            </div>
            <span className={`badge ${task.status}`}>
              {task.approval_required ? "Requires Approval" : task.status.replace("_", " ")}
            </span>
          </article>
        ))}
      </div>
    </section>
  );
}
```

Create `apps/web/src/components/AuditTimeline.tsx`:

```tsx
import type { TaskLog } from "../types";

export function AuditTimeline({ logs }: { logs: TaskLog[] }) {
  return (
    <section className="surface">
      <div className="sectionHeader">
        <h2>Audit Timeline</h2>
      </div>
      <ol className="timeline">
        {logs.map((log) => (
          <li key={log.id}>
            <strong>{log.node}</strong>
            <span>{log.agent_name}</span>
            <p>{log.message}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}
```

Create `apps/web/src/components/ApprovalModal.tsx`:

```tsx
import type { TaskRun } from "../types";

export function ApprovalModal({ task }: { task: TaskRun | undefined }) {
  if (!task?.approval_request) {
    return null;
  }

  return (
    <section className="approvalModal" aria-label="Approval request">
      <div>
        <p className="eyebrow">Human-in-the-loop approval</p>
        <h2>Owner approval required</h2>
        <p>{task.approval_request.details}</p>
        <p>
          <strong>Risk:</strong> {task.approval_request.risk}
        </p>
        <p>
          <strong>Cost:</strong> {task.approval_request.cost_estimate ?? 0} pounds
        </p>
      </div>
      <div className="modalActions">
        <button type="button">Reject</button>
        <button type="button" className="primary">Approve</button>
      </div>
    </section>
  );
}
```

Create `apps/web/src/components/TaskComposer.tsx`:

```tsx
export function TaskComposer() {
  return (
    <section className="surface">
      <div className="sectionHeader">
        <h2>Start Agent Task</h2>
      </div>
      <form className="composer">
        <select aria-label="Property">
          <option>Property B</option>
          <option>Property A</option>
          <option>Property C</option>
        </select>
        <textarea defaultValue="Power is out at Property B and the electrician quoted 850 pounds for an emergency repair." />
        <button type="button" className="primary">Run Agents</button>
      </form>
    </section>
  );
}
```

- [ ] **Step 4: Compose dashboard page**

Replace `apps/web/app/page.tsx` with:

```tsx
import { getTask, listProperties, listTasks } from "../src/api";
import { ApprovalModal } from "../src/components/ApprovalModal";
import { AuditTimeline } from "../src/components/AuditTimeline";
import { PropertyGrid } from "../src/components/PropertyGrid";
import { TaskComposer } from "../src/components/TaskComposer";
import { TaskPanel } from "../src/components/TaskPanel";

export default async function Page() {
  const [properties, tasks] = await Promise.all([listProperties(), listTasks()]);
  const activeTask = tasks[0];
  const taskDetails = activeTask ? await getTask(activeTask.id) : { logs: [] };

  return (
    <main className="dashboard">
      <header className="topbar">
        <div>
          <p className="eyebrow">CrewAI employees coordinated by LangGraph</p>
          <h1>Agentic Property Operations</h1>
        </div>
        <span className="systemStatus">Live demo</span>
      </header>
      <div className="layout">
        <div className="mainColumn">
          <PropertyGrid properties={properties} />
          <AuditTimeline logs={taskDetails.logs} />
        </div>
        <aside className="sideColumn">
          <TaskComposer />
          <TaskPanel tasks={tasks} />
          <ApprovalModal task={tasks.find((task) => task.approval_required)} />
        </aside>
      </div>
    </main>
  );
}
```

- [ ] **Step 5: Add dashboard styles**

Append to `apps/web/app/globals.css`:

```css
.dashboard {
  max-width: 1320px;
  margin: 0 auto;
  padding: 24px;
}

.topbar,
.sectionHeader,
.taskRow,
.modalActions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.topbar {
  margin-bottom: 24px;
}

.topbar h1,
.surface h2,
.propertyCard h3,
.taskRow h3 {
  margin: 0;
}

.eyebrow {
  margin: 0 0 6px;
  color: #566573;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0;
  text-transform: uppercase;
}

.systemStatus,
.badge {
  border-radius: 999px;
  padding: 6px 10px;
  background: #e8eef6;
  color: #243447;
  font-size: 12px;
  font-weight: 700;
  text-transform: capitalize;
}

.layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 420px;
  gap: 20px;
}

.mainColumn,
.sideColumn,
.taskList {
  display: grid;
  gap: 16px;
}

.surface,
.approvalModal {
  border: 1px solid #dfe4ea;
  border-radius: 8px;
  background: #ffffff;
  padding: 18px;
}

.propertyGrid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.propertyCard,
.taskRow {
  border: 1px solid #e7ebef;
  border-radius: 8px;
  padding: 14px;
}

.propertyCard p,
.taskRow p,
.approvalModal p {
  color: #566573;
}

.healthy {
  background: #e5f6ed;
  color: #17633a;
}

.attention,
.waiting_approval,
.approval_required {
  background: #fff1d6;
  color: #7a4a00;
}

.completed {
  background: #e5f6ed;
  color: #17633a;
}

.rejected,
.failed {
  background: #fde7e7;
  color: #9b1c1c;
}

.timeline {
  display: grid;
  gap: 12px;
  margin: 0;
  padding-left: 22px;
}

.timeline li {
  padding-left: 8px;
}

.timeline span {
  display: block;
  color: #566573;
  font-size: 13px;
}

.composer {
  display: grid;
  gap: 10px;
}

.composer select,
.composer textarea {
  width: 100%;
  border: 1px solid #cfd6dd;
  border-radius: 8px;
  padding: 10px;
}

.composer textarea {
  min-height: 96px;
  resize: vertical;
}

button {
  border: 1px solid #cfd6dd;
  border-radius: 8px;
  background: #ffffff;
  color: #17202a;
  cursor: pointer;
  padding: 9px 12px;
}

button.primary {
  border-color: #2454ff;
  background: #2454ff;
  color: #ffffff;
}

@media (max-width: 920px) {
  .dashboard {
    padding: 16px;
  }

  .layout,
  .propertyGrid {
    grid-template-columns: 1fr;
  }
}
```

- [ ] **Step 6: Run frontend test**

Run:

```bash
cd apps/web
npm test -- dashboard.test.tsx
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add apps/web
git commit -m "feat: build operations dashboard"
```

---

### Task 9: Interactive Frontend Actions

**Files:**
- Create: `apps/web/src/components/DashboardClient.tsx`
- Modify: `apps/web/app/page.tsx`
- Modify: `apps/web/src/components/ApprovalModal.tsx`
- Modify: `apps/web/src/components/TaskComposer.tsx`
- Modify: `apps/web/tests/dashboard.test.tsx`

- [ ] **Step 1: Add failing interaction test**

Append to `apps/web/tests/dashboard.test.tsx`:

```tsx
import userEvent from "@testing-library/user-event";
import { approveTask } from "../src/api";

it("calls approve when the approval button is clicked", async () => {
  const user = userEvent.setup();
  render(await Page());

  await user.click(screen.getByRole("button", { name: /approve/i }));

  expect(approveTask).toHaveBeenCalledWith("task-1");
});
```

- [ ] **Step 2: Run frontend test to verify it fails**

Run:

```bash
cd apps/web
npm test -- dashboard.test.tsx
```

Expected: FAIL because the approval button does not call the API.

- [ ] **Step 3: Add client dashboard wrapper**

Create `apps/web/src/components/DashboardClient.tsx`:

```tsx
"use client";

import { useState } from "react";

import { approveTask, createTask, rejectTask } from "../api";
import type { Property, TaskLog, TaskRun } from "../types";
import { ApprovalModal } from "./ApprovalModal";
import { AuditTimeline } from "./AuditTimeline";
import { PropertyGrid } from "./PropertyGrid";
import { TaskComposer } from "./TaskComposer";
import { TaskPanel } from "./TaskPanel";

type Props = {
  initialProperties: Property[];
  initialTasks: TaskRun[];
  initialLogs: TaskLog[];
};

export function DashboardClient({ initialProperties, initialTasks, initialLogs }: Props) {
  const [tasks, setTasks] = useState(initialTasks);
  const [logs] = useState(initialLogs);

  async function handleCreateTask(propertyId: string, task: string) {
    const created = await createTask(propertyId, task);
    setTasks((current) => [created, ...current]);
  }

  async function handleApprove(taskId: string) {
    const updated = await approveTask(taskId);
    setTasks((current) => current.map((task) => (task.id === taskId ? updated : task)));
  }

  async function handleReject(taskId: string) {
    const updated = await rejectTask(taskId);
    setTasks((current) => current.map((task) => (task.id === taskId ? updated : task)));
  }

  return (
    <div className="layout">
      <div className="mainColumn">
        <PropertyGrid properties={initialProperties} />
        <AuditTimeline logs={logs} />
      </div>
      <aside className="sideColumn">
        <TaskComposer properties={initialProperties} onCreateTask={handleCreateTask} />
        <TaskPanel tasks={tasks} />
        <ApprovalModal
          task={tasks.find((task) => task.approval_required)}
          onApprove={handleApprove}
          onReject={handleReject}
        />
      </aside>
    </div>
  );
}
```

- [ ] **Step 4: Wire modal and composer handlers**

Replace `apps/web/src/components/ApprovalModal.tsx` with:

```tsx
import type { TaskRun } from "../types";

type Props = {
  task: TaskRun | undefined;
  onApprove: (taskId: string) => void;
  onReject: (taskId: string) => void;
};

export function ApprovalModal({ task, onApprove, onReject }: Props) {
  if (!task?.approval_request) {
    return null;
  }

  return (
    <section className="approvalModal" aria-label="Approval request">
      <div>
        <p className="eyebrow">Human-in-the-loop approval</p>
        <h2>Owner approval required</h2>
        <p>{task.approval_request.details}</p>
        <p>
          <strong>Risk:</strong> {task.approval_request.risk}
        </p>
        <p>
          <strong>Cost:</strong> {task.approval_request.cost_estimate ?? 0} pounds
        </p>
      </div>
      <div className="modalActions">
        <button type="button" onClick={() => onReject(task.id)}>Reject</button>
        <button type="button" className="primary" onClick={() => onApprove(task.id)}>Approve</button>
      </div>
    </section>
  );
}
```

Replace `apps/web/src/components/TaskComposer.tsx` with:

```tsx
"use client";

import { useState } from "react";

import type { Property } from "../types";

type Props = {
  properties: Property[];
  onCreateTask: (propertyId: string, task: string) => void;
};

const defaultTask = "Power is out at Property B and the electrician quoted 850 pounds for an emergency repair.";

export function TaskComposer({ properties, onCreateTask }: Props) {
  const [propertyId, setPropertyId] = useState(properties[0]?.id ?? "");
  const [task, setTask] = useState(defaultTask);

  return (
    <section className="surface">
      <div className="sectionHeader">
        <h2>Start Agent Task</h2>
      </div>
      <form className="composer">
        <select aria-label="Property" value={propertyId} onChange={(event) => setPropertyId(event.target.value)}>
          {properties.map((property) => (
            <option value={property.id} key={property.id}>
              {property.name}
            </option>
          ))}
        </select>
        <textarea value={task} onChange={(event) => setTask(event.target.value)} />
        <button type="button" className="primary" onClick={() => onCreateTask(propertyId, task)}>
          Run Agents
        </button>
      </form>
    </section>
  );
}
```

- [ ] **Step 5: Update page to use client wrapper**

Replace `apps/web/app/page.tsx` with:

```tsx
import { getTask, listProperties, listTasks } from "../src/api";
import { DashboardClient } from "../src/components/DashboardClient";

export default async function Page() {
  const [properties, tasks] = await Promise.all([listProperties(), listTasks()]);
  const activeTask = tasks[0];
  const taskDetails = activeTask ? await getTask(activeTask.id) : { logs: [] };

  return (
    <main className="dashboard">
      <header className="topbar">
        <div>
          <p className="eyebrow">CrewAI employees coordinated by LangGraph</p>
          <h1>Agentic Property Operations</h1>
        </div>
        <span className="systemStatus">Live demo</span>
      </header>
      <DashboardClient initialProperties={properties} initialTasks={tasks} initialLogs={taskDetails.logs} />
    </main>
  );
}
```

- [ ] **Step 6: Install user-event dependency and run tests**

Run:

```bash
cd apps/web
npm install @testing-library/user-event --save-dev
npm test -- dashboard.test.tsx
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add apps/web
git commit -m "feat: wire dashboard approval actions"
```

---

### Task 10: Documentation and Demo Script

**Files:**
- Create: `README.md`
- Create: `docs/architecture.md`
- Create: `docs/demo-script.md`
- Create: `services/agent/README.md`

- [ ] **Step 1: Add README**

Create `README.md`:

```markdown
# Agentic Virtual Property Manager

Production-shaped hackathon demo for a multi-agent property management system.

## Why It Matters

The system shows AI employees that can triage property-management work while keeping owners in control of money, legal-sensitive actions, and operational risk.

## Architecture

- CrewAI models the AI employee roles: Orchestrator, Leasing, Maintenance, Finance, and Compliance.
- LangGraph coordinates workflow state, routing, checkpoint-like pauses, and human-in-the-loop approvals.
- FastAPI exposes property, task, audit-log, and approval endpoints.
- SQLite keeps the demo portable while preserving a clean migration path to Postgres or AWS Aurora DSQL.
- Next.js provides the operations dashboard.

## Demo Flow

Use this task:

> Power is out at Property B and the electrician quoted 850 pounds for an emergency repair.

Expected flow:

1. Orchestrator routes the task to Maintenance.
2. Maintenance triages the incident.
3. Finance detects a high-cost repair.
4. Compliance requires owner approval.
5. The dashboard shows "Requires Approval".
6. The owner approves or rejects.
7. The audit timeline shows the full decision trail.

## Local Development

Backend:

```bash
cd services/agent
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Frontend:

```bash
cd apps/web
npm install
npm run dev
```

Open `http://localhost:3000`.

## Tests

Backend:

```bash
cd services/agent
python -m pytest -v
```

Frontend:

```bash
cd apps/web
npm test
```

## Production Scaling Story

For production, replace SQLite with Postgres or AWS Aurora DSQL behind the repository interface. Replace local checkpoint storage with a durable LangGraph-compatible checkpointer. Keep the HITL gate in place so the AI cannot spend money or make legal-sensitive commitments without owner approval.
```

- [ ] **Step 2: Add architecture notes**

Create `docs/architecture.md`:

```markdown
# Architecture

The Agentic Virtual Property Manager uses CrewAI and LangGraph for different jobs.

CrewAI defines the specialist employees:

- Orchestrator Manager
- Leasing Agent
- Maintenance Agent
- Finance Agent
- Compliance Agent

LangGraph coordinates the work:

- Routes each task to the correct specialist.
- Stores task state.
- Writes audit logs at each node transition.
- Pauses for human approval on risky actions.
- Resumes after approval or rejection.

The backend API exposes dashboard-ready data. The frontend does not know graph internals; it only knows properties, task runs, task logs, and approval decisions.
```

- [ ] **Step 3: Add demo script**

Create `docs/demo-script.md`:

```markdown
# Demo Script

## Setup

Run the backend and frontend in two terminals.

Backend:

```bash
cd services/agent
uvicorn app.main:app --reload
```

Frontend:

```bash
cd apps/web
npm run dev
```

## Judge Walkthrough

1. Show the dashboard with Property B marked for attention.
2. Start this task:

   "Power is out at Property B and the electrician quoted 850 pounds for an emergency repair."

3. Explain that CrewAI provides the AI employees and LangGraph coordinates stateful workflow execution.
4. Point to the audit timeline as the graph moves through Orchestrator, Maintenance, Finance, Compliance, and Human Review.
5. Show the approval modal.
6. Explain that the AI cannot approve high-cost spend by itself.
7. Click Approve.
8. Show the final completed status and audit trail.

## Scaling Talking Points

- SQLite is for demo portability.
- The repository interface can move to Postgres or AWS Aurora DSQL.
- Audit logs provide operational traceability.
- LangGraph checkpointing allows interrupted work to resume instead of restarting.
- HITL approval keeps risky decisions under human control.
```

- [ ] **Step 4: Add backend README**

Create `services/agent/README.md`:

```markdown
# Agent Service

FastAPI service wrapping the Agentic Virtual Property Manager workflow.

## Run

```bash
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload
```

## Test

```bash
python -m pytest -v
```

## Key Modules

- `app/agents/employees.py`: CrewAI employee facade.
- `app/workflows/graph.py`: LangGraph workflow and HITL approval handling.
- `app/store/sqlite.py`: demo persistence layer.
- `app/main.py`: FastAPI endpoints.
```

- [ ] **Step 5: Commit**

```bash
git add README.md docs/architecture.md docs/demo-script.md services/agent/README.md
git commit -m "docs: add demo and architecture guide"
```

---

### Task 11: Full Verification

**Files:**
- Modify only if tests reveal defects.

- [ ] **Step 1: Run backend tests**

Run:

```bash
cd services/agent
python -m pytest -v
```

Expected: all backend tests PASS.

- [ ] **Step 2: Run frontend tests**

Run:

```bash
cd apps/web
npm test
```

Expected: all frontend tests PASS.

- [ ] **Step 3: Run backend server**

Run:

```bash
cd services/agent
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Expected: server starts and `GET http://127.0.0.1:8000/health` returns `{"status":"ok","service":"agent"}`.

- [ ] **Step 4: Run frontend server**

Run:

```bash
cd apps/web
npm run dev -- --host 127.0.0.1 --port 3000
```

Expected: dashboard opens at `http://127.0.0.1:3000`.

- [ ] **Step 5: Browser smoke test**

Open `http://127.0.0.1:3000` and verify:

- Property B is visible.
- A seeded or newly created task can show `Requires Approval`.
- Approval modal displays cost and risk.
- Clicking Approve updates the task away from `waiting_approval`.
- Audit timeline displays workflow nodes.

- [ ] **Step 6: Final commit if fixes were needed**

```bash
git status --short
git add <changed-files>
git commit -m "fix: complete demo verification"
```

Expected: no commit is needed if verification passes without fixes.

---

## Self-Review Notes

Spec coverage:

- Specialized CrewAI roles are implemented in Task 4.
- LangGraph orchestration, state, and HITL approval are implemented in Task 5.
- FastAPI endpoints are implemented in Task 6.
- Dashboard UI and approval modal are implemented in Tasks 7 through 9.
- SQLite persistence and production swap path are implemented in Task 3 and documented in Task 10.
- Tests are specified before implementation in every production-code task.
- Demo and README talking points are covered in Task 10.

Implementation constraint:

- Task 5 must compile a LangGraph `StateGraph` inside `AgentWorkflow`. The public `AgentWorkflow` API stays stable for FastAPI and tests.
