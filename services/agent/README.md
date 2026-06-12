# Agent Service

FastAPI service wrapping the Agentic Virtual Property Manager workflow.

## Run

```bash
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload
```

## Aurora DSQL Environment

Set one of:

```bash
DATABASE_URL="postgresql://admin:<temporary-iam-token>@<cluster-endpoint>:5432/postgres?sslmode=require"
```

or:

```bash
AURORA_DSQL_ENDPOINT="<cluster-endpoint>"
AURORA_DSQL_DATABASE="postgres"
AURORA_DSQL_USER="admin"
AWS_REGION="<cluster-region>"
```

When Aurora variables are absent, the service uses local SQLite.

## Test

```bash
python -m pytest -v
```

## Key Modules

- `app/agents/employees.py`: CrewAI-shaped employee facade.
- `app/workflows/graph.py`: LangGraph workflow and HITL approval handling.
- `app/store/factory.py`: environment-driven repository selection.
- `app/store/postgres.py`: Aurora DSQL/PostgreSQL persistence layer.
- `app/store/sqlite.py`: local fallback persistence layer.
- `app/main.py`: FastAPI endpoints.
