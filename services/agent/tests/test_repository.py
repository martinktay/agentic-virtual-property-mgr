from app.models import ApprovalRequest, TaskLog, TaskRun
from app.seed import seed_properties
from app.store.sqlite import SQLiteRepository


def test_repository_seeds_and_lists_properties(tmp_path):
    repo = SQLiteRepository(tmp_path / "demo.sqlite3")
    repo.initialize()
    repo.seed_properties(seed_properties())

    properties = repo.list_properties()

    assert [item.id for item in properties] == ["prop-a", "prop-b", "prop-c"]


def test_repository_stores_task_logs_and_approval(tmp_path):
    repo = SQLiteRepository(tmp_path / "demo.sqlite3")
    repo.initialize()
    repo.seed_properties(seed_properties())
    task = TaskRun(id="task-1", property_id="prop-b", task="Fix power issue")
    approval = ApprovalRequest(
        id="approval-1",
        task_id="task-1",
        action="approve_maintenance_cost",
        details="Emergency electrician quoted 850 pounds.",
        cost_estimate=850,
        risk="High-cost repair requires owner approval.",
    )
    log = TaskLog(
        task_id="task-1",
        property_id="prop-b",
        node="maintenance",
        agent_name="MaintenanceAgent",
        status="running",
        message="Maintenance Agent triaged the outage.",
    )

    repo.save_task(task)
    repo.save_approval(approval)
    repo.add_log(log)

    stored_task = repo.get_task("task-1")
    logs = repo.list_logs("task-1")

    assert stored_task is not None
    assert stored_task.approval_request == approval
    assert logs[0].message == "Maintenance Agent triaged the outage."

