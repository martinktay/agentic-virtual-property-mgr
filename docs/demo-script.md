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
5. Show the approval panel.
6. Explain that the AI cannot approve high-cost spend by itself.
7. Click Approve.
8. Show the completed status and audit trail.

## Scaling Talking Points

- SQLite is for demo portability.
- The repository interface can move to Postgres or AWS Aurora DSQL.
- Audit logs provide operational traceability.
- LangGraph checkpointing allows interrupted work to resume instead of restarting.
- HITL approval keeps risky decisions under human control.

