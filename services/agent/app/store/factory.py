import os
from pathlib import Path

from app.seed import seed_properties
from app.store.repository import Repository
from app.store.sqlite import SQLiteRepository


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
    return repository

