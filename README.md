# Agentic Virtual Property Manager

Production-shaped hackathon demo for a multi-agent property management system.

## Why It Matters

The system shows AI employees that can triage property-management work while keeping owners in control of money, legal-sensitive actions, and operational risk.

## Architecture

- CrewAI models the AI employee roles: Orchestrator, Leasing, Maintenance, Finance, and Compliance.
- LangGraph coordinates workflow state, routing, checkpoint-backed execution, and human-in-the-loop approvals.
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
npm run build
```

## Production Scaling Story

For production, replace SQLite with Postgres or AWS Aurora DSQL behind the repository interface. Replace local checkpoint storage with a durable LangGraph-compatible checkpointer. Keep the HITL gate in place so the AI cannot spend money or make legal-sensitive commitments without owner approval.

