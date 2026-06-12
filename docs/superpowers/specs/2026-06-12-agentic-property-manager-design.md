# Agentic Virtual Property Manager Design

Date: 2026-06-12

## Goal

Build a production-shaped hackathon demo for an Agentic Virtual Property Manager that combines CrewAI role-based agents with LangGraph workflow orchestration. The system should impress judges by showing specialized AI employees, stateful workflow checkpoints, human approval before risky actions, and a dashboard that makes the agent work visible.

The demo should be reliable with seeded local data while clearly documenting how the same architecture scales to Postgres or AWS Aurora DSQL.

## Product Scope

The MVP supports property-management tasks such as guest inquiries, maintenance incidents, repair approvals, and owner-facing audit logs.

Core demo flow:

1. A user starts a task from the dashboard, such as "Fix the power issue at Property B" or "Approve a high-cost repair at Property A".
2. The backend creates a LangGraph workflow run with persistent state.
3. The LangGraph orchestrator routes the task to the right CrewAI-powered specialist.
4. CrewAI agents produce role-specific decisions and summaries.
5. LangGraph records each node transition in the task log.
6. If an action requires human approval, LangGraph interrupts the run.
7. The dashboard shows "Requires Human Approval" and opens an approval modal.
8. The owner approves or rejects the action.
9. The workflow resumes from its checkpoint and writes the final status.

Out of scope for the first build:

- Real payment execution.
- Real legal commitments.
- Real contractor dispatch.
- Production authentication.
- Live AWS Aurora DSQL provisioning.

## Architecture

The repository is organized as a small monorepo:

- `apps/web`: Next.js dashboard for property status, agent activity, task logs, and approvals.
- `services/agent`: FastAPI service that exposes task APIs and wraps LangGraph workflows.
- `services/agent/app/agents`: CrewAI agent definitions for the AI employees.
- `services/agent/app/workflows`: LangGraph state, nodes, routing, interrupt handling, and checkpoint configuration.
- `services/agent/app/store`: persistence abstraction for properties, task runs, approvals, and audit logs.
- `docs`: architecture notes, demo script, and scaling story.

CrewAI and LangGraph have distinct jobs:

- CrewAI owns the specialist reasoning layer. Each AI employee has a role, goal, backstory, and task-specific tools.
- LangGraph owns orchestration, state, checkpointing, branching, retries, and human-in-the-loop control.

This split keeps the demo easy to explain: CrewAI is the "team of employees"; LangGraph is the "operations manager" that coordinates them safely.

## AI Employees

The MVP includes these CrewAI-backed roles:

- Orchestrator Manager: classifies tasks and chooses the next workflow route.
- Leasing Agent: handles guest inquiries, booking questions, and guest vetting summaries.
- Maintenance Agent: handles incident triage, outage reports, repair status, and contractor notes.
- Finance Agent: estimates cost impact and flags high-cost actions.
- Compliance Agent: flags actions that need owner approval or legal caution.

In the first demo implementation, agents can use deterministic tools and seeded context so the demo remains stable. The code should be shaped so real LLM calls can be enabled by configuration.

## Workflow Design

LangGraph uses a shared state object containing:

- `task_id`
- `property_id`
- `task`
- `status`
- `agent_name`
- `messages`
- `approval_required`
- `approval_request`
- `final_summary`
- `error`

Main graph nodes:

- `orchestrator`: classifies the task and routes to a specialist.
- `leasing`: invokes the Leasing CrewAI agent.
- `maintenance`: invokes the Maintenance CrewAI agent.
- `finance`: evaluates cost and refund or repair impact.
- `compliance`: decides whether owner approval is required.
- `human_review`: interrupts execution and waits for approval or rejection.
- `finalize`: writes the final summary and status.

Critical actions, such as high-cost repairs, refunds, cancellations, or legal-sensitive messages, must pass through `human_review`.

## Persistence

The demo uses local SQLite persistence through a repository-style interface. This keeps setup simple while supporting a credible production migration path.

Stored records:

- Properties.
- Agent task runs.
- Agent task logs.
- Approval requests.
- Approval decisions.

Every workflow node writes an audit log entry with task ID, property ID, node name, agent name, status, message, and timestamp.

Production scaling path:

- Replace SQLite with Postgres or AWS Aurora DSQL.
- Replace local checkpoint storage with a durable LangGraph-compatible checkpointer.
- Keep the same repository interface so the graph and API do not need major changes.

## API Design

FastAPI endpoints:

- `GET /health`: service health.
- `GET /properties`: list seeded properties and current status.
- `GET /tasks`: list task runs.
- `POST /tasks`: start a new agent workflow task.
- `GET /tasks/{task_id}`: inspect task state, logs, and approval status.
- `POST /tasks/{task_id}/approve`: approve an interrupted task.
- `POST /tasks/{task_id}/reject`: reject an interrupted task.

The API returns dashboard-ready data so the frontend can stay focused on presentation.

## Dashboard Design

The dashboard is the first screen, not a marketing landing page.

Primary surfaces:

- Property overview grid with status badges.
- Active task panel showing current agent, state, and last action.
- Audit log timeline showing node-by-node agent work.
- Human approval queue with prominent "Requires Approval" state.
- Approval modal with task details, cost/risk summary, and approve/reject controls.

The interface should feel like an operations command center: dense, readable, and credible. It should avoid decorative marketing sections.

## Error Handling

The backend should handle:

- Unknown task IDs with `404`.
- Invalid approval decisions with `400`.
- Attempts to approve tasks that are not waiting for approval with `409`.
- Agent or graph failures by writing a failed task state and audit log entry.

The frontend should show failure states inline without blocking the rest of the dashboard.

## Testing

Backend tests should cover:

- Task routing to the expected specialist.
- Maintenance tasks can trigger a human approval interrupt.
- Approval resumes a checkpointed workflow.
- Rejection finalizes the task without executing the risky action.
- Audit logs are written for each workflow transition.

Frontend tests should cover:

- Property and task data render correctly.
- Approval-required tasks show the approval action.
- Approve and reject actions call the correct API endpoints.

## Demo Story

The demo should show a split-screen narrative:

- Left: backend logs or API activity showing LangGraph node transitions and CrewAI agent outputs.
- Right: dashboard updating task state, current AI employee, audit log, and HITL approval modal.

Suggested demo task:

> "Power is out at Property B and the electrician quoted 850 pounds for an emergency repair."

Expected flow:

1. Orchestrator routes to Maintenance.
2. Maintenance summarizes the incident.
3. Finance flags high cost.
4. Compliance requires owner approval.
5. Dashboard shows approval modal.
6. Owner approves.
7. Maintenance finalizes repair approval.
8. Audit log shows the full decision trail.

## README Talking Points

The README should emphasize:

- CrewAI provides specialized AI employees.
- LangGraph provides stateful orchestration, checkpointing, and HITL approvals.
- The system does not allow AI to spend money or make legal-sensitive commitments without owner approval.
- Every node transition is logged for auditability.
- SQLite is used for demo portability and can be swapped for Postgres or AWS Aurora DSQL for production-scale persistence.
- The architecture supports future integrations with property-management systems, contractor APIs, messaging channels, and payment systems.
