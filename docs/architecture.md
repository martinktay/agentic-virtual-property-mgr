# Architecture

The Agentic Virtual Property Manager uses CrewAI and LangGraph for different jobs.

CrewAI defines the specialist employees:

- Orchestrator Manager
- Leasing Agent
- Maintenance Agent
- Finance Agent
- Compliance Agent

LangGraph coordinates the work:

- Routes each task to the correct specialist.
- Stores task state.
- Writes audit logs at each node transition.
- Pauses for human approval on risky actions.
- Resumes after approval or rejection.

The backend API exposes dashboard-ready data. The frontend does not know graph internals; it only knows properties, task runs, task logs, and approval decisions.

## Persistence

The demo uses SQLite for portability. The repository interface keeps persistence behind `services/agent/app/store`, so production can move task runs, approvals, and audit logs to Postgres or AWS Aurora DSQL without changing the API or dashboard contract.

