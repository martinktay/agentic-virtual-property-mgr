import os
from pathlib import Path

from app.seed import DEMO_TASK_ID, seed_demo_logs, seed_demo_task, seed_properties
from app.store.repository import Repository
from app.store.sqlite import SQLiteRepository


def _seed_demo_data_enabled() -> bool:
    return os.getenv("SEED_DEMO_DATA", "true").lower() not in {"0", "false", "no"}


def _seed_demo_run(repository: Repository) -> None:
    if repository.get_task(DEMO_TASK_ID) is not None:
        return

    repository.save_task(seed_demo_task())
    for log in seed_demo_logs():
        repository.add_log(log)


def build_repository() -> Repository:
    database_url = os.getenv("DATABASE_URL") or os.getenv("AURORA_DSQL_DATABASE_URL")
    dsql_endpoint = os.getenv("AURORA_DSQL_ENDPOINT")

    if database_url or dsql_endpoint:
        from app.store.postgres import PostgresRepository

        repository = PostgresRepository.from_env()
    else:
        db_path = Path(os.getenv("SQLITE_DB_PATH", Path(__file__).resolve().parents[2] / "data" / "agent.sqlite3"))
        repository = SQLiteRepository(db_path)

    repository.initialize()
    repository.seed_properties(seed_properties())
    if _seed_demo_data_enabled():
        _seed_demo_run(repository)
    return repository
