from datetime import datetime, timezone

from app.models import ApprovalRequest, Property, TaskLog, TaskRun

DEMO_TASK_ID = "task-demo"
DEMO_APPROVAL_ID = "approval-demo"
DEMO_PROPERTY_ID = "prop-b"


def _demo_time(second: int) -> datetime:
    return datetime(2026, 6, 12, 10, 24, second, tzinfo=timezone.utc)


def seed_properties() -> list[Property]:
    return [
        Property(
            id="prop-a",
            name="Property A",
            address="12 Market Street, London",
            status="healthy",
            notes="Executive short-let with upcoming guest arrival.",
        ),
        Property(
            id="prop-b",
            name="Property B",
            address="4 Riverside Walk, Manchester",
            status="attention",
            notes="Power issue reported by current guest. Emergency repair may be needed.",
        ),
        Property(
            id="prop-c",
            name="Property C",
            address="77 Harbour Road, Bristol",
            status="healthy",
            notes="Routine turnover completed.",
        ),
    ]


def seed_demo_task() -> TaskRun:
    task_text = "Power is out at Property B and the electrician quoted 850 pounds for an emergency repair."
    return TaskRun(
        id=DEMO_TASK_ID,
        property_id=DEMO_PROPERTY_ID,
        task=task_text,
        status="waiting_approval",
        agent_name="ComplianceAgent",
        messages=[
            "Orchestrator routed task to maintenance.",
            "Maintenance Agent triaged the incident and prepared an emergency repair recommendation.",
            "Finance Agent reviewed the cost impact. Estimated cost: 850 pounds.",
            "Compliance Agent requires human approval before committing spend.",
        ],
        approval_required=True,
        approval_request=ApprovalRequest(
            id=DEMO_APPROVAL_ID,
            task_id=DEMO_TASK_ID,
            action="approve_maintenance_cost",
            details=task_text,
            cost_estimate=850,
            risk="Owner approval required before high-cost repair can proceed.",
            created_at=_demo_time(18),
        ),
        created_at=_demo_time(12),
        updated_at=_demo_time(18),
    )


def seed_demo_logs() -> list[TaskLog]:
    return [
        TaskLog(
            id="log-demo-orchestrator",
            task_id=DEMO_TASK_ID,
            property_id=DEMO_PROPERTY_ID,
            node="orchestrator",
            agent_name="OrchestratorManager",
            status="running",
            message="Routed power outage task to Maintenance.",
            created_at=_demo_time(12),
        ),
        TaskLog(
            id="log-demo-maintenance",
            task_id=DEMO_TASK_ID,
            property_id=DEMO_PROPERTY_ID,
            node="maintenance",
            agent_name="MaintenanceAgent",
            status="running",
            message="Triaged outage and prepared emergency repair recommendation.",
            created_at=_demo_time(13),
        ),
        TaskLog(
            id="log-demo-finance",
            task_id=DEMO_TASK_ID,
            property_id=DEMO_PROPERTY_ID,
            node="finance",
            agent_name="FinanceAgent",
            status="running",
            message="Validated repair quote. Estimated cost: 850 pounds.",
            created_at=_demo_time(15),
        ),
        TaskLog(
            id="log-demo-compliance",
            task_id=DEMO_TASK_ID,
            property_id=DEMO_PROPERTY_ID,
            node="compliance",
            agent_name="ComplianceAgent",
            status="running",
            message="High-cost repair requires owner approval.",
            created_at=_demo_time(17),
        ),
        TaskLog(
            id="log-demo-human-review",
            task_id=DEMO_TASK_ID,
            property_id=DEMO_PROPERTY_ID,
            node="human_review",
            agent_name="Owner",
            status="waiting_approval",
            message="Workflow paused for owner approval.",
            created_at=_demo_time(18),
        ),
    ]
