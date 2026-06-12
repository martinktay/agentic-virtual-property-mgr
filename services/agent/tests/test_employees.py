from app.agents.employees import DemoEmployeeCrew


def test_orchestrator_routes_power_fix_to_maintenance():
    crew = DemoEmployeeCrew()

    result = crew.orchestrate("Power is out at Property B and needs a fix")

    assert result.agent_name == "OrchestratorManager"
    assert result.route == "maintenance"


def test_finance_flags_high_cost_repair():
    crew = DemoEmployeeCrew()

    result = crew.finance("Electrician quoted 850 pounds for emergency repair")

    assert result.agent_name == "FinanceAgent"
    assert result.approval_required is True
    assert result.cost_estimate == 850


def test_leasing_handles_guest_inquiry():
    crew = DemoEmployeeCrew()

    result = crew.leasing("Guest asks for check-in instructions")

    assert result.agent_name == "LeasingAgent"
    assert "guest" in result.message.lower()

