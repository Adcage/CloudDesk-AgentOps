from app.agents.supervisor import INTENT_AGENT_MAP


def test_high_risk_action_should_route_to_account_agent_first():
    assert INTENT_AGENT_MAP["high_risk_action"] == "account_agent"
