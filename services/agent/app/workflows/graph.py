from typing import Literal, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, StateGraph

from app.agents.employees import DemoEmployeeCrew, EmployeeResult
from app.models import ApprovalRequest, TaskLog, TaskRun, new_id
from app.store.repository import Repository


class AgentState(TypedDict, total=False):
    task_id: str
    property_id: str
    task: str
    route: str
    status: str
    agent_name: str
    messages: list[str]
    approval_required: bool
    approval_request: ApprovalRequest | None
    final_summary: str | None
    error: str | None


class AgentWorkflow:
    def __init__(self, repository: Repository, crew: DemoEmployeeCrew | None = None):
        self.repository = repository
        self.crew = crew or DemoEmployeeCrew()
        self.graph = self._build_graph()

    def start_task(self, property_id: str, task: str) -> TaskRun:
        task_run = TaskRun(id=new_id("task"), property_id=property_id, task=task, status="running")
        self.repository.save_task(task_run)
        initial_state: AgentState = {
            "task_id": task_run.id,
            "property_id": property_id,
            "task": task,
            "status": "running",
            "agent_name": task_run.agent_name,
            "messages": [],
            "approval_required": False,
            "approval_request": None,
        }
        config = {"configurable": {"thread_id": task_run.id}}
        self.graph.invoke(initial_state, config=config)
        stored = self.repository.get_task(task_run.id)
        if stored is None:
            raise RuntimeError("workflow did not persist task")
        return stored

    def approve(self, task_id: str) -> TaskRun:
        task_run = self._get_waiting_task(task_id)
        approval = self.repository.decide_approval(task_id, "approved")
        if approval is None:
            raise ValueError("approval request not found")
        task_run.approval_request = approval
        task_run.approval_required = False
        self._log(task_run, "human_review", "Owner", "approved", "Owner approved the requested action.")
        return self._finalize_task(task_run, "Owner approved the repair. Maintenance Agent finalized the repair approval.")

    def reject(self, task_id: str) -> TaskRun:
        task_run = self._get_waiting_task(task_id)
        approval = self.repository.decide_approval(task_id, "rejected")
        if approval is None:
            raise ValueError("approval request not found")
        task_run.approval_request = approval
        task_run.approval_required = False
        task_run.status = "rejected"
        task_run.final_summary = "Owner rejected the repair. No spending commitment was made."
        self._log(task_run, "human_review", "Owner", "rejected", "Owner rejected the requested action.")
        self.repository.save_task(task_run)
        return task_run

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("orchestrator", self._orchestrator_node)
        workflow.add_node("leasing", self._leasing_node)
        workflow.add_node("maintenance", self._maintenance_node)
        workflow.add_node("finance", self._finance_node)
        workflow.add_node("compliance", self._compliance_node)
        workflow.add_node("human_review", self._human_review_node)
        workflow.add_node("finalize", self._finalize_node)
        workflow.set_entry_point("orchestrator")
        workflow.add_conditional_edges(
            "orchestrator",
            self._route_after_orchestrator,
            {"maintenance": "maintenance", "finance": "finance", "leasing": "leasing"},
        )
        workflow.add_edge("maintenance", "finance")
        workflow.add_edge("finance", "compliance")
        workflow.add_conditional_edges(
            "compliance",
            self._route_after_compliance,
            {"human_review": "human_review", "finalize": "finalize"},
        )
        workflow.add_edge("leasing", "finalize")
        workflow.add_edge("human_review", END)
        workflow.add_edge("finalize", END)
        return workflow.compile(checkpointer=InMemorySaver())

    def _orchestrator_node(self, state: AgentState) -> AgentState:
        result = self.crew.orchestrate(state["task"])
        self._apply_result(state["task_id"], "orchestrator", result)
        return {"route": result.route or "leasing"}

    def _leasing_node(self, state: AgentState) -> AgentState:
        result = self.crew.leasing(state["task"])
        self._apply_result(state["task_id"], "leasing", result)
        return {"agent_name": result.agent_name, "messages": [result.message]}

    def _maintenance_node(self, state: AgentState) -> AgentState:
        result = self.crew.maintenance(state["task"])
        self._apply_result(state["task_id"], "maintenance", result)
        return {"agent_name": result.agent_name, "messages": [result.message]}

    def _finance_node(self, state: AgentState) -> AgentState:
        result = self.crew.finance(state["task"])
        self._apply_result(state["task_id"], "finance", result)
        return {
            "agent_name": result.agent_name,
            "messages": [result.message],
            "approval_required": result.approval_required,
        }

    def _compliance_node(self, state: AgentState) -> AgentState:
        result = self.crew.compliance(state["task"], bool(state.get("approval_required")))
        self._apply_result(state["task_id"], "compliance", result)
        return {
            "agent_name": result.agent_name,
            "messages": [result.message],
            "approval_required": result.approval_required,
        }

    def _human_review_node(self, state: AgentState) -> AgentState:
        task_run = self._require_task(state["task_id"])
        cost_estimate = task_run.approval_request.cost_estimate if task_run.approval_request else None
        approval = ApprovalRequest(
            id=new_id("approval"),
            task_id=task_run.id,
            action="approve_maintenance_cost",
            details=task_run.task,
            cost_estimate=cost_estimate,
            risk="Owner approval required before high-cost repair can proceed.",
        )
        task_run.status = "waiting_approval"
        task_run.approval_required = True
        task_run.approval_request = approval
        self.repository.save_approval(approval)
        self._log(task_run, "human_review", "Owner", "waiting_approval", "Workflow paused for owner approval.")
        self.repository.save_task(task_run)
        return {"status": "waiting_approval", "approval_required": True, "approval_request": approval}

    def _finalize_node(self, state: AgentState) -> AgentState:
        task_run = self._require_task(state["task_id"])
        summary = "Workflow completed without requiring owner approval."
        self._finalize_task(task_run, summary)
        return {"status": "completed", "final_summary": summary, "approval_required": False}

    def _route_after_orchestrator(self, state: AgentState) -> Literal["maintenance", "finance", "leasing"]:
        route = state.get("route", "leasing")
        if route in {"maintenance", "finance", "leasing"}:
            return route  # type: ignore[return-value]
        return "leasing"

    def _route_after_compliance(self, state: AgentState) -> Literal["human_review", "finalize"]:
        return "human_review" if state.get("approval_required") else "finalize"

    def _apply_result(self, task_id: str, node: str, result: EmployeeResult) -> None:
        task_run = self._require_task(task_id)
        task_run.agent_name = result.agent_name
        task_run.messages.append(result.message)
        if result.approval_required:
            existing_cost = task_run.approval_request.cost_estimate if task_run.approval_request else None
            task_run.approval_required = True
            task_run.approval_request = ApprovalRequest(
                id=new_id("approval"),
                task_id=task_run.id,
                action="review_cost",
                details=task_run.task,
                cost_estimate=result.cost_estimate if result.cost_estimate is not None else existing_cost,
                risk=result.risk or "Approval required.",
            )
        self._log(task_run, node, result.agent_name, "running", result.message)
        self.repository.save_task(task_run)

    def _finalize_task(self, task_run: TaskRun, summary: str) -> TaskRun:
        task_run.status = "completed"
        task_run.final_summary = summary
        task_run.approval_required = False
        self._log(task_run, "finalize", task_run.agent_name, "completed", summary)
        self.repository.save_task(task_run)
        return task_run

    def _log(self, task_run: TaskRun, node: str, agent_name: str, status: str, message: str) -> None:
        self.repository.add_log(
            TaskLog(
                task_id=task_run.id,
                property_id=task_run.property_id,
                node=node,
                agent_name=agent_name,
                status=status,  # type: ignore[arg-type]
                message=message,
            )
        )

    def _require_task(self, task_id: str) -> TaskRun:
        task_run = self.repository.get_task(task_id)
        if task_run is None:
            raise KeyError(task_id)
        return task_run

    def _get_waiting_task(self, task_id: str) -> TaskRun:
        task_run = self._require_task(task_id)
        if task_run.status != "waiting_approval":
            raise RuntimeError("task is not waiting for approval")
        return task_run
