# Agentic Virtual Property Manager

Production-shaped hackathon demo for a multi-agent property management system.

## Why It Matters

The system shows AI employees that can triage property-management work while keeping owners in control of money, legal-sensitive actions, and operational risk.

## Architecture

- CrewAI models the AI employee roles: Orchestrator, Leasing, Maintenance, Finance, and Compliance.
- LangGraph coordinates workflow state, routing, checkpoint-backed execution, and human-in-the-loop approvals.
- FastAPI exposes property, task, audit-log, and approval endpoints.
- AWS Aurora DSQL/PostgreSQL is selected through environment variables, with SQLite retained only for local fallback.
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

## Aurora DSQL Configuration

Do not commit database credentials. In Vercel or your production runtime, set one of these configurations:

Option A, full PostgreSQL URL:

```bash
DATABASE_URL="postgresql://admin:<temporary-iam-token>@<cluster-endpoint>:5432/postgres?sslmode=require"
```

Option B, Aurora DSQL endpoint plus token generation:

```bash
AURORA_DSQL_ENDPOINT="<cluster-endpoint>"
AURORA_DSQL_DATABASE="postgres"
AURORA_DSQL_USER="admin"
AWS_REGION="<cluster-region>"
```

For local testing with a pre-generated token:

```bash
AURORA_DSQL_DATABASE_URL="postgresql://admin:<temporary-iam-token>@<cluster-endpoint>:5432/postgres?sslmode=require"
```

The backend selects Aurora/Postgres whenever `DATABASE_URL`, `AURORA_DSQL_DATABASE_URL`, or `AURORA_DSQL_ENDPOINT` is present. If none are set, it falls back to local SQLite.

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

For production, use Aurora DSQL through the PostgreSQL repository in `services/agent/app/store/postgres.py`. Replace local checkpoint storage with a durable LangGraph-compatible checkpointer. Keep the HITL gate in place so the AI cannot spend money or make legal-sensitive commitments without owner approval.
