from app.models import ApprovalRequest, TaskRun
from app.seed import seed_demo_logs, seed_demo_task, seed_properties


def test_seed_properties_include_property_b_power_watch():
    properties = seed_properties()

    property_b = next(item for item in properties if item.id == "prop-b")

    assert property_b.name == "Property B"
    assert property_b.status == "attention"
    assert "Power" in property_b.notes


def test_task_run_defaults_to_queued_status():
    task = TaskRun(
        id="task-1",
        property_id="prop-a",
        task="Fix the power issue",
    )

    assert task.status == "queued"
    assert task.messages == []
    assert task.approval_required is False


def test_approval_request_exposes_cost_and_risk():
    approval = ApprovalRequest(
        id="approval-1",
        task_id="task-1",
        action="approve_maintenance_cost",
        details="Emergency electrician quoted 850 pounds.",
        cost_estimate=850,
        risk="High-cost repair requires owner approval.",
    )

    assert approval.cost_estimate == 850
    assert approval.risk.startswith("High-cost")


def test_seed_demo_task_requires_human_review_for_power_repair():
    task = seed_demo_task()

    assert task.id == "task-demo"
    assert task.property_id == "prop-b"
    assert task.status == "waiting_approval"
    assert task.approval_required is True
    assert task.approval_request is not None
    assert task.approval_request.cost_estimate == 850


def test_seed_demo_logs_create_agentic_timeline():
    logs = seed_demo_logs()

    assert [log.id for log in logs] == [
        "log-demo-orchestrator",
        "log-demo-maintenance",
        "log-demo-finance",
        "log-demo-compliance",
        "log-demo-human-review",
    ]
    assert [log.node for log in logs] == [
        "orchestrator",
        "maintenance",
        "finance",
        "compliance",
        "human_review",
    ]
