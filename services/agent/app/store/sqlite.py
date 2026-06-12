import sqlite3
from pathlib import Path

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
            task.approval_required = False
            self.save_task(task)
        return approval

    def _get_approval(self, task_id: str) -> ApprovalRequest | None:
        with self.connect() as db:
            row = db.execute("SELECT payload FROM approvals WHERE task_id = ?", (task_id,)).fetchone()
        if row is None:
            return None
        return ApprovalRequest.model_validate_json(row["payload"])

