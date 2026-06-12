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

- `app/agents/employees.py`: CrewAI-shaped employee facade.
- `app/workflows/graph.py`: LangGraph workflow and HITL approval handling.
- `app/store/sqlite.py`: demo persistence layer.
- `app/main.py`: FastAPI endpoints.

