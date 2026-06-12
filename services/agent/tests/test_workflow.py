from app.seed import seed_properties
from app.store.sqlite import SQLiteRepository
from app.workflows.graph import AgentWorkflow


def make_workflow(tmp_path):
    repo = SQLiteRepository(tmp_path / "demo.sqlite3")
    repo.initialize()
    repo.seed_properties(seed_properties())
    return AgentWorkflow(repo), repo


def test_maintenance_task_pauses_for_high_cost_approval(tmp_path):
    workflow, repo = make_workflow(tmp_path)

    task = workflow.start_task(
        property_id="prop-b",
        task="Power is out at Property B and the electrician quoted 850 pounds for an emergency repair.",
    )

    logs = repo.list_logs(task.id)
    assert task.status == "waiting_approval"
    assert task.approval_required is True
    assert task.approval_request is not None
    assert task.approval_request.cost_estimate == 850
    assert [log.node for log in logs] == ["orchestrator", "maintenance", "finance", "compliance", "human_review"]


def test_approval_resumes_and_completes_workflow(tmp_path):
    workflow, _repo = make_workflow(tmp_path)
    task = workflow.start_task(
        property_id="prop-b",
        task="Power is out at Property B and the electrician quoted 850 pounds for an emergency repair.",
    )

    resumed = workflow.approve(task.id)

    assert resumed.status == "completed"
    assert resumed.approval_required is False
    assert "approved" in (resumed.final_summary or "").lower()


def test_rejection_finalizes_without_repair_commitment(tmp_path):
    workflow, _repo = make_workflow(tmp_path)
    task = workflow.start_task(
        property_id="prop-b",
        task="Power is out at Property B and the electrician quoted 850 pounds for an emergency repair.",
    )

    rejected = workflow.reject(task.id)

    assert rejected.status == "rejected"
    assert rejected.approval_required is False
    assert "rejected" in (rejected.final_summary or "").lower()

