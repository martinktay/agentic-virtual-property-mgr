from app.store.factory import build_repository
from app.store.postgres import POSTGRES_SCHEMA, _config_from_url
from app.store.sqlite import SQLiteRepository


def test_store_factory_uses_sqlite_without_production_env(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("AURORA_DSQL_DATABASE_URL", raising=False)
    monkeypatch.delenv("AURORA_DSQL_ENDPOINT", raising=False)
    monkeypatch.delenv("SEED_DEMO_DATA", raising=False)
    monkeypatch.setenv("SQLITE_DB_PATH", str(tmp_path / "agent.sqlite3"))

    repository = build_repository()

    assert isinstance(repository, SQLiteRepository)
    assert [item.id for item in repository.list_properties()] == ["prop-a", "prop-b", "prop-c"]
    task = repository.get_task("task-demo")
    assert task is not None
    assert task.status == "waiting_approval"
    assert task.approval_request is not None
    assert task.approval_request.cost_estimate == 850
    assert [log.node for log in repository.list_logs("task-demo")] == [
        "orchestrator",
        "maintenance",
        "finance",
        "compliance",
        "human_review",
    ]


def test_store_factory_can_disable_demo_task_seed(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("AURORA_DSQL_DATABASE_URL", raising=False)
    monkeypatch.delenv("AURORA_DSQL_ENDPOINT", raising=False)
    monkeypatch.setenv("SEED_DEMO_DATA", "false")
    monkeypatch.setenv("SQLITE_DB_PATH", str(tmp_path / "agent.sqlite3"))

    repository = build_repository()

    assert repository.get_task("task-demo") is None
    assert repository.list_tasks() == []


def test_store_factory_uses_postgres_when_database_url_exists(monkeypatch):
    initialized = []
    seeded = []

    class FakePostgresRepository:
        @classmethod
        def from_env(cls):
            return cls()

        def initialize(self):
            initialized.append(True)

        def seed_properties(self, properties):
            seeded.extend(properties)

    monkeypatch.setenv("DATABASE_URL", "postgresql://admin:token@example.dsql.us-east-1.on.aws:5432/postgres?sslmode=require")
    monkeypatch.setenv("SEED_DEMO_DATA", "false")
    monkeypatch.setattr("app.store.postgres.PostgresRepository", FakePostgresRepository)

    repository = build_repository()

    assert isinstance(repository, FakePostgresRepository)
    assert initialized == [True]
    assert [item.id for item in seeded] == ["prop-a", "prop-b", "prop-c"]


def test_postgres_schema_uses_aurora_dsql_supported_types():
    lowered = POSTGRES_SCHEMA.lower()

    assert "jsonb" not in lowered
    assert "serial" not in lowered
    assert "payload json not null" in lowered
    assert "created_at timestamptz not null" in lowered


def test_postgres_config_parses_database_url():
    config = _config_from_url("postgresql://admin:token@example.dsql.us-east-1.on.aws:5432/postgres?sslmode=require")

    assert config.host == "example.dsql.us-east-1.on.aws"
    assert config.database == "postgres"
    assert config.user == "admin"
    assert config.password == "token"
    assert config.port == 5432
    assert config.ssl_context is True
