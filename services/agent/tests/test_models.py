from app.models import ApprovalRequest, TaskRun
from app.seed import seed_properties


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

