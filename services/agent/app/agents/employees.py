import re
from dataclasses import dataclass


@dataclass(frozen=True)
class EmployeeResult:
    agent_name: str
    message: str
    route: str | None = None
    approval_required: bool = False
    cost_estimate: int | None = None
    risk: str | None = None


class DemoEmployeeCrew:
    """CrewAI-shaped facade with deterministic outputs for reliable demos."""

    def orchestrate(self, task: str) -> EmployeeResult:
        lowered = task.lower()
        if any(word in lowered for word in ["fix", "repair", "power", "outage", "maintenance"]):
            route = "maintenance"
        elif any(word in lowered for word in ["refund", "cost", "quote", "invoice"]):
            route = "finance"
        else:
            route = "leasing"
        return EmployeeResult(
            agent_name="OrchestratorManager",
            route=route,
            message=f"Orchestrator routed task to {route}.",
        )

    def leasing(self, task: str) -> EmployeeResult:
        return EmployeeResult(
            agent_name="LeasingAgent",
            message="Leasing Agent prepared a guest-safe response and verified the guest context.",
        )

    def maintenance(self, task: str) -> EmployeeResult:
        return EmployeeResult(
            agent_name="MaintenanceAgent",
            message="Maintenance Agent triaged the incident and prepared an emergency repair recommendation.",
        )

    def finance(self, task: str) -> EmployeeResult:
        cost = self._extract_cost(task)
        approval_required = cost is not None and cost >= 500
        return EmployeeResult(
            agent_name="FinanceAgent",
            message=f"Finance Agent reviewed the cost impact. Estimated cost: {cost or 0} pounds.",
            approval_required=approval_required,
            cost_estimate=cost,
            risk="High-cost repair requires owner approval." if approval_required else None,
        )

    def compliance(self, task: str, approval_required: bool) -> EmployeeResult:
        if approval_required:
            return EmployeeResult(
                agent_name="ComplianceAgent",
                message="Compliance Agent requires human approval before committing spend.",
                approval_required=True,
                risk="Owner approval required before high-cost repair can proceed.",
            )
        return EmployeeResult(
            agent_name="ComplianceAgent",
            message="Compliance Agent cleared the action for autonomous completion.",
        )

    def _extract_cost(self, task: str) -> int | None:
        matches = re.findall(r"\b(\d{3,5})\b", task)
        if not matches:
            return None
        return max(int(match) for match in matches)

