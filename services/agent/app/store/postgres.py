from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qs, urlparse

from app.models import ApprovalRequest, Property, TaskLog, TaskRun, utc_now


POSTGRES_SCHEMA = """
CREATE TABLE IF NOT EXISTS properties (
    id text PRIMARY KEY,
    payload json NOT NULL
);
CREATE TABLE IF NOT EXISTS tasks (
    id text PRIMARY KEY,
    created_at timestamptz NOT NULL,
    payload json NOT NULL
);
CREATE TABLE IF NOT EXISTS logs (
    id text PRIMARY KEY,
    task_id text NOT NULL,
    created_at timestamptz NOT NULL,
    payload json NOT NULL
);
CREATE TABLE IF NOT EXISTS approvals (
    task_id text PRIMARY KEY,
    payload json NOT NULL
);
"""


@dataclass(frozen=True)
class PostgresConfig:
    host: str
    database: str = "postgres"
    user: str = "admin"
    password: str | None = None
    port: int = 5432
    ssl_context: bool = True


class PostgresRepository:
    def __init__(self, config: PostgresConfig):
        self.config = config

    @classmethod
    def from_env(cls) -> "PostgresRepository":
        database_url = os.getenv("DATABASE_URL") or os.getenv("AURORA_DSQL_DATABASE_URL")
        if database_url:
            return cls(_config_from_url(database_url))

        host = os.environ["AURORA_DSQL_ENDPOINT"]
        region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")
        user = os.getenv("AURORA_DSQL_USER", "admin")
        database = os.getenv("AURORA_DSQL_DATABASE", "postgres")
        password = os.getenv("AURORA_DSQL_AUTH_TOKEN")
        if not password:
            password = _generate_dsql_token(host=host, region=region, user=user)
        return cls(PostgresConfig(host=host, database=database, user=user, password=password))

    def connect(self):
        import pg8000.dbapi

        return pg8000.dbapi.connect(
            host=self.config.host,
            port=self.config.port,
            database=self.config.database,
            user=self.config.user,
            password=self.config.password,
            ssl_context=self.config.ssl_context,
        )

    def initialize(self) -> None:
        with self.connect() as db:
            cursor = db.cursor()
            for statement in _schema_statements():
                cursor.execute(statement)
            db.commit()

    def seed_properties(self, properties: list[Property]) -> None:
        with self.connect() as db:
            cursor = db.cursor()
            for property_item in properties:
                cursor.execute(
                    """
                    INSERT INTO properties (id, payload)
                    VALUES (%s, %s::json)
                    ON CONFLICT (id) DO UPDATE SET payload = EXCLUDED.payload
                    """,
                    (property_item.id, property_item.model_dump_json()),
                )
            db.commit()

    def list_properties(self) -> list[Property]:
        with self.connect() as db:
            cursor = db.cursor()
            cursor.execute("SELECT payload FROM properties ORDER BY id")
            rows = cursor.fetchall()
        return [Property.model_validate(_json_payload(row[0])) for row in rows]

    def save_task(self, task: TaskRun) -> None:
        task.updated_at = utc_now()
        with self.connect() as db:
            cursor = db.cursor()
            cursor.execute(
                """
                INSERT INTO tasks (id, created_at, payload)
                VALUES (%s, %s, %s::json)
                ON CONFLICT (id) DO UPDATE
                SET created_at = EXCLUDED.created_at, payload = EXCLUDED.payload
                """,
                (task.id, task.created_at, task.model_dump_json()),
            )
            db.commit()
        if task.approval_request is not None:
            self.save_approval(task.approval_request)

    def get_task(self, task_id: str) -> TaskRun | None:
        with self.connect() as db:
            cursor = db.cursor()
            cursor.execute("SELECT payload FROM tasks WHERE id = %s", (task_id,))
            row = cursor.fetchone()
        if row is None:
            return None
        task = TaskRun.model_validate(_json_payload(row[0]))
        approval = self._get_approval(task_id)
        if approval is not None:
            task.approval_request = approval
        return task

    def list_tasks(self) -> list[TaskRun]:
        with self.connect() as db:
            cursor = db.cursor()
            cursor.execute("SELECT payload FROM tasks ORDER BY created_at DESC")
            rows = cursor.fetchall()
        return [TaskRun.model_validate(_json_payload(row[0])) for row in rows]

    def add_log(self, log: TaskLog) -> None:
        with self.connect() as db:
            cursor = db.cursor()
            cursor.execute(
                """
                INSERT INTO logs (id, task_id, created_at, payload)
                VALUES (%s, %s, %s, %s::json)
                ON CONFLICT (id) DO UPDATE
                SET task_id = EXCLUDED.task_id, created_at = EXCLUDED.created_at, payload = EXCLUDED.payload
                """,
                (log.id, log.task_id, log.created_at, log.model_dump_json()),
            )
            db.commit()

    def list_logs(self, task_id: str) -> list[TaskLog]:
        with self.connect() as db:
            cursor = db.cursor()
            cursor.execute("SELECT payload FROM logs WHERE task_id = %s ORDER BY created_at", (task_id,))
            rows = cursor.fetchall()
        return [TaskLog.model_validate(_json_payload(row[0])) for row in rows]

    def save_approval(self, approval: ApprovalRequest) -> None:
        with self.connect() as db:
            cursor = db.cursor()
            cursor.execute(
                """
                INSERT INTO approvals (task_id, payload)
                VALUES (%s, %s::json)
                ON CONFLICT (task_id) DO UPDATE SET payload = EXCLUDED.payload
                """,
                (approval.task_id, approval.model_dump_json()),
            )
            db.commit()

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
            cursor = db.cursor()
            cursor.execute("SELECT payload FROM approvals WHERE task_id = %s", (task_id,))
            row = cursor.fetchone()
        if row is None:
            return None
        return ApprovalRequest.model_validate(_json_payload(row[0]))


def _schema_statements() -> list[str]:
    return [statement.strip() for statement in POSTGRES_SCHEMA.split(";") if statement.strip()]


def _json_payload(payload: Any) -> Any:
    if isinstance(payload, str):
        import json

        return json.loads(payload)
    return payload


def _config_from_url(database_url: str) -> PostgresConfig:
    parsed = urlparse(database_url)
    query = parse_qs(parsed.query)
    sslmode = query.get("sslmode", ["require"])[0]
    return PostgresConfig(
        host=parsed.hostname or "",
        database=(parsed.path or "/postgres").lstrip("/") or "postgres",
        user=parsed.username or "admin",
        password=parsed.password,
        port=parsed.port or 5432,
        ssl_context=sslmode != "disable",
    )


def _generate_dsql_token(host: str, region: str | None, user: str) -> str:
    if not region:
        raise RuntimeError("AWS_REGION or AWS_DEFAULT_REGION is required for Aurora DSQL IAM token generation")
    import boto3

    client = boto3.client("dsql", region_name=region)
    if user == "admin":
        return client.generate_db_connect_admin_auth_token(host, region)
    return client.generate_db_connect_auth_token(host, region)

